# How this site is updated

The site is generated: edit files in `content/`, run `python3 build.py`, commit, push.
GitHub Pages republishes `docs/` within a couple of minutes.

- `content/publications.txt`: one paper per line, grouped under `## YEAR` headings, newest year first.
  `**Name, X.,**` marks a student author from the group (bold). `*text*` is italics (journals, species).
  Optional `[link](https://doi.org/...)` at the end.
- `content/news.json`: newest item first. `{"date": "Month YYYY", "text": "..."}`, same markdown.
- `content/members.json`: current and former lab members.
- `content/research.html`, `content/style.css`: research page and styling.

## Monthly paper check (run by a scheduled task)

Owner: Prof. Carl D. Soulsbury, University of Lincoln. ORCID 0000-0001-8808-5210.
Google Scholar: https://scholar.google.com/citations?user=4IAXZDEAAAAJ

1. Find papers by Carl Soulsbury published since the newest year in `publications.txt`
   (and any from that year that are missing). Try, in order:
   - Crossref: `https://api.crossref.org/works?query.author=Soulsbury&filter=from-pub-date:YYYY-MM-01&rows=100`
   - Europe PMC: `https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=AUTH:"Soulsbury CD" AND PUB_YEAR:[YYYY TO YYYY]&format=json&pageSize=100`
   - ORCID public API: `https://pub.orcid.org/v3.0/0000-0001-8808-5210/works`
   - Web search as a last resort.
   If a source is rate-limited or blocked, note it and use the others. Never add a paper you could
   not confirm from a real record.
2. Keep only papers where Soulsbury, C.D. (Carl) is an author. Skip preprints when the published
   version exists, corrections, and anything already listed (match on title, ignoring case/punctuation).
3. Add each new paper under the right `## YEAR` heading (create the heading if needed, keep years in
   descending order), in the existing citation style:
   `Authors (Year) Title. *Journal*, volume, article/pages. [link](https://doi.org/DOI)`
   Bold any author who is a student in `members.json` (current or former; not Carl himself).
4. Add one news item at the top of `news.json` dated the current month, written in Carl's
   first-person voice, short and plain, linking each new paper and naming student co-authors.
   One item per run, even if several papers were found.
5. Run `python3 build.py`, check it prints "built", commit with a message listing the papers, push to `main`.
6. If nothing new was found, change nothing and do not commit.
7. Finish with a short plain-English summary for Carl: what was added (titles + journals), or that
   nothing new turned up, plus any source that couldn't be reached.
