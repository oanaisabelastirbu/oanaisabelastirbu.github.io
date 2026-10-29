/* OpenAlex citation figures are refreshed periodically by GitHub Actions.
 * The HTML embeds the verified 2026-10-28 snapshot for offline previews and as a safe fallback. */
(() => {
  'use strict';
  const badges = Array.from(document.querySelectorAll('.pub-citation-badge[data-doi]'));
  if (!badges.length || location.protocol === 'file:') return;
  const safeDate = stamp => {
    const dt = new Date(`${stamp}T00:00:00Z`);
    return Number.isNaN(dt.getTime()) ? null : new Intl.DateTimeFormat('en-GB', {
      day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC'
    }).format(dt);
  };
  async function loadSnapshot() {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 9000);
    try {
      const response = await fetch(`assets/openalex-citations.json?updated=${Date.now()}`, {
        signal: controller.signal, cache: 'no-store'
      });
      if (!response.ok) throw new Error('Citation snapshot could not be loaded');
      const data = await response.json();
      if (data.source !== 'OpenAlex' || data.author_id !== 'A5067304723' ||
          data.orcid !== '0009-0006-0638-6129' || !data.works || !data.profile ||
          badges.some(b => !data.works[b.dataset.doi] ||
             !Number.isInteger(data.works[b.dataset.doi].cited_by_count) ||
             data.works[b.dataset.doi].cited_by_count < 0) ||
          !safeDate(data.updated_at)) {
        throw new Error('Incomplete or invalid citation snapshot; retaining verified values');
      }
      const fields = {
        'oa-profile-citations': data.profile.cited_by_count,
        'oa-h-index': data.profile.h_index,
        'oa-i10-index': data.profile.i10_index,
        'oa-work-count': data.profile.works_count,
      };
      if (Object.values(fields).some(n => !Number.isInteger(n) || n < 0)) throw new Error('Invalid OpenAlex profile metrics');
      badges.forEach(badge => {
        const record = data.works[badge.dataset.doi];
        const number = record.cited_by_count;
        badge.dataset.cites = String(number);
        badge.textContent = `OpenAlex · ${number}`;
        const recordId = String(record.openalex_id || '');
        if (/^W\d+$/.test(recordId)) badge.href = `https://openalex.org/works/${recordId}`;
        const cardTitle = badge.closest('.pub-card')?.querySelector('h3')?.textContent || '';
        badge.setAttribute('aria-label', `${number} OpenAlex citations: ${cardTitle}`);
      });
      Object.entries(fields).forEach(([id, value]) => { document.getElementById(id).textContent = String(value); });
      const time = document.getElementById('oa-updated');
      time.setAttribute('datetime', data.updated_at);
      time.textContent = safeDate(data.updated_at);
    } catch (error) {
      // A failed refresh must never replace known figures with zeros.
      console.info('Displaying last verified OpenAlex citation figures:', error.message);
    } finally { clearTimeout(timer); }
  }
  loadSnapshot();
})();
