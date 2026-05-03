# File Search & Auditor for Google Drive™ — File Searching Scripts

## What This Is

A Google Apps Script add-on that searches Google Shared Drives for files matching
a user's search string, and writes the results to a new tab in a Google Sheet.
The long-term goal is a two-tier product:

- **Community edition** — open source, basic search, results to sheet.
- **Marketplace Pro edition** — adds permission mining, external sharing risk
  detection, scheduled snapshots, and bulk permission remediation.

The project is currently in the prototyping phase as a bound script attached to a
Google Sheet. Once the logic is stable it will be moved to a standalone project
for Google Workspace Marketplace submission.

## Directory Structure

```
/home/temple/Documents/AppsScript/FileSearchScripts/
├── CLAUDE.md            ← this file
├── appsscript.json      ← OAuth scopes and runtime config
├── listFilesFound.gs    ← main Apps Script logic (the one we're developing)
├── searchInput.html     ← sidebar UI shown in Google Sheets
└── css.html             ← placeholder (not yet used)
```

## Scripts

### listFilesFound.gs — The Drive Searcher

- Adds a **"File Search"** custom menu to Google Sheets via `onOpen()`.
- Opens a sidebar (`searchInput.html`) where the user types a search string.
- `driveLister(searchString)` is the main entry point called from the sidebar:
  - Reads a list of shared drive IDs from a sheet tab called **"myDrives"** (column B).
  - Creates a new sheet tab named after the search string to hold results.
  - Searches every listed drive for files whose full text contains every word in
    the search string (AND logic).
  - Writes results to the new tab: Name, ID, Link, Created Date, Modified Date,
    Mime Type, Size, Shared Drive Name, Description.
  - Returns an HTML status string to the sidebar ("Found N files" / "No records found").
- `generateDriveFiles(driveId, filesQuery, driveNameCache)` — fetches and formats
  results for a single drive.
- `driveCall_(filesQuery, driveId, driveNameCache)` — makes paginated Drive API v3
  `files.list` calls, caches drive names to avoid redundant API calls.

### searchInput.html — The Sidebar UI

- Plain HTML/CSS sidebar styled to match Google Workspace (no Bootstrap dependency).
- Text input for the search string, Search button, Clear button.
- Shows a CSS spinner while the search is running.
- Disables the Search button during a search to prevent double-clicks.
- Calls `google.script.run.driveLister()` and handles both success and error callbacks.
- Enter key triggers the search.

### css.html — Placeholder

- Currently empty. Reserved for shared styles if the project grows.

## Coding Style

- Every function needs a descriptive heading comment explaining what it does,
  its parameters, and what it returns.
- **Every single line of code must have a comment explaining its intent.** The
  code should be understandable by anyone reading it — "should I get abducted by
  aliens" level of clarity.
- Use `const` and `let` — never `var`.
- Comments go at the end of the line where practical, or on the line above for
  longer explanations.
- Use the language/vocabulary the user would use — don't over-formalise.

## appsscript.json — Required OAuth Scopes

```json
{
  "timeZone": "Europe/London",
  "dependencies": {},
  "exceptionLogging": "STACKDRIVER",
  "runtimeVersion": "V8",
  "oauthScopes": [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/script.container.ui",
    "https://www.googleapis.com/auth/script.external_request"
  ]
}
```

Note: The target scope for Marketplace submission is
`https://www.googleapis.com/auth/drive.metadata.readonly` (Sensitive, not
Restricted — avoids the $10,000+ annual security audit). The current
`drive.readonly` scope is used during development. The Drive API advanced service
must also be enabled in the Apps Script project (Services → Drive API v3).

## myDrives Sheet

The script reads shared drive IDs from a sheet tab called **"myDrives"**:
- Row 1 is a header row (skipped).
- Column A: human-readable drive name (for reference only).
- Column B: the shared drive ID (this is what the script uses).

## Key Architectural Decisions

- **`UrlFetchApp` not Advanced Drive Service** — the script calls the Drive API
  directly via `UrlFetchApp` rather than using the Apps Script Advanced Drive
  Service. This gives full control over the API request and response.
- **Drive name caching** — a `Map` is passed between functions so each shared
  drive's name is only looked up once per search run, regardless of how many
  files are found on that drive.
- **Batch write** — all results are accumulated in memory and written to the sheet
  in a single `setValues()` call per drive, rather than row by row.
- **lastRow scoping** — `lastRow` is passed explicitly between functions. It must
  NOT be a global variable as this causes rows to overwrite each other when
  searching multiple drives.
- **Sheet tab naming** — the search string is sanitised before use as a tab name
  (removes characters Google Sheets disallows: `[ ] * ? : / \`, max 100 chars).
  Any existing tab with the same name is deleted and recreated fresh.

## Planned Pro Features (not yet implemented)

These are the USPs that will differentiate the Marketplace edition from the
open-source Community edition:

1. **Permission mining** — add `permissions` to the Drive API `fields` parameter
   to retrieve who has access to each file. Requires `drive.metadata.readonly`.
2. **External sharing risk detection** — flag files shared with `type: "anyone"`
   (Anyone with the link) or with email addresses outside the organisation's domain.
3. **Scheduled snapshots** — use Apps Script time-driven triggers to re-run the
   search automatically every 24 hours and append a timestamped results tab.
4. **Bulk permission remediation** — let the user mark rows in the results sheet
   and revoke access for a specific user directly from the sheet.

## Platform Notes

- Google Apps Script (V8 runtime).
- Runs inside a Google Sheets spreadsheet as a bound script (prototype phase).
- The Drive API advanced service must be enabled: Apps Script editor → Services → Drive API.
- `onOpen()` runs automatically when the spreadsheet is opened — it builds the
  custom menu. Only one `onOpen` can exist per project.
- `SpreadsheetApp.getUi()` only works in UI context (menu clicks, sidebar
  interactions) — NOT from time-driven triggers.
- Apps Script execution limit: 6 minutes for consumer Gmail accounts, 30 minutes
  for Google Workspace accounts. Large searches across many drives may approach
  this limit.
- The Google Workspace Marketplace requires a 1-hour minimum interval for
  published add-on triggers. Time-driven trigger features will need to respect
  this when the Marketplace edition is built.
