# How This Project Was Built

## The Short Version

File Search & Auditor for Google Drive™ was built collaboratively between a human developer (Temple) and various AI tools; Gemini from Google, ChatGPT and, from Anthropic: **Claude** (via the web chat interface) and **Claude Code** (the CLI-based coding agent). This document is here so anyone looking at the repo understands how the code and docs came together.

---

## The Division of Labour

The workflow settled into a consistent pattern pretty early on, and it stuck:

- **Temple** — project lead, architect, tester, and the one making the final call on every design decision. Set the direction, wrote the requirements, reviewed every change, and caught the bugs that only showed up in real-world use (like the false-positive folder search in v12, where searching for a name returned every folder created by anyone with that name in their email address).
- **Claude (chat)** — strategy and diagnosis. Architectural discussions, log analysis, working out *why* something was broken before deciding *what* to do about it, and writing documentation like this one. Claude chat never touched the code directly.
- **Claude Code (CLI)** — the actual code changes. Every edit to `listFilesFound.gs` and `searchInput.html` went through Claude Code, following instructions handed over from the chat session.

This two-tool split worked well because it kept the strategic thinking (where mistakes are cheap and easily corrected) separate from the file editing (where a wrong change to the wrong line can silently break the whole thing). It also meant the chat session always had a clean view of the current state of the code, because the updated files got uploaded back to the project after every round of changes.

---

## The Iterative Loop

For almost every feature or fix, the cycle looked like this:

1. **Temple describes the problem or the goal.** Often with a screenshot of the sidebar, a line from the Apps Script execution log, or a specific symptom ("searching for 'Smith' with Folders Only is returning every folder created by anyone called Smith").
2. **Claude chat works out what's going on.** Reads the relevant parts of the code, asks clarifying questions where needed, and proposes a fix or an architectural change.
3. **Temple agrees, pushes back, or asks for alternatives.** A lot of the best design decisions came from pushback — for example, sticking with `UrlFetchApp` over the Advanced Drive Service because the explicit control over request/response made debugging API quirks much easier.
4. **Claude chat writes a prompt for Claude Code.** A specific, unambiguous set of instructions describing what to change and what to leave alone.
5. **Claude Code applies the changes.** Temple runs it, reviews the diff, and pastes the updated file into the Apps Script editor.
6. **Temple tests in the real Drive environment.** This is where the rubber meets the road — Apps Script's behaviour in production is often different from what the docs suggest. The Drive API in particular has a load of subtle differences between what `corpora`, `supportsAllDrives`, and `includeItemsFromAllDrives` actually do in practice versus what the docs say.
7. **Log output gets pasted back into chat.** Any problems get diagnosed, and the loop starts again.

---

## What the AI Actually Contributed

### Code

- The full codebase of `listFilesFound.gs` (12 versions and counting) and the rewritten `searchInput.html` sidebar UI.
- The `detectDrives()` auto-discovery flow that replaced the original "paste in Drive IDs by hand" approach — meaning users no longer have to hunt down Shared Drive IDs to use the tool.
- The drive name caching pattern in `driveCall_()` that does the lookup once per drive instead of once per file, saving hundreds or thousands of API calls on a busy search.
- The Smart Query Builder (v9) that handles `"exact phrase"` and `title:` modes, plus the single-quote escaping that stopped searches for `it's broken` from crashing the Drive API.
- The plain CSS rewrite of the sidebar to match the Google Workspace look without any Bootstrap dependency.
- Every inline comment on every line of code (per Temple's "abducted by aliens" coding standard — the code should be understandable to any future reader, including a future version of Temple).

### Debugging

Some of the harder problems that came out of genuine collaboration between Temple and Claude:

- **The original `lastRow` overwrite bug** — the v1 code declared `lastRow` inside `generateDriveFiles()`, which meant every drive started writing back at row 2 and overwrote the previous drive's results. The fix (move `lastRow` to module scope and reset it at the start of `driveLister()`) sounds obvious in hindsight but only became clear after the symptom — "I'm only seeing results from one of three drives" — got investigated properly.
- **The `driveData[i][1]` vs `driveData[i][2]` bug (v4)** — searches were silently failing because the script was passing drive *names* to the API instead of drive *IDs*. The Drive API doesn't error in any helpful way when you do this; it just returns empty results. Took a careful read of the column layout to spot.
- **The folder-search false positives (v12)** — the Drive API's `fullText` operator matches more than just file content. For folders, it also matches the creator's name, share history, and other metadata fields. So a search for "Smith" with Folders Only returned every folder created by anyone called Smith. The fix was to detect the folders-only case and rewrite the query to use `name` instead of `fullText`.
- **The Drive API enablement saga** — early on, there was a lot of trial and error trying to enable the Drive API via the Google Cloud Console or by editing `appsscript.json` directly. Temple identified that the correct approach is to add the Drive API via the **Services (➕) panel** in the Apps Script editor, not the Cloud Console. This was a "nope, that's wrong, here's the actual way" correction from Temple that got built into the project's setup notes.
- **The OAuth re-authorisation gotcha** — adding new scopes to `appsscript.json` doesn't trigger Apps Script to ask the user to re-authorise. You have to manually run a function from the editor to re-trigger the auth flow. This caught us out a few times before getting properly documented.
- **The stale `myDrives` sheet bug (v6)** — `SpreadsheetApp` can return cached data if you read a sheet immediately after rebuilding it. `SpreadsheetApp.flush()` between the rebuild and the read fixed it.

### Documentation

- This `README.md` — structure, prose, architectural explanations, function reference tables, version history.
- `CLAUDE.md` — the project-internal reference doc that gives future Claude Code sessions a head start on the conventions.
- `CHANGELOG.md`, `LICENSE`, the GitHub issue/PR templates, and this document.

---

## What the AI Did Not Do

Worth being clear about this too:

- **No architectural decisions without review.** Every "here's how I'd do it" from Claude was a proposal, not a fait accompli. Temple vetoed plenty of suggestions that sounded clever but didn't fit the project's goals — the decision to stay on `UrlFetchApp` rather than switch to the Advanced Drive Service was a good example.
- **No real-world testing.** All testing was done by Temple, in real Google Drive environments with real Shared Drives, against real file volumes. This matters because Apps Script's behaviour in production is often different from what the docs suggest — the Drive API has subtle quirks around `corpora`, `supportsAllDrives`, and pagination that only surface when you hit them.
- **No secrets or personal data.** Claude has no ongoing access to Temple's Drive, spreadsheets, or Google account. Every piece of data that appeared in the collaboration was pasted in by Temple, reviewed first, and scrubbed of anything private (Drive IDs, internal email addresses) before sharing.
- **No unsolicited feature creep.** The project stayed focused on what Temple actually wanted to build. The Pro features (scheduled snapshots, bulk permission remediation) are documented as planned for the Marketplace edition rather than half-built into the Community edition.

---

## Why Document This?

Two reasons.

First, **transparency.** If someone's going to grant an app full Drive read permissions (see the broad-permissions warning in the README), they deserve to know how the code got written and who was in the room. "A human and two AI tools working together, with the human making the final call on everything" is a more honest answer than pretending any of it was solo work in either direction.

Second, **reproducibility.** This collaborative model is increasingly common but rarely written down. If someone reads this repo and thinks "I could build something like this too" — the answer is yes, and this is roughly how.

---

## Tooling Used

- **Claude** — accessed via [claude.ai](https://claude.ai)
- **Claude Code** — the CLI coding agent from Anthropic, installed via npm
- **Google Apps Script** — the runtime for the actual code
- **Google Drive API v3** — accessed directly via `UrlFetchApp` rather than the Advanced Drive Service
- **openSUSE Tumbleweed** — the development host OS
- **GitHub** — for version control and publishing
