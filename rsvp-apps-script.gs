/**
 * RSVP collector for the wedding website.
 *
 * Setup (once):
 *   1. Create a blank Google Sheet.
 *   2. Extensions > Apps Script. Delete the sample code, paste this whole file, save.
 *   3. Deploy > New deployment > type "Web app".
 *        Execute as: Me
 *        Who has access: Anyone
 *      Authorise when asked, then copy the Web app URL (ends in /exec).
 *   4. Paste that URL into config.js as rsvpScriptUrl.
 *
 * If you ever edit this script: Deploy > Manage deployments > edit > New version.
 */

var SHEET_NAME = 'RSVPs';
var NOTIFY_EMAIL = '';   // e.g. 'you@example.com' to get an email for each RSVP; leave '' for none

var MAX_GUESTS = 2;             // per invitation
var MAX_WITH_EXCEPTION = 8;     // when the guest ticks the exception box

var HEADERS = ['Timestamp', 'Name', 'Email / phone', 'Attending', 'Guests', 'Exception', 'Guest names', 'Message'];

function doPost(e) {
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(10000);
    var data = parseBody_(e);
    if (data.website) return respond_({ ok: true }); // honeypot filled in: silently ignore bots

    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
    if (sheet.getLastRow() === 0 || sheet.getLastColumn() < HEADERS.length) {
      sheet.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]).setFontWeight('bold');
      sheet.setFrozenRows(1);
    }
    var exception = /^yes$/i.test(String(data.exception || '')) ? 'Yes' : 'No';
    var cap = exception === 'Yes' ? MAX_WITH_EXCEPTION : MAX_GUESTS;
    var guests = Math.min(cap, Math.max(0, parseInt(data.guests, 10) || 0));
    var row = [
      new Date(),
      clean_(data.name),
      clean_(data.contact),
      clean_(data.attending),
      guests,
      exception,
      clean_(data.guestNames),
      clean_(data.message)
    ];
    sheet.appendRow(row);

    if (NOTIFY_EMAIL) {
      MailApp.sendEmail({
        to: NOTIFY_EMAIL,
        subject: 'RSVP: ' + row[1] + ', ' + row[3],
        body: HEADERS.map(function (h, i) { return h + ': ' + row[i]; }).join('\n')
      });
    }
    return respond_({ ok: true });
  } catch (err) {
    return respond_({ ok: false, error: String(err) });
  } finally {
    lock.releaseLock();
  }
}

function doGet() {
  return respond_({ ok: true, message: 'RSVP endpoint is live.' });
}

function parseBody_(e) {
  if (e && e.postData && e.postData.contents) {
    try { return JSON.parse(e.postData.contents); } catch (ignore) {}
  }
  return (e && e.parameter) || {};
}

function clean_(v) {
  return String(v == null ? '' : v).replace(/^[=+\-@]/, "'$&").slice(0, 2000);
}

function respond_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
