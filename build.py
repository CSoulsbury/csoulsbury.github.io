"""Builds the Life History Research site into ./docs (GitHub Pages folder).

Edit the text in content/ (or the sections below), then run:  python3 build.py
"""
import html, re, pathlib, json, sys, shutil

ROOT = pathlib.Path(__file__).parent
CONTACT_EMAIL = "csoulsbury@lincoln.ac.uk"
SCHOOL = "School of Natural Sciences"

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

# Picture behind the title band on each page: (file, alt text, focal point for cropping)
HEROES = {
    "index.html": ("study-species.jpg", "Cranesbill flowers, a male black grouse and a magpie", "50% 35%"),
    "lab.html": ("cloud-forest.jpg", "Cloud forest at dawn, seen from a field station veranda", "50% 40%"),
    "research.html": ("taiga-lakes.jpg", "Autumn lakes and birch-covered hills in Finland", "50% 55%"),
    "publications.html": ("sperm-fluorescence.jpg", "Insect sperm under fluorescence microscopy", "50% 50%"),
    "contact.html": ("katydid.jpg", "A green katydid on a leaf at night", "50% 40%"),
}

def page(fname, title, heading, sub, body):
    nav = "".join(
        f'<a href="{h}"{" aria-current=\"page\"" if h == fname else ""}>{n}</a>' for h, n in NAV)
    img, alt, focus = HEROES[fname]
    home = fname == "index.html"
    return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="Research group of Prof. Carl Soulsbury, {SCHOOL}, University of Lincoln: evolution of life history strategies, sexual selection and wild animal welfare.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,600;1,7..72,400&family=Schibsted+Grotesk:wght@500;600;700&family=IBM+Plex+Mono:wght@500&display=swap">
<link rel="stylesheet" href="style.css">
</head>
<body>
<header class="masthead{' masthead-home' if home else ''}">
  <img class="masthead-img" src="img/{img}" alt="{alt}" style="object-position:{focus}">
  <div class="wrap masthead-inner">
    <div class="topbar">
      <a class="brand" href="index.html">Life History Research</a>
      <nav aria-label="Main">{nav}</nav>
    </div>
    <div class="masthead-text">
      <p class="masthead-eyebrow">Soulsbury Lab · {SCHOOL} · University of Lincoln</p>
      <h1>{heading}</h1>
      {f'<p class="masthead-sub">{sub}</p>' if sub else ''}
    </div>
  </div>
</header>
<main class="wrap">
{body}
</main>
<footer class="site">
  <div class="wrap footer-inner">
    <p><strong>Prof. Carl Soulsbury</strong><br>{SCHOOL}, University of Lincoln<br><span class="sel">{CONTACT_EMAIL}</span></p>
    <p class="footer-links"><a href="https://orcid.org/0000-0001-8808-5210">ORCID</a><a href="https://scholar.google.com/citations?user=4IAXZDEAAAAJ">Google Scholar</a><a href="https://bsky.app/profile/cds-york.bsky.social">Bluesky</a></p>
  </div>
</footer>
</body>
</html>
"""

# ---------------------------------------------------------------- pages
def home():
    items = "\n".join(
        f'<li class="news-item"><time>{html.escape(n["date"])}</time><div class="news-body">{paras(n["text"])}</div></li>'
        for n in news)
    return f"""<section class="intro">
  <p class="lede">Welcome to the research home page of Prof. Carl Soulsbury. My group studies the evolution of life history strategies in animals and plants, with field sites in Britain and abroad, and how we can measure and improve the welfare of wild animals. If you are interested in joining, <a href="contact.html">get in contact</a>.</p>
  <ul class="systems" aria-label="Study systems">
    <li><a href="research.html#vertebrates">Black grouse <em>Lyrurus tetrix</em></a></li>
    <li><a href="research.html#vertebrates">Red fox <em>Vulpes vulpes</em></a></li>
    <li><a href="research.html#insects">Katydids &amp; crickets</a></li>
    <li><a href="research.html#insects">Insect sperm &amp; eggs</a></li>
    <li><a href="research.html#plants">Plant–pollinator interactions</a></li>
    <li><a href="research.html#welfare">Wild animal welfare</a></li>
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
    photo = ""
    if m.get("photo"):
        cap = f'<figcaption>{html.escape(m["caption"])}</figcaption>' if m.get("caption") else ""
        photo = f'<figure class="portrait"><img src="img/{m["photo"]}" alt="{html.escape(m.get("caption") or m["name"])}" loading="lazy">{cap}</figure>'
    return f"""<article class="person{' lead' if lead else ''}{' has-photo' if photo else ''}">{photo}
  <div class="person-body"><h3>{html.escape(m["name"])}</h3>{role}
  {paras(m["text"])}{links}</div>
</article>"""

def lab():
    pi, *current = members["current"]
    former = "\n".join(person(m) for m in members["former"])
    return f"""<section class="lab">
  {person(pi, lead=True)}
  <h2>Current members</h2>
  <div class="people">{''.join(person(m) for m in current)}</div>
  <details class="former">
    <summary>Former lab members <span class="count">{len(members["former"])}</span></summary>
    <div class="people">{former}</div>
  </details>
</section>"""

def research():
    return (ROOT / "content/research.html").read_text()

def publications():
    groups = pub_groups()
    jump = "".join(f'<a href="#y{re.sub(r"[^0-9]", "", y)[:4]}">{y}</a>' for y, _ in groups)
    blocks = []
    for y, papers in groups:
        lis = "\n".join(f"<li>{inline(p)}</li>" for p in papers)
        blocks.append(f'<section class="year" id="y{re.sub(r"[^0-9]", "", y)[:4]}"><h2>{y}</h2><ol>{lis}</ol></section>')
    return f"""<section class="pubs">
  <nav class="years" aria-label="Jump to year">{jump}</nav>
  {''.join(blocks)}
</section>"""

def pub_sub():
    n = sum(len(g[1]) for g in pub_groups())
    return f'{n} papers from the group. Student authors are shown in bold. For citation counts see <a href="https://scholar.google.com/citations?user=4IAXZDEAAAAJ">Google Scholar</a>.'

def contact():
    return f"""<section class="contact">
  <div class="contact-text">
    <p class="lede">I welcome informal enquiries from postdoctoral and postgraduate researchers who would like to join the group and can attract their own funding, for example EU fellowships, international PhD scholarships or visiting positions.</p>
    <p>If your interests align with the group's current research, I'm happy to help develop an application. If you're unsure, just ask: my research interests are broad.</p>
  </div>
  <dl class="card">
    <dt>Email</dt><dd class="sel">{CONTACT_EMAIL}</dd>
    <dt>Address</dt><dd>{SCHOOL}, University of Lincoln, Brayford Pool, Lincoln LN6 7TS, UK</dd>
    <dt>Elsewhere</dt><dd><a href="https://orcid.org/0000-0001-8808-5210">ORCID 0000-0001-8808-5210</a><br><a href="https://scholar.google.com/citations?user=4IAXZDEAAAAJ">Google Scholar</a><br><a href="https://bsky.app/profile/cds-york.bsky.social">Bluesky @cds-york.bsky.social</a></dd>
  </dl>
</section>"""

# file: (tab title, big heading, subheading, body)
PAGES = {
    "index.html": ("Life History Research", lambda: "Life History Research",
                   lambda: "How organisms grow, breed, age and die, and why it differs between them", home),
    "lab.html": ("Lab members · Life History Research", lambda: "Lab members", lambda: "", lab),
    "research.html": ("Research · Life History Research", lambda: "Research",
                      lambda: "Life history evolution, sexual selection and the welfare of wild animals", research),
    "publications.html": ("Publications · Life History Research", lambda: "Publications", pub_sub, publications),
    "contact.html": ("Contact · Life History Research", lambda: "Opportunities and contact", lambda: "", contact),
}

if __name__ == "__main__":
    out = ROOT / "docs"
    out.mkdir(exist_ok=True)
    (out / "style.css").write_text((ROOT / "content/style.css").read_text())
    shutil.copytree(ROOT / "content/img", out / "img", dirs_exist_ok=True)
    for f, (t, h, s, fn) in PAGES.items():
        (out / f).write_text(page(f, t, h(), s(), fn()))
    print("built", out)
