# Ibrahim & Asma wedding website

A static site served by GitHub Pages.

**To change any text on the site:** edit `site-text.tex` (every string, in page order, with a legend at the top), then run

```
python3 tools/build_site.py
```

which rewrites the three HTML pages. Commit and push. `xelatex site-text.tex` makes a PDF proof of the text.

- `site-text.tex`: **all the words on the site**; the pages are generated from it
- `tools/build_site.py`: the generator (page structure lives here); `tools/arch.svg.html` is the arch ornament
- `index.html`: home (names, date, countdown, details). Generated, do not edit by hand
- `registry.html`: registry (single cash-fund link). Generated
- `rsvp.html`: RSVP form that writes to the Google Sheet. Generated
- `config.js`: **edit this** to set the RSVP script URL (or Google Form link), the cash fund link and the RSVP deadline
- `rsvp-apps-script.gs`: paste into a Google Sheet's Apps Script editor; setup steps are at the top of the file
- `assets/style.css`, `assets/site.js`: styling and behaviour
- `robots.txt` + `<meta name="robots" content="noindex">` keep the site out of search engines

To change a link, edit `config.js`, commit and push. GitHub Pages redeploys in about a minute.
