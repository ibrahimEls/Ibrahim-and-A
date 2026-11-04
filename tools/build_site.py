#!/usr/bin/env python3
"""Build index.html, registry.html and rsvp.html from site-text.tex.

Run from anywhere:  python3 tools/build_site.py
Every visible string comes from the \\commands in site-text.tex; this file
holds only the page structure. The arch ornament is tools/arch.svg.html.
"""
import html, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = os.path.join(ROOT, "site-text.tex")
ARCH = os.path.join(ROOT, "tools", "arch.svg.html")

# ---------------------------------------------------------------- tex parsing
def read_body(path):
    s = open(path, encoding="utf-8").read()
    s = re.sub(r"(?<!\\)%.*", "", s)              # strip comments
    m = re.search(r"\\begin\{document\}(.*)\\end\{document\}", s, re.S)
    if not m:
        sys.exit("site-text.tex: no \\begin{document} ... \\end{document}")
    return m.group(1)

def brace_groups(s, pos, n):
    """Read n {...} groups starting at pos; returns (args, end)."""
    args = []
    for _ in range(n):
        while pos < len(s) and s[pos] in " \t\r\n":
            pos += 1
        if pos >= len(s) or s[pos] != "{":
            raise ValueError("expected '{' at offset %d" % pos)
        depth, start = 0, pos
        while pos < len(s):
            c = s[pos]
            if c == "\\":
                pos += 2; continue
            if c == "{": depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    args.append(s[start + 1:pos]); pos += 1; break
            pos += 1
        else:
            raise ValueError("unbalanced braces after offset %d" % start)
    return args, pos

def collect(body, arity):
    found = {}
    for name, n in arity.items():
        for m in re.finditer(r"\\" + name + r"(?![A-Za-z])", body):
            try:
                args, _ = brace_groups(body, m.end(), n)
            except ValueError as e:
                sys.exit("site-text.tex: \\%s: %s" % (name, e))
            found.setdefault(name, []).append(args)
    return found

ARITY = {
    "sitename": 2, "navlabels": 3, "footerline": 1, "eventdate": 1, "pagemeta": 3,
    "bismillah": 2, "invitationline": 1, "names": 2, "dateline": 4, "place": 1,
    "countdownlabels": 8, "countdowndone": 1, "rsvpbutton": 1, "ayah": 3,
    "sectionhead": 2, "cardwhen": 3, "cardwhere": 6, "cardreply": 4, "giftnote": 3,
    "registryhead": 3, "registrypanel": 5,
    "rsvphead": 4, "rsvpform": 2, "formfields": 5, "formguests": 3, "formexception": 2, "formnote": 3,
    "formmessages": 3, "thankyou": 3, "rsvpfallback": 5,
}

def tex_to_html(s, raw=False):
    """LaTeX escapes -> plain text -> HTML. raw=True keeps a URL untouched except escapes."""
    s = s.strip()
    s = s.replace("\\\\", "\0BR\0")
    for a, b in (("\\&", "&"), ("\\%", "%"), ("\\#", "#"), ("\\_", "_"), ("\\$", "$"),
                 ("``", "\u201c"), ("''", "\u201d"), ("\\ldots", "\u2026"), ("~", "\u00a0")):
        s = s.replace(a, b)
    s = re.sub(r"\\textit\{([^}]*)\}", r"\0I\0\1\0/I\0", s)
    s = html.escape(s, quote=True)
    s = s.replace("\0BR\0", "<br>").replace("\0I\0", "<em>").replace("\0/I\0", "</em>")
    return s

def load():
    body = read_body(TEX)
    found = collect(body, ARITY)
    T = {}
    for name, n in ARITY.items():
        if name == "pagemeta":
            continue
        if name not in found:
            sys.exit("site-text.tex: missing \\%s" % name)
        if len(found[name]) > 1:
            sys.exit("site-text.tex: \\%s appears %d times; it should appear once" % (name, len(found[name])))
        T[name] = [tex_to_html(a) for a in found[name][0]]
    meta = {}
    for key, title, desc in found.get("pagemeta", []):
        meta[key.strip()] = (tex_to_html(title), tex_to_html(desc))
    for k in ("index", "registry", "rsvp"):
        if k not in meta:
            sys.exit("site-text.tex: missing \\pagemeta{%s}{...}{...}" % k)
    T["meta"] = meta
    return T

# ---------------------------------------------------------------- templates
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E"
           "%3Crect width='64' height='64' fill='%23f5f5dc'/%3E"
           "%3Cpath d='M32 54 C14 46 10 30 14 14 C24 22 30 34 32 54 Z' fill='%237b8fdc'/%3E"
           "%3Cpath d='M32 54 C50 46 54 30 50 14 C40 22 34 34 32 54 Z' fill='%237b8fdc'/%3E"
           "%3Cpath d='M32 54 C24 40 24 22 32 6 C40 22 40 40 32 54 Z' fill='%231f4690'/%3E%3C/svg%3E")

FONTS = ("https://fonts.googleapis.com/css2?family=Forum&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400"
         "&family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400;1,500&family=Jost:wght@400;500;600&family=Amiri:wght@700&display=swap")

GIFT_ICON = '''<svg viewBox="0 0 80 80" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">
  <rect x="10" y="24" width="60" height="42" rx="3"/>
  <path d="M10 28 L40 50 L70 28"/>
  <path d="M10 64 L31 44 M70 64 L49 44"/>
  <path d="M40 24 C40 24 29 17 29 11.5 C29 7.5 32.5 5.5 35 7 C37 8.2 40 11 40 11 C40 11 43 8.2 45 7 C47.5 5.5 51 7.5 51 11.5 C51 17 40 24 40 24 Z" fill="#d9a93a" stroke="#b08d47" stroke-width="1.4"/>
</svg>'''

def head(title, desc):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <!-- Keep the site out of search engines -->
  <meta name="robots" content="noindex, nofollow, noarchive, noimageindex">
  <meta name="googlebot" content="noindex, nofollow">
  <meta name="referrer" content="no-referrer">
  <link rel="icon" href="{FAVICON}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="{FONTS}" rel="stylesheet">
  <link rel="stylesheet" href="assets/style.css">
</head>'''

def crown():
    return '<div class="crown" aria-hidden="true"><img src="assets/art/crown.svg" alt="" decoding="async"></div>'

def header(T, active):
    home, reg, rsvp = T["navlabels"]
    a, b = T["sitename"]
    def link(href, label, key):
        cur = ' aria-current="page"' if active == key else ''
        return f'<a href="{href}"{cur}>{label}</a>'
    return f'''<header class="site-header reveal is-visible">
  <a class="wordmark" href="index.html">{a} <span class="amp">&amp;</span> {b}</a>
  <nav class="site-nav" aria-label="Main">
    {link("index.html", home, "home")}
    {link("registry.html", reg, "registry")}
    {link("rsvp.html", rsvp, "rsvp")}
  </nav>
</header>'''

def footer(T):
    home, reg, rsvp = T["navlabels"]
    a, b = T["sitename"]
    return f'''<footer class="site-footer">
  <div class="inner">
    <div class="wordmark">{a} <span class="amp">&amp;</span> {b}</div>
    <p class="caption">{T["footerline"][0]}</p>
    <nav aria-label="Footer">
      <a href="index.html">{home}</a>
      <a href="registry.html">{reg}</a>
      <a href="rsvp.html">{rsvp}</a>
    </nav>
  </div>
  <div class="ribbon" aria-hidden="true"></div>
</footer>
<script src="config.js"></script>
<script src="assets/site.js" defer></script>
</body>
</html>'''

def page_index(T):
    arch = open(ARCH, encoding="utf-8").read().replace(' preserveAspectRatio="none"', '')
    arch = re.sub(r'<!-- apex lotus finial.*?</g>\s*</g>',
                  '<image class="arch-finial" href="assets/art/finial.svg" x="241" y="-54" width="118" height="67"/>',
                  arch, flags=re.S)
    title, desc = T["meta"]["index"]
    bis_ar, bis_en = T["bismillah"]
    n1, n2 = T["names"]
    day, num, time, month = T["dateline"]
    ld, lh, lm, ls, sd, sh, sm, ss = T["countdownlabels"]
    ay_ar, ay_en, ay_cite = T["ayah"]
    sh_small, sh_big = T["sectionhead"]
    w_lbl, w_title, w_sub = T["cardwhen"]
    p_lbl, p_venue, p_street, p_city, p_link, p_url = T["cardwhere"]
    r_lbl, r_title, r_by, r_link = T["cardreply"]
    g_title, g_text, g_btn = T["giftnote"]
    return head(title, desc) + f'''
<body class="page-home">
{crown()}
<div class="top">
<img class="lantern lantern--left" src="assets/art/lantern-left.svg" alt="" aria-hidden="true" decoding="async">
<img class="lantern lantern--right" src="assets/art/lantern-right.svg" alt="" aria-hidden="true" decoding="async">
{header(T, "home")}
<main id="main">

  <section class="hero">
    <div class="arch-wrap">
    <img class="bouquet bouquet--left reveal" data-delay="3" src="assets/art/bouquet-left.svg" alt="" aria-hidden="true" decoding="async" loading="lazy">
    <img class="bouquet bouquet--right reveal" data-delay="3" src="assets/art/bouquet-right.svg" alt="" aria-hidden="true" decoding="async" loading="lazy">
    <div class="arch reveal" data-delay="2">
      {arch}
      <div class="arch-body">
        <div class="arch-inner">
          <p class="arabic bismillah" lang="ar">{bis_ar}</p>
          <p class="translation bismillah-translation">{bis_en}</p>
          <p class="caption">{T["invitationline"][0]}</p>
          <h1 class="names">
            <span class="script">{n1}</span>
            <span class="and">and</span>
            <span class="script">{n2}</span>
          </h1>

          <div class="date-row" aria-label="{day} {num} {month}, {time}">
            <span class="side">{day}</span>
            <span class="numeral">{num}</span>
            <span class="side">{time}</span>
          </div>
          <p class="date-month">{month}</p>
          <p class="place">{T["place"][0]}</p>

          <div class="countdown" data-countdown="{T["eventdate"][0]}" data-today="{T["countdowndone"][0]}" aria-live="off">
            <div class="unit"><span class="num" data-unit="d">00</span><span class="lbl"><span class="long">{ld}</span><span class="short">{sd}</span></span></div>
            <div class="unit"><span class="num" data-unit="h">00</span><span class="lbl"><span class="long">{lh}</span><span class="short">{sh}</span></span></div>
            <div class="unit"><span class="num" data-unit="m">00</span><span class="lbl"><span class="long">{lm}</span><span class="short">{sm}</span></span></div>
            <div class="unit"><span class="num" data-unit="s">00</span><span class="lbl"><span class="long">{ls}</span><span class="short">{ss}</span></span></div>
          </div>

          <a class="btn" href="rsvp.html">{T["rsvpbutton"][0]}</a>
        </div>
      </div>
      <div class="arch-base" aria-hidden="true"></div>
    </div>
    </div>
  </section>

  <section class="ayah reveal">
    <p class="arabic" lang="ar">{ay_ar}</p>
    <p class="translation">{ay_en}</p>
    <div class="rule"><span class="caption caption--gold">{ay_cite}</span></div>
  </section>

  <section class="section" id="details">
    <div class="section-head reveal">
      <p class="caption">{sh_small}</p>
      <h2 class="display">{sh_big}</h2>
      <div class="rule"><span class="diamond"></span></div>
    </div>
    <div class="cards">
      <article class="card reveal" data-delay="1">
        <p class="caption">{w_lbl}</p>
        <h3 class="display">{w_title}</h3>
        <p class="sub">{w_sub}</p>
      </article>
      <article class="card reveal" data-delay="2">
        <p class="caption">{p_lbl}</p>
        <p class="venue">{p_venue}</p>
        <p class="sub">{p_street}<br>{p_city}</p>
        <a class="link" href="{p_url}" target="_blank" rel="noopener">{p_link}</a>
      </article>
      <article class="card reveal" data-delay="3">
        <p class="caption">{r_lbl}</p>
        <h3 class="display">{r_title}</h3>
        <p class="sub">{r_by} <span data-text="rsvpDeadline">December 3</span></p>
        <a class="link" href="rsvp.html">{r_link}</a>
      </article>
    </div>
  </section>

  <section class="note reveal">
    <div class="rule"><span class="diamond"></span></div>
    <h2 class="display" style="margin-top:22px">{g_title}</h2>
    <p class="lead">{g_text}</p>
    <a class="btn btn--ghost" href="registry.html">{g_btn}</a>
  </section>

</main>
</div>
{footer(T)}'''

def page_registry(T):
    title, desc = T["meta"]["registry"]
    small, big, lead = T["registryhead"]
    p_title, p_sub, p_btn, p_none, p_fine = T["registrypanel"]
    return head(title, desc) + f'''
<body class="page-registry">
{crown()}
{header(T, "registry")}
<main id="main" class="page">
  <p class="caption reveal is-visible">{small}</p>
  <h1 class="display reveal is-visible">{big}</h1>
  <div class="rule reveal is-visible"><span class="diamond"></span></div>
  <p class="lead reveal is-visible" data-delay="1">{lead}</p>

  <div class="panel reveal is-visible" data-delay="2">
    <div class="icon">{GIFT_ICON}</div>
    <h2 class="display">{p_title}</h2>
    <p class="sub">{p_sub}</p>
    <a class="btn" href="#" data-link="cashFund" data-fallback="{p_none}">{p_btn}</a>
    <p class="fine">{p_fine}</p>
  </div>
</main>
{footer(T)}'''

def page_rsvp(T):
    title, desc = T["meta"]["rsvp"]
    small, big, event, replyby = T["rsvphead"]
    f_title, f_sub = T["rsvpform"]
    l_name, l_contact, l_q, l_yes, l_no = T["formfields"]
    l_guests, l_hint, l_names = T["formguests"]
    l_exc, exc_max = T["formexception"]
    try:
        exc_max = max(3, int(exc_max))
    except ValueError:
        sys.exit("site-text.tex: \\formexception's second argument must be a number")
    options = "".join(f"<option>{i}</option>" if i <= 2 else f'<option disabled hidden>{i}</option>' for i in range(1, exc_max + 1))
    l_note, l_opt, l_send = T["formnote"]
    m_missing, m_sending, m_failed = T["formmessages"]
    t_title, t_yes, t_no = T["thankyou"]
    fb_title, fb_sub, fb_btn, fb_none, fb_fine = T["rsvpfallback"]
    return head(title, desc) + f'''
<body class="page-rsvp">
{crown()}
{header(T, "rsvp")}
<main id="main" class="page">
  <p class="caption reveal is-visible">{small}</p>
  <h1 class="display reveal is-visible">{big}</h1>
  <div class="rule reveal is-visible"><span class="diamond"></span></div>
  <p class="lead reveal is-visible" data-delay="1">{event}<br>{replyby} <strong><span data-text="rsvpDeadline">December 3</span></strong>.</p>

  <!-- On-site form: shown when config.js has rsvpScriptUrl -->
  <form class="panel rsvp-form reveal is-visible" data-delay="2" id="rsvp-form" novalidate hidden
        data-msg-missing="{m_missing}" data-msg-sending="{m_sending}" data-msg-failed="{m_failed}">
    <h2 class="display">{f_title}</h2>
    <p class="sub">{f_sub}</p>

    <div class="field">
      <label for="f-name">{l_name}</label>
      <input id="f-name" name="name" type="text" autocomplete="name" required>
    </div>
    <div class="field">
      <label for="f-contact">{l_contact}</label>
      <input id="f-contact" name="contact" type="text" autocomplete="email" required>
    </div>

    <fieldset class="field choice">
      <legend>{l_q}</legend>
      <label class="pill"><input type="radio" name="attending" value="{l_yes}" required><span>{l_yes}</span></label>
      <label class="pill"><input type="radio" name="attending" value="{l_no}"><span>{l_no}</span></label>
    </fieldset>

    <div class="only-attending">
      <div class="field">
        <label for="f-guests">{l_guests}</label>
        <select id="f-guests" name="guests" data-max="{exc_max}">{options}</select>
        <p class="hint">{l_hint}</p>
        <label class="check"><input type="checkbox" name="exception" id="f-exception" value="Yes"><span>{l_exc}</span></label>
      </div>
      <div class="field">
        <label for="f-guestnames">{l_names}</label>
        <textarea id="f-guestnames" name="guestNames" rows="2"></textarea>
      </div>
    </div>

    <div class="field">
      <label for="f-message">{l_note} <span class="opt">{l_opt}</span></label>
      <textarea id="f-message" name="message" rows="3"></textarea>
    </div>

    <!-- honeypot: humans never see this -->
    <div class="hp" aria-hidden="true"><label>Website<input name="website" type="text" tabindex="-1" autocomplete="off"></label></div>

    <button class="btn" type="submit">{l_send}</button>
    <p class="form-status" role="status" aria-live="polite"></p>
  </form>

  <!-- Thank-you panel, shown after a successful submission -->
  <div class="panel rsvp-thanks reveal is-visible" id="rsvp-thanks" hidden data-text-declined="{t_no}">
    <h2 class="display">{t_title}</h2>
    <p class="sub" id="rsvp-thanks-text">{t_yes}</p>
    <div class="rule" style="margin-top:22px"><span class="diamond"></span></div>
  </div>

  <!-- Fallback: Google Form link, used only when rsvpScriptUrl is empty -->
  <div class="panel reveal is-visible" data-delay="2" id="rsvp-fallback">
    <h2 class="display">{fb_title}</h2>
    <p class="sub">{fb_sub}</p>
    <a class="btn" href="#" data-link="rsvpForm" data-fallback="{fb_none}">{fb_btn}</a>
    <p class="fine">{fb_fine}</p>
  </div>

  <div class="embed" id="rsvp-embed" hidden>
    <iframe title="RSVP form" loading="lazy"></iframe>
  </div>
</main>
{footer(T)}'''

def main():
    T = load()
    for name, fn in (("index.html", page_index), ("registry.html", page_registry), ("rsvp.html", page_rsvp)):
        out = fn(T)
        with open(os.path.join(ROOT, name), "w", encoding="utf-8") as f:
            f.write(out)
        print("wrote", name, len(out), "bytes")

if __name__ == "__main__":
    main()
