# Ibrahim & Asma — wedding website

A static site served by GitHub Pages. No build step.

- `index.html` — home (names, date, countdown, details)
- `registry.html` — registry (single cash-fund link)
- `rsvp.html` — RSVP (links to / embeds the Google Form)
- `config.js` — **edit this** to set the RSVP form link, the cash fund link and the RSVP deadline
- `assets/style.css`, `assets/site.js` — styling and behaviour
- `robots.txt` + `<meta name="robots" content="noindex">` keep the site out of search engines

To change a link, edit `config.js`, commit and push. GitHub Pages redeploys in about a minute.
