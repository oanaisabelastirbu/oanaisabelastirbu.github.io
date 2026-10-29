SITE-UL ACADEMIC - ETAPA 1, VERSIUNEA 8 (CITARI OPENALEX)

CE SE AFISEAZA
- 16 publicatii selectate (fara cele eliminate de utilizatoare).
- Pentru fiecare: "Cited by N" conform OpenAlex.
- In sumar: 78 de citari, h-index 5, i10-index 2 din profilul OpenAlex (22 de lucrari indexate), verificate la 28 octombrie 2026.
- Sursa: https://openalex.org/authors/A5067304723
- Valorile sunt bibliometrice OpenAlex, nu Google Scholar; nu cresc imediat in clipa aparitiei unei noi citari.

VIZUALIZARE INAINTE DE PUBLICARE
Dezarhiveaza toate fisierele intr-un folder si deschide publications.html in browser.
Statisticile verificate sunt vizibile si offline, inclusiv daca deschizi fisierul direct prin file://.

ACTUALIZARE AUTOMATA PE GITHUB PAGES
Arhiva include .github/workflows/refresh-openalex-and-deploy.yml.
Dupa ce ai aprobat versiunea, incarca TOATE fisierele pe ramura main, inclusiv folderul ascuns .github si tools.
IMPORTANT: pentru ca programul automat sa publice efectiv cifrele actualizate, intra in:
  repository > Settings > Pages > Build and deployment > Source > GitHub Actions
Aceasta INLOCUIESTE configuratia "Deploy from a branch" folosita pana acum.
Workflow-ul ruleaza o data pe saptamana, luni la 05:37 UTC, precum si la fiecare commit si manual din Actions.
El consulta OpenAlex, verifica toate cele 16 DOI-uri, actualizeaza JSON-ul citatiilor si publica intregul site pe GitHub Pages.
Daca OpenAlex este indisponibil, pastreaza ultimul set de cifre verificat in loc sa afiseze 0 sau alte date incomplete.
Nu este necesara o cheie API pentru aceasta utilizare redusa. Daca obtii una, adaug-o NUMAI in GitHub
  Settings > Secrets and variables > Actions > New repository secret > OPENALEX_API_KEY
Nu lipi NICIODATA cheia in codul HTML, in fisierele publice sau in discutii publice.

IMPORTANT
- Publicarea initiala NU s-a facut automat din aceasta conversatie.
- GitHub poate intarzia sau dezactiva automatizarile in repository-uri publice inactive (60 de zile fara activitate).
- Schimbarile de numerotare/citare sunt facute doar in Publications; Home, About, Research, Contact sunt neschimbate.
