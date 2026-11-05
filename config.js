/* ============================================================
   Edit this file to update links on the site. Nothing else
   needs to change. Paste the full URL between the quotes.
   ============================================================ */
window.WEDDING_CONFIG = {

  /* RSVP form on the site -> Google Sheet.
     Paste the Apps Script "Web app" URL (ends in /exec) from
     rsvp-apps-script.gs. Leave empty ("") to fall back to rsvpFormUrl. */
  rsvpScriptUrl: "https://script.google.com/macros/s/AKfycbwUAwxNeC1t4KNvu1YoFFdyaKnSGzz3Am48BAeGL3K1eOEqbjA16hkHaNUu6QPYLRyP/exec",

  /* Fallback: a Google Form link, used only if rsvpScriptUrl is empty.
     e.g. "https://docs.google.com/forms/d/e/XXXXXXXX/viewform" */
  rsvpFormUrl: "",

  /* Cash fund link (Venmo, PayPal, Zelle page, etc.).
     Leave empty ("") to show "Details coming soon". */
  cashFundUrl: "",

  /* RSVP deadline shown on the site. */
  rsvpDeadline: "November 20"
};
