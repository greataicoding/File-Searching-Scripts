# File Search & Auditor for Google Drive™ — File Search & Sharing Audit Tool

> *Developed by Temple and Claude — a collaboration between a human developer and Anthropic's Claude (chat) and Claude Code. See [PROJECT_ASSISTANT_ROLE.md](PROJECT_ASSISTANT_ROLE.md) for how this project was built.*

A Google Apps Script project that searches across your Google Shared Drives (and optionally your personal My Drive) for files matching a search string, and writes the results to a new tab in a Google Sheet — including who has access to each file and whether anything is shared externally.

This is the **Community edition** — open-source, manually installed via copy/paste, with the full feature set including basic external-sharing detection. A Marketplace edition with narrower permissions and Pro features (scheduled snapshots, bulk permission remediation, organisation-aware risk detection) is in development.

---

## ⚠️ Heads up: Drive Read Permissions

**Before you install, you need to know what you're agreeing to.**

The Community edition requests `https://www.googleapis.com/auth/drive.readonly` — Google's full Drive read scope. This is because it needs to search file *content* (not just titles), and to read each file's permission list to detect external sharing risks.

**What this means in practice:**

- The app *can* read any file in your Drive and any Shared Drive you have access to
- It cannot modify, move, or delete any file — read-only means read-only
- In reality, it only uses these permissions for the documented features: searching for files matching your query, listing them in a sheet, and reporting who has access
- All code is open-source and in this repository — you can verify exactly what it does before installing
- Nothing is sent anywhere; all processing happens inside your own Google account

**If you'd rather not grant content-read access,** you have two options:

1. **Wait for the Marketplace edition** (coming soon) — it'll use the narrower `https://www.googleapis.com/auth/drive.metadata.readonly` scope, which lets the script search file names and list permissions without ever reading file contents. This is a "Sensitive" scope (rather than "Restricted"), so it avoids the $10,000+ annual security assessment Google requires for full Drive scopes.
2. **Modify this code yourself** — swap `drive.readonly` for `drive.metadata.readonly` in `appsscript.json`. Full-text content search will stop working, but title and metadata searches will still function.

**Only install this if you've read the above and are comfortable with granting full Drive read access to a script you've reviewed and trust.**

---

## Table of Contents

- [What It Does](#what-it-does)
- [How It Works — The Big Picture](#how-it-works--the-big-picture)
- [Scripts Overview](#scripts-overview)
- [Setup & Installation](#setup--installation)
- [Using the App](#using-the-app)
  - [Step 1: Open the Sidebar](#step-1-open-the-sidebar)
  - [Step 2: Pick Which Drives to Search](#step-2-pick-which-drives-to-search)
  - [Step 3: Run Your Search](#step-3-run-your-search)
  - [Step 4: Review the Results](#step-4-review-the-results)
- [Spreadsheet Sheets Reference](#spreadsheet-sheets-reference)
  - [myDrives](#mydrives)
  - [Results tabs (one per search)](#results-tabs-one-per-search)
- [Search Syntax](#search-syntax)
- [Architecture & Key Concepts](#architecture--key-concepts)
  - [UrlFetchApp not Advanced Drive Service](#urlfetchapp-not-advanced-drive-service)
  - [Drive Name Caching](#drive-name-caching)
  - [Batch Writes](#batch-writes)
  - [lastRow Scoping](#lastrow-scoping)
  - [Smart Folder-Only Search](#smart-folder-only-search)
  - [Pagination](#pagination)
  - [My Drive vs Shared Drives](#my-drive-vs-shared-drives)
- [Function Reference](#function-reference)
- [OAuth Scopes](#oauth-scopes)
- [Platform Notes & Limitations](#platform-notes--limitations)
- [Version History](#version-history)

---

## What It Does

File Search & Auditor for Google Drive™ (the "App") answers a simple question: **where in my Drives is that file, and who has access to it?**

It searches every Shared Drive you have access to (plus your personal My Drive if you tick the box) for files matching your search string, then produces a spreadsheet listing each match with its name, ID, link, dates, type, size, the drive it lives on, who it's shared with, and whether anyone outside your organisation has access.

### Clickable File Links

Each file in the **Link** column of the results sheet is the file's standard `webViewLink` — clicking it opens the file directly in Drive in a new tab. So you can eyeball a file before deciding what to do with it, or just use Drive's native sharing controls to deal with it manually.

This is especially useful when the **Risk Flag** column flags something as `⚠ EXTERNAL` — one click and you're looking at the file's sharing settings, ready to revoke access.

---

## How It Works — The Big Picture

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  1. DETECT       │     │  2. SEARCH       │     │  3. AUDIT        │
│                  │     │                  │     │                  │
│  Open the        │────▶│  Type a search   │────▶│  Review the      │
│  sidebar         │     │  string and hit  │     │  results sheet,  │
│                  │     │  Search          │     │  flag externals, │
│  Auto-discovers  │     │                  │     │  remediate       │
│  all your Shared │     │  Builds the      │     │  sharing in      │
│  Drives into the │     │  results tab     │     │  Drive directly  │
│  myDrives sheet  │     │  with sharing    │     │                  │
│                  │     │  info per file   │     │                  │
└──────────────────┘     └──────────────────┘     └──────────────────┘
```

The first time you open the sidebar, the App calls the Drive API to discover every Shared Drive you have access to and writes them into a sheet called `myDrives` with a tickbox next to each one. You decide which drives to search by ticking or unticking those boxes — no need to hunt down drive IDs by hand.

---

## Scripts Overview

The project has one script file, one sidebar HTML file, and a manifest:

| File | What It Does | Current Version |
|------|-------------|-----------------|
| `listFilesFound.gs` | All the Apps Script logic — drive detection, search, sheet writing | v12 |
| `searchInput.html` | The sidebar UI shown in Google Sheets | — |
| `css.html` | Placeholder for shared styles (currently empty) | — |
| `appsscript.json` | Project manifest — OAuth scopes, advanced services, runtime config | — |

`listFilesFound.gs` owns the `onOpen()` function that builds the **File Search** custom menu.

---

## Setup & Installation

1. **Create a new Google Sheets spreadsheet** — this will be the App's home base.

2. **Open the script editor** — go to Extensions > Apps Script.

3. **Copy the files** — create the files in the editor:
   - Paste the contents of `listFilesFound.gs` into the default `.gs` file
   - Add a new HTML file called `searchInput` and paste in the sidebar HTML
   - Add a new HTML file called `css` and paste in the placeholder
   - Replace the contents of `appsscript.json` with the project's manifest (you may need to enable "Show 'appsscript.json' manifest file in editor" under Project Settings)

4. **Enable the Drive API advanced service** — in the Apps Script editor, click the `+` next to **Services** in the left sidebar, find "Drive API", and add it. Make sure the version is **v3** and the identifier is `Drive`.

5. **Save and reload the spreadsheet** — close the script editor tab and refresh the spreadsheet. The **File Search** menu should appear in the menu bar.

6. **Authorise on first run** — the first time you click a menu item, Google will ask you to authorise the required permissions. You'll need to approve access to Drive (read-only), the current spreadsheet, the script container UI, and external requests (for the `UrlFetchApp` calls to the Drive API).

   If you change the OAuth scopes later (for example, swapping `drive.readonly` for `drive.metadata.readonly`), you'll need to re-authorise manually — Apps Script doesn't trigger re-authorisation automatically when scopes change.

---

## Using the App

### Step 1: Open the Sidebar

Open the spreadsheet and go to **File Search > Search Content for Strings**. The sidebar will open on the right and show "Detecting drives…" while it works out what you have access to.

What happens behind the scenes: the sidebar calls `detectDrives()`, which hits the Drive API to list every Shared Drive you can see. The results get written to a sheet called `myDrives`, with the user's personal **My Drive** added as the first row.

### Step 2: Pick Which Drives to Search

Once detection is done, the sidebar will say either "Search shared drives" (if you have at least one Shared Drive) or "Search My Drive" (if you're on a consumer Gmail account with no Shared Drives).

For Shared Drives users:

- Open the **myDrives** sheet at the bottom of the spreadsheet
- Each row has a tickbox in column A — tick the drives you want to include in the search, untick the ones you don't
- Don't worry about column C (the Drive ID) — that's just there so the script knows what to query

If you've added a new Shared Drive since you last opened the sidebar, click the **↻ Refresh Drives** button in the sidebar. This rebuilds the `myDrives` sheet from scratch with the latest list.

### Step 3: Run Your Search

Type your search string into the box and click **Search** (or press Enter).

You can also choose what *type* of items to search for:

- **Include Files** (ticked by default) — search regular files (Docs, Sheets, PDFs, images, etc.)
- **Include Folders** — search folders too

If you only tick **Include Folders**, the script automatically switches to a title-only search. (If it didn't, the Drive API would match folder *metadata* — like the creator's name — and return a load of false positives.)

The sidebar shows a spinner while the search runs and disables the Search button so you can't double-click. When it's done, you'll see "Found Records" or "No Records Found".

### Step 4: Review the Results

A new tab is created in the spreadsheet, named after your search string. (If a tab with that name already exists from a previous search, it gets cleared and rewritten — no duplicates, no errors about duplicate sheet names.)

The results tab has:

- A **frozen header row** so the column titles stay visible while you scroll
- An **automatic filter** on every column so you can sort and filter by any field
- One row per matching file, with full sharing details

The columns are documented under [Results tabs](#results-tabs-one-per-search) below.

---

## Spreadsheet Sheets Reference

### myDrives

The control sheet for which drives the script searches. Auto-created and auto-populated by `detectDrives()` when you first open the sidebar (or when you click Refresh Drives).

| Column | Header | Content |
|--------|--------|---------|
| A | Include | Tickbox — tick to include this drive in searches, untick to skip it |
| B | Drive Name | Human-readable name of the drive (for your reference only) |
| C | Drive ID | The Shared Drive ID the script uses to query the Drive API. The first row is always `MY_DRIVE` for the user's personal Drive |

Row 1 is the header row and is skipped when reading.

If you ever paste a full Drive URL into column C instead of just the ID, the script will automatically extract the ID portion before using it — so you don't need to be careful about format.

### Results tabs (one per search)

Each search creates (or overwrites) a tab named after the search string.

| Column | Header | Content |
|--------|--------|---------|
| A | Name | The file's display name |
| B | ID | The file's unique Drive ID |
| C | Link | The file's `webViewLink` — clickable, opens the file in Drive |
| D | Created Date | When the file was created |
| E | Modified Data | When the file was last modified *(typo preserved from v1 for backwards compatibility)* |
| F | Mime Type | The file type (e.g. `application/vnd.google-apps.document`) |
| G | Size | How many quota bytes the file uses (0 for native Google Docs/Sheets/Slides) |
| H | Shared Drive Name | Which drive the file lives on |
| I | Description Text | The file's description field (usually blank) |
| J | Shared With | Comma-separated emails of named users and groups with access |
| K | External Sharing | "Anyone with link" or "Private" |
| L | Risk Flag | `⚠ EXTERNAL` if any external party has named access, otherwise blank |

The **Risk Flag** column depends on the `ORG_DOMAIN` constant at the top of `listFilesFound.gs`. While `ORG_DOMAIN` is blank, the flag fires on every named user/group permission, because without a known domain we can't tell what counts as external. Set `ORG_DOMAIN` to your organisation's domain (e.g. `"mycompany.com"`) and the flag will only fire for emails outside that domain.

---

## Search Syntax

The search box supports three modes:

| You type | What happens |
|----------|--------------|
| `Q3 budget report` | Default mode — every word must appear somewhere in the file (full-text AND search) |
| `"Q3 budget report"` | Exact phrase mode — the exact phrase must appear together |
| `title:Q3 budget` | Title-only mode — search file names only, ignore file contents |

Single quotes inside your search are automatically escaped, so a search for `it's broken` won't crash the API.

If you tick **Include Folders** and untick **Include Files**, all three modes automatically switch to title-only search regardless of which mode you used — searching folder *contents* doesn't make sense.

---

## Architecture & Key Concepts

### UrlFetchApp not Advanced Drive Service

The script calls the Drive API v3 directly via `UrlFetchApp.fetch()` rather than using the Apps Script Advanced Drive Service. This gives full control over the request and response — every parameter is set explicitly, and the raw JSON response is parsed in script. The trade-off is more code, but the upside is no surprises.

### Drive Name Caching

When `driveCall_()` finds files in a Shared Drive, it needs to look up the drive's human-readable name to write into the results sheet. Without caching, this would mean one extra API call per file. Instead, a `Set` of unique drive IDs is built from each batch and the name lookup happens once per drive — then the name is stamped onto every matching file.

### Batch Writes

Results are accumulated in memory and written to the sheet in a single `setValues()` call per drive, rather than one row at a time. This is dramatically faster — Apps Script's per-call overhead is the dominant cost when writing to a sheet, so cutting down the number of calls makes a huge difference for large result sets.

### lastRow Scoping

`lastRow` tracks where to write the next row of results. It lives at module level (not as a global state stored in the spreadsheet) and gets reset to 2 at the start of every `driveLister()` call. This is critical: when searching across multiple drives, `generateDriveFiles()` advances `lastRow` after each drive's batch write so the next drive's results don't overwrite the previous drive's results.

The original v1 of this script had `lastRow` declared inside `generateDriveFiles()`, which caused exactly that overwrite bug — every drive started writing back at row 2. Moving it to module-level scope fixed it.

### Smart Folder-Only Search

The Drive API's `fullText` operator searches a file's content *and* certain metadata fields. For folders, that metadata includes the creator's name, share history, and other fields that have nothing to do with the folder's title. So if you search for "Smith" using `fullText` with folders only, you get back every folder created by anyone called Smith — not what you wanted.

Since v12, when only **Include Folders** is ticked (and **Include Files** is unticked), the script automatically rewrites the query to use the `name` field instead of `fullText`. This applies to all three search modes (default, exact phrase, and `title:`).

### Pagination

The Drive API returns at most 100 results per page. For large drives or broad searches, results are paginated using `nextPageToken` — `driveCall_()` loops until no token is returned, accumulating results across pages. The same pattern applies to `detectDrives()` for listing Shared Drives.

### My Drive vs Shared Drives

The Drive API requires different parameters for the two cases:

| Search target | `corpora` | `driveId` |
|---------------|-----------|-----------|
| A specific Shared Drive | `drive` | The Shared Drive's ID |
| The user's personal My Drive | `user` | (not set) |

`driveCall_()` checks the `isMyDrive` flag and sets the parameters accordingly. The `myDrives` sheet uses the literal string `MY_DRIVE` in column C as a sentinel value — when `driveLister()` sees that, it calls `generateDriveFiles()` with `isMyDrive = true`.

For consumer Gmail accounts (which have no Shared Drives at all), `detectDrives()` returns the string `"my_drive_only"`, and the sidebar shows a simple "Search My Drive" tickbox instead of the full myDrives workflow.

---

## Function Reference

### Entry Points

| Function | Purpose |
|----------|---------|
| `onOpen(e)` | Builds the **File Search** custom menu when the spreadsheet opens |
| `addMenu()` | Defines the menu and its items |
| `SearchForFileForm()` | Opens the search sidebar (`searchInput.html`) |

### Core Search Logic

| Function | Purpose |
|----------|---------|
| `detectDrives()` | Discovers all Shared Drives the user has access to and writes them to the `myDrives` sheet with tickboxes; returns `"found_shared_drives"` or `"my_drive_only"` |
| `driveLister(searchString, incFiles, incFolders)` | Main entry point called from the sidebar — builds the query, finds the ticked drives in `myDrives`, calls `generateDriveFiles()` for each, returns a status message to the sidebar |
| `generateDriveFiles(drive, sheet, queryString, isMyDrive, incFiles, incFolders)` | Searches a single drive (Shared or My Drive), formats the results, writes them to the sheet |
| `driveCall_(filesQuery, drive, isMyDrive)` | Calls the Drive API v3 `files.list` endpoint with pagination and drive-name caching |

### Helpers

| Function | Purpose |
|----------|---------|
| `setSearchMyDrive(value)` | Persists the My Drive checkbox state to script properties (used in My Drive only mode) |
| `isMyDrivesSheetValid_(sheet)` | Checks the `myDrives` sheet has the expected `Include / Drive Name / Drive ID` headers; returns false if it has an old layout |

### Constants

| Name | Purpose |
|------|---------|
| `ORG_DOMAIN` | Your organisation's email domain. Used by the Risk Flag logic in `generateDriveFiles()`. While blank, the flag fires on every named user/group permission |
| `lastRow` | Module-level row counter used to write results across multiple drives in one search |

---

## OAuth Scopes

Defined in `appsscript.json`:

| Scope | Why It's Needed |
|-------|----------------|
| `drive.readonly` | Read access to all your files and Shared Drives — needed for full-text content search and reading per-file permissions |
| `spreadsheets.currentonly` | Read and write to the spreadsheet the script is bound to |
| `script.container.ui` | Show the sidebar and custom menu in the spreadsheet UI |
| `script.external_request` | Make `UrlFetchApp` calls to the Drive API v3 endpoints |

**See the [broad permissions warning at the top of this README](#️-heads-up-drive-read-permissions) for a full explanation of the `drive.readonly` scope and the planned `drive.metadata.readonly` alternative for the Marketplace edition.**

**Why `drive.readonly` and not `drive.metadata.readonly`?** Metadata-only scope lets you list files, see their names, sizes, and permissions — but it doesn't let you search file *contents*. The Community edition's full-text search depends on the broader scope. The Marketplace edition will swap to metadata-only and search titles only, in exchange for avoiding Google's Restricted-scope security audit.

---

## Platform Notes & Limitations

- **Google Apps Script V8 runtime** — the project uses modern JavaScript (let/const, arrow functions, template literals, Maps, Sets, the spread operator).
- **Drive API advanced service** must be enabled in the Apps Script editor (Services > Drive API, v3).
- **Apps Script execution limit** — 6 minutes for consumer Gmail accounts, 30 minutes for Google Workspace. A search across many large Shared Drives could approach this limit; if it does, the script will time out and you'll see an error in the sidebar. The current version doesn't break searches into sessions like a long-running crawl would.
- **Bound script** — the project is currently a bound script attached to its host spreadsheet. Once the logic is stable it'll be moved to a standalone project for Marketplace submission (per the strategy notes in `claudeInput.txt`).
- **Only one `onOpen()` per project** — it lives in `listFilesFound.gs`.
- **`SpreadsheetApp.getUi()` only works in UI context** — the sidebar and menu items are fine, but any future time-driven trigger features (like scheduled snapshots) won't be able to use it.
- **Re-authorisation after scope changes** — Apps Script doesn't auto-trigger re-authorisation when you change the scopes in `appsscript.json`. You have to manually run a function from the editor to re-trigger the auth flow, or revoke the existing authorisation and re-grant it.
- **Sheet tab naming** — Google Sheets disallows certain characters in tab names (`[ ] * ? : / \`) and caps them at 100 characters. Search strings should be safe within these limits for typical use, but extremely long queries or queries with these characters may need sanitising.

---

## Planned Pro Features (Marketplace edition)

These are the differentiators planned for the Marketplace edition. None of them exist in the Community edition yet.

| Feature | What It Will Do |
|---------|-----------------|
| **Permission Mining** | Already partly built — the results sheet shows who has access to each file. The Pro version will add a dedicated permissions audit view. |
| **Org-aware Risk Detection** | The Risk Flag column will properly use `ORG_DOMAIN` to flag external users only, instead of flagging every named user. |
| **Scheduled Snapshots** | Use Apps Script time-driven triggers to re-run the search every 24 hours and append a timestamped results tab, so you can track what's changed. |
| **Bulk Permission Remediation** | Mark rows in the results sheet and revoke access for a specific user (e.g. an ex-employee or contractor) directly from the sheet. |
| **Cross-Drive Aggregation** | Single search across every Shared Drive simultaneously with consolidated results. |

---

## Version History

### listFilesFound.gs

| Version | Changes |
|---------|---------|
| v12 | Fixed false positives when searching folders only — the script now forces a `name` (title) search instead of `fullText` when only Include Folders is ticked, because `fullText` matches folder metadata (creator name, etc.) |
| v11 | Added frozen header row and automatic column filtering to the results sheet; added Include Files / Include Folders checkboxes to the sidebar |
| v10 | Code cleanup — restored line-by-line comment density to `detectDrives()`, `generateDriveFiles()`, and `driveCall_()` for Marketplace maintainability; corrected indentation alignment in the `generateDriveFiles()` return array |
| v9 | Added Smart Query Builder — `"exact phrase"` searches and `title:` prefix; single-quote escaping to prevent API crashes when searching for words containing apostrophes |
| v8 | Added "Silent Refresh" — searching for the same string twice no longer errors out; the existing tab is cleared and reused |
| v7 | Fixed `detectDrives()` failing to delete an invalid `myDrives` sheet when the user has 0 shared drives; added clearer logging in `driveCall_()` to identify and skip Folder IDs mistakenly passed as Shared Drive IDs |
| v6 | Added `SpreadsheetApp.flush()` after rebuilding `myDrives` to prevent stale-data reads; added URL sanitiser to `driveLister()` to extract the ID if a full URL is pasted into the Drive ID column |
| v5 | Fixed script failures on invalid Shared Drives by adding explicit loop breaks and safer error object parsing in `driveCall_()` and `detectDrives()`; corrected a syntax error from a broken comment line |
| v4 | `driveLister()` now validates the `myDrives` sheet structure via `isMyDrivesSheetValid_()` and rebuilds it via `detectDrives()` if the layout is wrong; fixed a bug where the drive name column was read instead of the drive ID column |
| v3 | `detectDrives()` now deletes and recreates the `myDrives` sheet rather than clearing it, so legacy column structures can never cause incorrect data to be read |
| v2 | Added automatic drive detection — `detectDrives()` auto-populates `myDrives` with checkboxes; added My Drive support for consumer Gmail users; `setSearchMyDrive()` persists the toggle state |
| v1 | Initial working version — searches Shared Drives by ID, results written to a new tab named after the search string, pagination, drive name caching, and batch write all working |
