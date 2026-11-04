/* Ibrahim & Asma — site behaviour: countdown, config links, reveal animation. */
(function () {
  var cfg = window.WEDDING_CONFIG || {};

  /* ---- Links that come from config.js ---- */
  function applyLink(key, selector, embedSel) {
    var url = (cfg[key] || "").trim();
    document.querySelectorAll(selector).forEach(function (el) {
      if (url) {
        el.setAttribute("href", url);
        el.setAttribute("target", "_blank");
        el.setAttribute("rel", "noopener");
        el.removeAttribute("aria-disabled");
      } else {
        el.setAttribute("aria-disabled", "true");
        el.setAttribute("href", "#");
        el.addEventListener("click", function (e) { e.preventDefault(); });
        var fallback = el.getAttribute("data-fallback");
        if (fallback) el.textContent = fallback;
      }
    });
    if (embedSel) {
      var wrap = document.querySelector(embedSel);
      if (wrap) {
        var frame = wrap.querySelector("iframe");
        if (url && /docs\.google\.com\/forms/.test(url) && frame) {
          var src = url.replace(/\?.*$/, "");
          if (!/\/viewform$/.test(src)) src = src.replace(/\/?$/, "/viewform");
          frame.src = src + "?embedded=true";
          wrap.hidden = false;
        } else {
          wrap.hidden = true;
        }
      }
    }
  }
  applyLink("rsvpFormUrl", "[data-link='rsvpForm']", "#rsvp-embed");
  applyLink("cashFundUrl", "[data-link='cashFund']");
  document.querySelectorAll("[data-text='rsvpDeadline']").forEach(function (el) {
    if (cfg.rsvpDeadline) el.textContent = cfg.rsvpDeadline;
  });

  /* ---- Countdown to the wedding day (midnight local time, like the old site) ---- */
  var cd = document.querySelector("[data-countdown]");
  if (cd) {
    var target = new Date(cd.getAttribute("data-countdown") + "T00:00:00");
    var units = {
      d: cd.querySelector("[data-unit='d']"),
      h: cd.querySelector("[data-unit='h']"),
      m: cd.querySelector("[data-unit='m']"),
      s: cd.querySelector("[data-unit='s']")
    };
    function pad(n) { return n < 10 ? "0" + n : "" + n; }
    function tick() {
      var diff = target - new Date();
      if (diff <= 0) {
        var todayMsg = cd.getAttribute("data-today") || "Today is the day";
        cd.innerHTML = '<span class="today">' + todayMsg + "</span>";
        return;
      }
      var s = Math.floor(diff / 1000);
      var d = Math.floor(s / 86400); s -= d * 86400;
      var h = Math.floor(s / 3600); s -= h * 3600;
      var m = Math.floor(s / 60); s -= m * 60;
      units.d.textContent = d;
      units.h.textContent = pad(h);
      units.m.textContent = pad(m);
      units.s.textContent = pad(s);
      setTimeout(tick, 1000 - (Date.now() % 1000));
    }
    tick();
  }

  /* ---- Reveal on load / on scroll ---- */
  var items = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("is-visible"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px" });
    items.forEach(function (el) { io.observe(el); });
  } else {
    items.forEach(function (el) { el.classList.add("is-visible"); });
  }
})();
