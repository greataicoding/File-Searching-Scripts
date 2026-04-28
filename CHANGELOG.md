# Changelog

> *Developed by Temple, Claude, Gemini and ChatGPT — see [PROJECT_ASSISTANT_ROLE.md](PROJECT_ASSISTANT_ROLE.md).*

All notable changes to Drive Auditor are documented here.

---

## listFilesFound.gs

### v12
- Fixed a bug where searching for "Folders Only" returned false positives. The Drive API's `fullText` operator matches folder metadata (like the creator's name and share history) as well as file content, so a search for "Smith" with only Folders ticked was returning every folder created by anyone called Smith. The script now automatically rewrites the query to use the `name` (title) field instead of `fullText` when only Include Folders is ticked. This applies to all three search modes — default word search, `"exact phrase"`, and `title:`.

### v11
- Added a frozen header row and automatic column filtering to every results sheet — the column titles stay visible while you scroll, and you can sort/filter on any column without setting it up by hand.
- Added **Include Files** and **Include Folders** checkboxes to the sidebar UI, with their state passed through to `driveLister()` and `generateDriveFiles()`. The `mimeFilter` portion of the Drive API query is built dynamically based on which boxes are ticked: files-only excludes folders, folders-only includes only folders, both ticked searches everything.

### v10
- Code cleanup pass for Marketplace maintainability. Restored the line-by-line comment density in `detectDrives()`, `generateDriveFiles()`, and `driveCall_()` to match the project's coding standard ("should I get abducted by aliens" level of clarity). Corrected multi-line indentation alignment in the `generateDriveFiles()` return array so the per-column comments line up neatly.

### v9
- Added a Smart Query Builder. The search box now supports three modes: default word search (every word must appear, joined with `AND`), `"exact phrase"` (the exact phrase must appear together), and `title:something` (search file names only, ignore content).
- Added single-quote escaping in the query builder so searches for words containing apostrophes (`it's broken`, `o'malley`) no longer crash the Drive API.

### v8
- Added "Silent Refresh" logic to `driveLister()`. If a user searches for the exact same string twice, the script now finds the existing tab and clears it rather than throwing an error about trying to create a duplicate sheet name. New tabs are still created for new searches.

### v7
- Fixed a logic bug where `detectDrives()` failed to delete an invalid `myDrives` sheet when the user had zero Shared Drives — the deletion now happens on both the "found drives" and "no drives" branches, so a stale or wrong-format sheet always gets cleaned up.
- Added clearer logging in `driveCall_()` to gracefully identify and skip Folder IDs that have been mistakenly pasted into the Drive ID column instead of a real Shared Drive ID. The error log now explicitly says the ID looks like a Folder ID rather than a generic API error.

### v6
- Added `SpreadsheetApp.flush()` after rebuilding the `myDrives` sheet to prevent Apps Script from reading cached/stale data on the next call.
- Added a URL sanitiser to `driveLister()` — if a user pastes a full Drive URL into the Drive ID column instead of just the ID, the script now automatically extracts the ID portion before using it.

### v5
- Fixed script failures when encountering invalid Shared Drives. Added explicit `break` statements after error responses in both `driveCall_()` and `detectDrives()` so a single bad drive can't hang the pagination loop. Replaced direct `response.error.message` access with safer parsing (`typeof response.error === 'object' ? response.error.message : response.error`) to handle both string and object error formats.
- Corrected a syntax error caused by a broken comment line in `driveLister()`.

### v4
- `driveLister()` now validates the `myDrives` sheet structure before reading it. New helper `isMyDrivesSheetValid_(sheet)` checks the column headers are `Include / Drive Name / Drive ID`. If the sheet was created manually or has an old layout, `detectDrives()` is called to rebuild it from scratch.
- Fixed a bug where `driveData[i][1]` (the drive name column) was being used instead of `driveData[i][2]` (the drive ID column) when building the search parameters — searches were silently failing because the API was being passed names instead of IDs.

### v3
- `detectDrives()` now deletes and recreates the `myDrives` sheet rather than just clearing the cell values. This means legacy column structures from older versions can never cause the script to read data from the wrong column.

### v2
- Added automatic drive detection via `detectDrives()`. The script now auto-populates the `myDrives` sheet with checkboxes on first run, so the user no longer has to hunt down Shared Drive IDs by hand and paste them in.
- Added My Drive support — consumer Gmail users with no Shared Drives get a simple yes/no toggle in the sidebar instead of the full myDrives workflow.
- `driveCall_()` updated to handle both `corpora: 'drive'` (for Shared Drives) and `corpora: 'user'` (for My Drive).
- New `setSearchMyDrive()` function persists the My Drive toggle state to script properties so the choice survives between sessions.

### v1
- Initial working version. Searches Shared Drives listed in the `myDrives` sheet by drive ID. Results written to a new sheet tab named after the search string. Pagination, drive name caching, and batch write all working from day one.

---

## searchInput.html

### v2
- Plain CSS rewrite styled to match the Google Workspace visual language — replaced the original Bootstrap dependency with hand-rolled styles (Google Sans font stack, Google Blue `#1a73e8` for primary actions, light grey `#f1f3f4` for secondary, `#dadce0` borders, subtle 4px corner rounding).
- Added a CSS spinner (`.spin`) using pure CSS keyframes — no image asset required.
- Search button is now disabled while a search is running, with reduced opacity and a `not-allowed` cursor, to prevent double-clicks.
- Added an "init loading" state shown while `detectDrives()` runs on first sidebar load and on Refresh.
- Added a Refresh Drives button that re-runs `detectDrives()` to pick up newly-added Shared Drives.
- Added the My Drive toggle row, shown only when `detectDrives()` returns `"my_drive_only"` (consumer Gmail users with no Shared Drives).
- Added Include Files / Include Folders checkboxes wired into `submitSearch()`.
- Added the search syntax tip line under the search box explaining `"exact phrase"` and `title:` modes.
- Enter key in the search box now triggers Search.

### v1
- Initial sidebar with a text input, Search button, and Clear button. Results status displayed below the buttons. Originally styled with Bootstrap.
