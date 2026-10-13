"""Builds the Life History Research site into ./docs (GitHub Pages folder).

Edit the text in content/ (or the sections below), then run:  python3 build.py
"""
import html, re, pathlib, json, sys

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "docs"
CONTACT_EMAIL = ""  # TODO: add your email address here

def inline(md):
    """Tiny markdown: **bold**, *italic*, [text](url)."""
    t = html.escape(md, quote=False)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\*(.+?)\*", r"<em>\1</em>", t)
    return t

def paras(text):
    return "\n".join(f"<p>{inline(p.strip())}</p>" for p in text.strip().split("\n\n"))

# ---------------------------------------------------------------- content
news = json.loads((ROOT / "content/news.json").read_text())
members = json.loads((ROOT / "content/members.json").read_text())

def pub_groups():
    groups, cur = [], None
    for line in (ROOT / "content/publications.txt").read_text().splitlines():
        line = line.strip()
        if not line or (line.startswith("#") and not line.startswith("## ")):
            continue
        if line.startswith("## "):
            cur = (line[3:], []); groups.append(cur)
        else:
            cur[1].append(line)
    return groups

# ---------------------------------------------------------------- layout
NAV = [("index.html", "Home"), ("lab.html", "Lab members"), ("research.html", "Research"),
       ("publications.html", "Publications"), ("contact.html", "Contact")]

def page(fname, title, body, *, full=True):
    nav = "".join(
        f'<a href="{h}"{" aria-current=\"page\"" if h == fname else ""}>{n}</a>' for h, n in NAV)
    head = f"""<title>{title}</title>
<meta name="description" content="Research group of Prof. Carl Soulsbury, University of Lincoln: evolution of life history strategies in animals and plants.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,600;1,7..72,400&family=Schibsted+Grotesk:wght@500;700;800&family=IBM+Plex+Mono:wght@500&display=swap">
<link rel="stylesheet" href="style.css">"""
    shell = f"""<header class="site">
  <a class="brand" href="index.html"><span class="brand-main">Life History Research</span><span class="brand-sub">Soulsbury Lab · University of Lincoln</span></a>
  <nav>{nav}</nav>
</header>
<main>
{body}
</main>
<footer class="site">
  <p>Prof. Carl Soulsbury · School of Life Sciences, University of Lincoln</p>
  <p><a href="https://orcid.org/0000-0001-8808-5210">ORCID</a> · <a href="https://scholar.google.com/citations?user=4IAXZDEAAAAJ">Google Scholar</a> · <a href="https://bsky.app/profile/cds-york.bsky.social">Bluesky</a></p>
</footer>"""
    if not full:  # artifact preview: the host adds the document skeleton
        return head + "\n" + shell
    return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{head}
</head>
<body>
{shell}
</body>
</html>
"""

# ---------------------------------------------------------------- pages
def home():
    items = "\n".join(
        f'<li><time>{html.escape(n["date"])}</time><div class="news-body">{paras(n["text"])}</div></li>'
        for n in news)
    return f"""<section class="intro">
  <p class="eyebrow">School of Life Sciences · University of Lincoln</p>
  <h1>How organisms grow, breed, age and die, and why it differs between them</h1>
  <p class="lede">Welcome to the research home page of Prof. Carl Soulsbury. My group studies the evolution of life history strategies in animals and plants, with field sites in Britain and abroad. If you are interested in joining, <a href="contact.html">get in contact</a>.</p>
  <ul class="systems">
    <li>Black grouse <em>Lyrurus tetrix</em></li><li>Red fox <em>Vulpes vulpes</em></li>
    <li>Katydids &amp; crickets</li><li>Insect sperm</li><li>Plant–pollinator interactions</li><li>Urban wildlife</li>
  </ul>
</section>
<section class="news" aria-labelledby="news-h">
  <h2 id="news-h">Latest news</h2>
  <ol class="news-list">
{items}
  </ol>
</section>"""

def person(m, lead=False):
    links = ""
    if m.get("links"):
        links = '<p class="links">' + " · ".join(
            f'<a href="{html.escape(u)}">{html.escape(t)}</a>' for t, u in m["links"]) + "</p>"
    role = f'<p class="role">{html.escape(m["role"])}</p>' if m.get("role") else ""
    return f"""<article class="person{' lead' if lead else ''}">
  <h3>{html.escape(m["name"])}</h3>{role}
  {paras(m["text"])}{links}
</article>"""

def lab():
    pi, *current = members["current"]
    former = "\n".join(person(m) for m in members["former"])
    return f"""<section>
  <h1>Lab members</h1>
  {person(pi, lead=True)}
  <h2>Current students</h2>
  <div class="people">{''.join(person(m) for m in current)}</div>
  <details class="former">
    <summary>Former lab members ({len(members["former"])})</summary>
    <div class="people">{former}</div>
  </details>
</section>"""

def research():
    return (ROOT / "content/research.html").read_text()

def publications():
    groups = pub_groups()
    n = sum(len(g[1]) for g in groups)
    jump = "".join(f'<a href="#y{re.sub(r"[^0-9]", "", y)[:4]}">{y}</a>' for y, _ in groups)
    blocks = []
    for y, papers in groups:
        lis = "\n".join(f"<li>{inline(p)}</li>" for p in papers)
        blocks.append(f'<section class="year" id="y{re.sub(r"[^0-9]", "", y)[:4]}"><h2>{y}</h2><ol>{lis}</ol></section>')
    return f"""<section>
  <h1>Publications</h1>
  <p class="lede">{n} papers from the group. Student authors from the group are shown in <strong>bold</strong>. For citation counts see <a href="https://scholar.google.com/citations?user=4IAXZDEAAAAJ">Google Scholar</a>.</p>
  <nav class="years" aria-label="Jump to year">{jump}</nav>
  {''.join(blocks)}
</section>"""

def contact():
    return f"""<section class="contact">
  <h1>Opportunities and contact</h1>
  <p class="lede">I welcome informal enquiries from postdoctoral and postgraduate researchers who would like to join the group and can attract their own funding, for example EU fellowships, international PhD scholarships or visiting positions.</p>
  <p>If your interests align with the group's current research, I'm happy to help develop an application. If you're unsure, just ask: my research interests are broad.</p>
  <dl class="card">
    <dt>Email</dt><dd class="sel">{CONTACT_EMAIL or '<span class="todo">Email address to be added</span>'}</dd>
    <dt>Address</dt><dd>School of Life Sciences, University of Lincoln, Brayford Pool, Lincoln LN6 7TS, UK</dd>
    <dt>Elsewhere</dt><dd><a href="https://orcid.org/0000-0001-8808-5210">ORCID 0000-0001-8808-5210</a><br><a href="https://scholar.google.com/citations?user=4IAXZDEAAAAJ">Google Scholar</a><br><a href="https://bsky.app/profile/cds-york.bsky.social">Bluesky @cds-york.bsky.social</a></dd>
  </dl>
</section>"""

PAGES = {
    "index.html": ("Life History Research", home),
    "lab.html": ("Lab members · Life History Research", lab),
    "research.html": ("Research · Life History Research", research),
    "publications.html": ("Publications · Life History Research", publications),
    "contact.html": ("Contact · Life History Research", contact),
}

if __name__ == "__main__":
    preview = "--preview" in sys.argv
    out = ROOT / ("preview" if preview else "docs")
    out.mkdir(exist_ok=True)
    (out / "style.css").write_text((ROOT / "content/style.css").read_text())
    for f, (t, fn) in PAGES.items():
        (out / f).write_text(page(f, t, fn(), full=not (preview and f == "index.html")))
    print("built", out)
