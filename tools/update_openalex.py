#!/usr/bin/env python3
"""Refresh citation snapshot without touching user-curated publication metadata.

Uses the official OpenAlex API. A free key is OPTIONAL for this low-volume job;
if supplied, it must come from the GitHub Actions secret OPENALEX_API_KEY.
Never display an API key or put it in client-side code.
"""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
AUTHOR = 'A5067304723'
ORCID = '0009-0006-0638-6129'
SNAPSHOT = ROOT / 'assets' / 'openalex-citations.json'
PAGE = ROOT / 'publications.html'
API = 'https://api.openalex.org'


def request_json(route: str, params: dict[str, str] | None = None) -> dict:
    params = dict(params or {})
    key = os.getenv('OPENALEX_API_KEY', '').strip()
    if key:
        params['api_key'] = key
    url = f'{API}{route}' + (f'?{urlencode(params)}' if params else '')
    # No credentials are logged, even on HTTP error.
    for attempt in range(4):
        try:
            headers = {'User-Agent': 'OanaAcademicWebsite-CitationUpdater/1.0', 'Accept': 'application/json'}
            with urlopen(Request(url, headers=headers), timeout=30) as response:
                return json.load(response)
        except HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == 3:
                raise RuntimeError(f'OpenAlex API error: HTTP {exc.code}') from None
        except (URLError, TimeoutError) as exc:
            if attempt == 3:
                raise RuntimeError('OpenAlex API request failed or timed out') from exc
        time.sleep(2 ** attempt)
    raise RuntimeError('OpenAlex API request failed')


def curated_records() -> list[dict]:
    text = PAGE.read_text(encoding='utf-8')
    block = re.search(r'<script\b[^>]*\bid="publication-data"[^>]*>(.*?)</script>', text, re.S)
    if not block:
        raise RuntimeError('Cannot find DOI whitelist in Publications page')
    records = json.loads(block.group(1))
    if not isinstance(records, list) or not records:
        raise RuntimeError('Empty curated publication list')
    return records


def refresh() -> dict:
    selected = curated_records()
    dois = {str(r.get('doi', '')).strip().lower() for r in selected}
    if len(dois) != len(selected) or any(not d.startswith('10.') for d in dois):
        raise RuntimeError('Each displayed publication must have a unique, valid DOI')
    author = request_json(f'/authors/{AUTHOR}', {'select': 'id,orcid,works_count,cited_by_count,summary_stats'})
    if str(author.get('id', '')).split('/')[-1].upper() != AUTHOR:
        raise RuntimeError('OpenAlex returned an unexpected author')
    if str(author.get('orcid', '')).split('/')[-1] != ORCID:
        raise RuntimeError('OpenAlex author ORCID mismatch')
    works_page = request_json('/works', {
        'filter': f'authorships.author.id:{AUTHOR}',
        'corpus': 'all', 'per_page': '100',
        'select': 'id,doi,cited_by_count'
    })
    # Refuse partial data instead of silently turning an unindexed study into 0 citations.
    if works_page.get('meta', {}).get('count', 10**9) > len(works_page.get('results', [])):
        raise RuntimeError('Author works list is incomplete; cannot safely refresh')
    works = {}
    for w in works_page.get('results', []):
        doi = str(w.get('doi') or '').replace('https://doi.org/', '').strip().lower()
        if doi not in dois:
            continue
        number = w.get('cited_by_count')
        wid = str(w.get('id', '')).split('/')[-1]
        if not isinstance(number, int) or number < 0 or not re.fullmatch(r'W\d+', wid):
            raise RuntimeError(f'OpenAlex returned invalid citation data for {doi}')
        if doi in works:
            raise RuntimeError(f'Multiple work records for DOI {doi}; manual review needed')
        works[doi] = {
            'openalex_id': wid,
            'openalex_url': f'https://openalex.org/works/{wid}',
            'cited_by_count': number,
        }
    if set(works) != dois:
        raise RuntimeError(f'{len(dois - set(works))} curated DOI(s) not found in the author profile; keeping previous snapshot')
    stats = author.get('summary_stats') or {}
    profile = {
        'works_count': author.get('works_count'),
        'cited_by_count': author.get('cited_by_count'),
        'h_index': stats.get('h_index'),
        'i10_index': stats.get('i10_index'),
    }
    if any(not isinstance(v, int) or v < 0 for v in profile.values()):
        raise RuntimeError('Invalid author metrics; keeping previous snapshot')
    return {
        'schema_version': 1,
        'source': 'OpenAlex',
        'author_id': AUTHOR,
        'author_url': f'https://openalex.org/authors/{AUTHOR}',
        'orcid': ORCID,
        'updated_at': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d'),
        'profile': profile,
        'selected_count': len(dois),
        'selected_citations': sum(w['cited_by_count'] for w in works.values()),
        'works': dict(sorted(works.items())),
    }


def main():
    try:
        latest = refresh()
    except Exception as exc:
        print(f'WARNING: {exc}. Last verified citation values retained.', file=sys.stderr)
        return 0
    tmp = SNAPSHOT.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(latest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    tmp.replace(SNAPSHOT)
    print(f'OpenAlex refreshed: {latest["profile"]["cited_by_count"]} profile citations; '
          f'{latest["selected_citations"]} citations across {latest["selected_count"]} selected publications.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
