/* Ibrahim & Asma site behaviour: countdown, config links, reveal animation. */
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
      } else if (el.getAttribute("data-fallback-as") === "details" && el.getAttribute("data-fallback")) {
        /* No link: show the fallback text as readable lines (e.g. "Zelle ..., Venmo ...") instead of a button */
        var box = document.createElement("div");
        box.className = "pay-details";
        el.getAttribute("data-fallback").split(/\s*,\s*/).forEach(function (line) {
          if (!line) return;
          var p = document.createElement("span");
          p.textContent = line;
          box.appendChild(p);
        });
        el.parentNode.replaceChild(box, el);
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
  /* ---- RSVP: on-site form -> Google Sheet (Apps Script), else Google Form link ---- */
  var scriptUrl = (cfg.rsvpScriptUrl || "").trim();
  var form = document.getElementById("rsvp-form");
  var fallback = document.getElementById("rsvp-fallback");
  if (form && scriptUrl) {
    form.hidden = false;
    if (fallback) fallback.hidden = true;
    var embedWrap = document.getElementById("rsvp-embed");
    if (embedWrap) embedWrap.hidden = true;
    setupRsvpForm(form, scriptUrl);
  } else {
    applyLink("rsvpFormUrl", "[data-link='rsvpForm']", "#rsvp-embed");
  }

  function setupRsvpForm(form, url) {
    var status = form.querySelector(".form-status");
    var button = form.querySelector("button[type=submit]");
    var attendingOnly = form.querySelector(".only-attending");
    var radios = form.querySelectorAll("input[name=attending]");

    function isDeclining() {
      var checked = form.querySelector("input[name=attending]:checked");
      return !!checked && checked.getAttribute("data-role") === "decline";
    }
    function syncAttending() {
      var any = !!form.querySelector("input[name=attending]:checked");
      var declining = isDeclining();
      attendingOnly.hidden = declining;
      form.querySelector("#f-guestnames").required = any && !declining;
    }
    radios.forEach(function (r) { r.addEventListener("change", syncAttending); });
    syncAttending();

    var exception = form.querySelector("#f-exception");
    var guestsSel = form.querySelector("#f-guests");
    function syncException() {
      var unlocked = exception.checked;
      Array.prototype.forEach.call(guestsSel.options, function (opt) {
        if (parseInt(opt.value, 10) > 2) { opt.disabled = !unlocked; opt.hidden = !unlocked; }
      });
      if (!unlocked && parseInt(guestsSel.value, 10) > 2) guestsSel.value = "2";
    }
    if (exception && guestsSel) { exception.addEventListener("change", syncException); syncException(); }

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      form.classList.add("was-validated");
      if (!form.checkValidity()) {
        status.textContent = form.getAttribute("data-msg-missing") || "Please fill in the highlighted fields.";
        status.classList.add("error");
        var bad = form.querySelector(":invalid");
        if (bad && bad.focus) bad.focus();
        return;
      }
      status.classList.remove("error");
      status.textContent = form.getAttribute("data-msg-sending") || "Sending\u2026";
      button.disabled = true;

      var data = {};
      new FormData(form).forEach(function (v, k) { data[k] = String(v).trim(); });
      if (attendingOnly.hidden) { data.guests = "0"; data.guestNames = ""; }
      data.exception = exception && exception.checked ? "Yes" : "No";

      fetch(url, { method: "POST", body: JSON.stringify(data) })
        .then(function (r) { return r.json(); })
        .then(function (res) {
          if (!res || res.ok !== true) throw new Error(res && res.error ? res.error : "Unexpected reply");
          form.hidden = true;
          var thanks = document.getElementById("rsvp-thanks");
          var text = document.getElementById("rsvp-thanks-text");
          if (isDeclining() && text && thanks.getAttribute("data-text-declined")) {
            text.textContent = thanks.getAttribute("data-text-declined");
          }
          thanks.hidden = false;
          thanks.scrollIntoView({ behavior: "smooth", block: "center" });
        })
        .catch(function (err) {
          status.classList.add("error");
          status.textContent = form.getAttribute("data-msg-failed") || "Sorry, something went wrong sending your reply. Please try again in a moment.";
          button.disabled = false;
          if (window.console) console.error("RSVP submit failed:", err);
        });
    });
  }

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
