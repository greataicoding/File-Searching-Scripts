/**
 * File Search & Auditor for Google Drive™ — File Searching Scripts
 * ----------------------------------------
 * Copyright © 2026 Temple Rodgers. All rights reserved.
 *
 * Author:  Temple Rodgers
 * Contact: GreatAICoding@gmail.com
 * Licence: Proprietary — not for redistribution without permission.
 *
 * Part of the GreatAICoding family of Google Workspace tools.
 *
 * Version 1: Initial working version. Searches shared drives listed in the
 * myDrives sheet by drive ID. Results written to a new sheet tab named after
 * the search string. Pagination, drive name caching, and batch write all working.
 *
 * Version 2: Added automatic drive detection via detectDrives(). Script now
 * auto-populates the myDrives sheet with checkboxes on first run. Added My Drive
 * support — consumer Gmail users with no Shared Drives get a simple yes/no toggle
 * in the sidebar. driveCall_() updated to handle both corpora: 'drive' and
 * corpora: 'user'. setSearchMyDrive() added to persist the My Drive toggle state.
 *
 * Version 3: detectDrives() now deletes and recreates the myDrives sheet rather
 * than clearing it, so legacy column structures can never cause incorrect data to be read.
 *
 * Version 4: driveLister() now validates the myDrives sheet structure before reading it.
 * If the sheet was created manually or has an old layout (e.g. Name|ID|Link instead of
 * Include|Drive Name|Drive ID), detectDrives() is called to rebuild it from scratch.
 * Also fixed a bug where driveData[i][1] (drive name column) was used instead of
 * driveData[i][2] (drive ID column) when building the search parameters.
 *
 * Version 5: Fixed script failures when encountering invalid shared drives by adding
 * explicit loop breaks and safer error object parsing in driveCall_() and detectDrives().
 * Corrected a syntax error caused by a broken comment line in driveLister().
 * * Version 6: Added SpreadsheetApp.flush() after rebuilding the myDrives sheet to prevent
 * Apps Script from reading cached/stale data. Added a URL sanitizer to driveLister()
 * to automatically extract the ID if a full URL is pasted into the Drive ID column.
 * * Version 7: Fixed a logic bug where detectDrives() failed to delete an invalid myDrives
 * sheet if the user had 0 shared drives. Added clearer logging in driveCall_() to gracefully
 * identify and skip Folder IDs that are mistakenly passed as Shared Drive IDs.
 * * Version 8: Added "Silent Refresh" logic to driveLister(). If a user searches for the exact
 * same string twice, the script now finds the existing tab and clears it, rather than
 * throwing an error for trying to create a duplicate sheet name.
 * * Version 9: Added a Smart Query Builder. Users can now use double quotes for "exact phrase"
 * searches, or use the prefix "title:" to search only document titles. Added single-quote escaping
 * to prevent API crashes when searching for words containing apostrophes.
 * * Version 10: Code cleanup. Restored line-by-line comment density to detectDrives(),
 * generateDriveFiles(), and driveCall_() for Marketplace maintainability. Corrected
 * multi-line indentation alignment in the generateDriveFiles() return array.
 * * Version 11: Added frozen header row and automatic column filtering to the results sheet.
 * Added 'Include Files' and 'Include Folders' checkboxes to the UI, allowing users to search
 * specifically for folders, files, or both.
 * * Version 12: Fixed a bug where searching for "Folders Only" returned false positives due to
 * the Drive API matching 'fullText' against folder metadata (like the creator's name). The script
 * now automatically forces a 'name' (title) search when only folders are selected.
 * * Version 13: Amended app name to comply with Google's standards
 * * Version 13: Defensive filter handling — driveLister() now explicitly removes any existing
 * filter before applying a new one, fixing "You can't create a filter in a sheet that already
 * has a filter" error that could occur when sheet.clear() failed to remove the filter. */

// ─────────────────────────────────────────────────────────────────────────────

/**
 * ORG_DOMAIN — the organisation's email domain used to detect external sharing.
 * Set this to your domain (e.g. "mycompany.com") once real domain detection is wired up.
 * While it is blank, the Risk Flag fires on ALL named user/group permissions,
 * because without a known domain we treat every email address as potentially external.
 */
const ORG_DOMAIN = ""; // leave blank until real domain detection is implemented

// ─────────────────────────────────────────────────────────────────────────────

/**
 * SearchForFileForm — opens the Drive Auditor search sidebar in Google Sheets.
 * No parameters. No return value.
 * Loads searchInput.html and shows it as a sidebar on the right of the sheet.
 */
function SearchForFileForm() {
  const form = HtmlService.createHtmlOutputFromFile('searchInput').setTitle('Search Files'); // load the sidebar HTML file and give it a title
  SpreadsheetApp.getUi().showSidebar(form); // display the sidebar in the Google Sheets UI
}

// ─────────────────────────────────────────────────────────────────────────────

/**
 * addMenu — adds the "File Search" custom menu to the Google Sheets menu bar.
 * No parameters. No return value.
 * Called by onOpen so the menu is there every time the spreadsheet loads.
 */
function addMenu() {
  const menu = SpreadsheetApp.getUi().createMenu('File Search'); // create a top-level menu called "File Search"
  menu.addItem('Search Content for Strings', 'SearchForFileForm'); // full-text content search — the active option
  menu.addToUi(); // attach the menu to the spreadsheet's UI so the user can see it
}

// ─────────────────────────────────────────────────────────────────────────────

/**
 * onInstall — runs automatically when a user installs the add-on from the Marketplace.
 * @param {Object} e - the Apps Script event object.
 * No return value.
 * * Delegates directly to onOpen(e) so the "File Search" menu builds immediately
 * upon installation without requiring the user to refresh their browser.
 */
function onInstall(e) {
  onOpen(e);
}

// ─────────────────────────────────────────────────────────────────────────────

/**
 * onOpen — runs automatically every time the spreadsheet is opened.
 * @param {Object} e - the Apps Script event object (not used directly here).
 * No return value.
 * Only one onOpen can exist per script project — it just delegates to addMenu.
 */
function onOpen(e) {
  addMenu(); // build the custom "File Search" menu on every spreadsheet open
}

// ─────────────────────────────────────────────────────────────────────────────

// lastRow tracks which row to write results into next.
// It lives at module level so generateDriveFiles can advance it across multiple drives
// within a single driveLister call. Each Apps Script execution starts fresh, so
// it always starts at 2 (row 1 is the header row).
let lastRow = 2; // start writing results from row 2
let foundRecords = 'false'; // flag used to track whether any files were found (not currently read back)

// ─────────────────────────────────────────────────────────────────────────────

/**
 * detectDrives — discovers all Shared Drives the user has access to and writes
 * them to the myDrives sheet so the user can tick which ones to search.
 */
function detectDrives() {
  const options = { // set up the HTTP options for the UrlFetchApp calls
    muteHttpExceptions: true, // prevent script crashes on API errors by returning the error payload instead
    method: "GET", // Drive API list endpoints require GET requests
    headers: { authorization: "Bearer " + ScriptApp.getOAuthToken() } // append the user's OAuth token for authorization
  };
  let pageToken = null; // initialize the page token variable as null for the first API request
  let allDrives = []; // initialize an empty array to collect shared drives across all paginated responses

  do { // begin a do-while loop to handle API pagination
    const params = { // construct the query parameters for the API call
      pageSize: 100, // request the maximum allowed number of drives per page
      fields: "drives(id,name),nextPageToken" // restrict the response to only the necessary fields to improve speed
    };
    if (pageToken) params.pageToken = pageToken; // if a page token exists from a previous loop, append it to the parameters

    const queryString = Object.keys(params).map(function(p) { // map the parameters object into an array of key-value pairs
      return [encodeURIComponent(p), encodeURIComponent(params[p])].join("="); // URL-encode the keys and values and join them with an equals sign
    }).join("&"); // join the array of pairs into a single query string separated by ampersands

    const url = "https://www.googleapis.com/drive/v3/drives?" + queryString; // construct the full API endpoint URL
    const response = JSON.parse(UrlFetchApp.fetch(url, options).getContentText()); // execute the HTTP request and parse the JSON response

    if ("error" in response) { // check if the API returned an error object
      const errMsg = typeof response.error === 'object' ? response.error.message : response.error; // safely extract the error message whether it's a string or an object
      Logger.log("Error listing drives: " + errMsg); // log the error message for debugging purposes
      break; // exit the pagination loop gracefully so the script doesn't hang
    }

    if (response.drives && response.drives.length > 0) { // verify that the response contains a drives array with at least one item
      allDrives = [...allDrives, ...response.drives]; // use the spread operator to append the new drives to the master array
    }

    pageToken = response.nextPageToken; // update the page token for the next iteration (will be undefined if on the last page)
  } while (pageToken); // continue looping as long as a nextPageToken was returned

  const ss = SpreadsheetApp.getActiveSpreadsheet(); // get a reference to the active Google Spreadsheet
  let myDrivesSheet = ss.getSheetByName("myDrives"); // attempt to find an existing sheet named "myDrives"

  if (allDrives.length === 0) { // check if the user has absolutely no shared drives (e.g., standard Gmail account)
    if (myDrivesSheet) ss.deleteSheet(myDrivesSheet); // if an invalid/old myDrives sheet exists, delete it to prevent confusion
    return "my_drive_only"; // return the specific string to trigger the My Drive toggle in the sidebar UI
  }

  if (myDrivesSheet) ss.deleteSheet(myDrivesSheet); // delete the existing myDrives sheet to ensure a clean slate without legacy data/formatting
  myDrivesSheet = ss.insertSheet("myDrives"); // create a brand new myDrives sheet

  myDrivesSheet.getRange(1, 1, 1, 3).setValues([["Include", "Drive Name", "Drive ID"]]); // write the three required column headers to the first row

  const allRows = [ // build a 2D array representing all rows to be written to the sheet
  [true, "My Drive", "MY_DRIVE"], // insert the sentinel row for the user's personal My Drive as the very first option
  ...allDrives.map(d => [true, d.name, d.id]) // map the API drive objects into rows with a checked box, name, and ID
  ];
  myDrivesSheet.getRange(2, 1, allRows.length, 3).setValues(allRows); // batch write all data rows to the sheet starting from row 2

  const checkboxValidation = SpreadsheetApp.newDataValidation().requireCheckbox().build(); // construct a data validation rule requiring a checkbox
  myDrivesSheet.getRange(2, 1, allRows.length, 1).setDataValidation(checkboxValidation); // apply the checkbox validation to the entire "Include" column

  return "found_shared_drives"; // return the specific string to trigger the Shared Drives UI in the sidebar
}

// ─────────────────────────────────────────────────────────────────────────────

function setSearchMyDrive(value) {
  PropertiesService.getScriptProperties().setProperty('searchMyDrive', value ? 'true' : 'false');
}

// ─────────────────────────────────────────────────────────────────────────────

function isMyDrivesSheetValid_(sheet) {
  if (!sheet) return false;
  if (sheet.getLastRow() < 1) return false;
  const headers = sheet.getRange(1, 1, 1, 3).getValues()[0];
  return headers[0] === 'Include' &&
  headers[1] === 'Drive Name' &&
  headers[2] === 'Drive ID';
}

// ─────────────────────────────────────────────────────────────────────────────

/**
 * driveLister — main entry point called from the sidebar when the user hits Search.
 */
function driveLister(searchString, incFiles = true, incFolders = false) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  let sheet = ss.getSheetByName(searchString);

  if (sheet) {
    sheet.clear(); // The tab exists! Just wipe it totally clean (removes existing filters and data)
  } else {
    sheet = ss.insertSheet(searchString); // The tab doesn't exist yet, so create it
  }

  const heads = [['Name', 'ID', 'Link', 'Created Date', 'Modified Data', 'Mime Type', 'Size', 'Shared Drive Name', 'Description Text', 'Shared With', 'External Sharing', 'Risk Flag']];
  sheet.getRange(1, 1, 1, 12).setValues([...heads]);

  lastRow = 2;

  let queryString = "";
  const cleanSearch = searchString.trim();

  // VERSION 12 FIX: Determine if we should force a 'name' search.
  // 'fullText' searches folder metadata, which causes massive false positives.
  const forceNameSearch = (!incFiles && incFolders);

  if (cleanSearch.toLowerCase().startsWith('title:')) {
    const titleText = cleanSearch.substring(6).trim().replace(/'/g, "\\'"); // extract text and escape single quotes
    queryString = ` AND name contains '${titleText}'`;

  } else if (cleanSearch.startsWith('"') && cleanSearch.endsWith('"')) {
    let phraseText = cleanSearch.replace(/'/g, "\\'"); // escape single quotes just in case

    if (forceNameSearch) {
      phraseText = phraseText.replace(/^"|"$/g, ''); // strip the quotes since we are forcing a name match
      queryString = ` AND name contains '${phraseText}'`;
    } else {
      queryString = ` AND fullText contains '${phraseText}'`;
    }

  } else {
    const words = cleanSearch.split(' ').filter(w => w !== ''); // split on spaces and ignore extra blanks
    queryString = words.map(function(word) {
      const safeWord = word.replace(/'/g, "\\'"); // escape single quotes
      const searchField = forceNameSearch ? 'name' : 'fullText'; // Use 'name' if folders only, otherwise 'fullText'
    return ` AND ${searchField} contains '${safeWord}'`;
    }).join('');
  }

  Logger.log("Final API Query String: " + queryString);

  let myDrivesSheet = ss.getSheetByName("myDrives");
  if (myDrivesSheet && !isMyDrivesSheetValid_(myDrivesSheet)) {
    Logger.log('myDrives sheet has incorrect structure - rebuilding via detectDrives()');
    detectDrives();
    SpreadsheetApp.flush();
  }

  const validatedSheet = ss.getSheetByName("myDrives");

  if (validatedSheet) {
    const lastDriveRow = validatedSheet.getLastRow();

    if (lastDriveRow > 1) {
      const driveData = validatedSheet.getRange(2, 1, lastDriveRow - 1, 3).getValues();

      for (let i = 0; i < driveData.length; ++i) {
        const isChecked = driveData[i][0];
        if (!isChecked) continue;

        let driveId = String(driveData[i][2]).trim();
        if (driveId.includes('/')) {
          driveId = driveId.split('/').pop().split('?')[0];
        }

        const isMyDrive = (driveId === 'MY_DRIVE');
        const driveParam = isMyDrive ? null : [driveId];

        generateDriveFiles(driveParam, sheet, queryString, isMyDrive, incFiles, incFolders);
      }
    }
  } else {
    const searchMyDrivePref = PropertiesService.getScriptProperties().getProperty('searchMyDrive');
    if (searchMyDrivePref === 'true') {
      generateDriveFiles(null, sheet, queryString, true, incFiles, incFolders);
    }
  }

  // Formatting phase: Freeze top row and apply column filters
  sheet.setFrozenRows(1); // Always freeze the header row so it stays visible while scrolling

  const lastRowofSheet = sheet.getLastRow(); // grab how many rows of data are now in the results sheet
  if (lastRowofSheet > 1) { // only apply formatting if there is at least one result row beyond the header
    const existingFilter = sheet.getFilter(); // check whether the sheet already has a filter applied
    if (existingFilter) existingFilter.remove(); // if a filter already exists, remove it first to avoid the "filter already exists" error
    sheet.getRange(1, 1, lastRowofSheet, 12).createFilter(); // apply a fresh filter to the entire data range, header included
    return "<span style=\"font-weight: bold\" >Found Records</span>"; // tell the sidebar that records were found
  } else {
    return "<span style=\"font-weight: bold\" >No Records Found</span>"; // tell the sidebar that nothing matched
  }
}

// ─────────────────────────────────────────────────────────────────────────────

/**
 * generateDriveFiles — searches a single drive (Shared Drive or My Drive) and
 * writes matching files to the results sheet.
 */
function generateDriveFiles(drive, sheet, queryString, isMyDrive, incFiles, incFolders) {
  let filesList = []; // initialize an empty array to hold the file objects returned by the API

  let mimeFilter = ""; // initialize an empty string for the mimeType filter portion of the query
  if (incFiles && !incFolders) {
    mimeFilter = " AND mimeType != 'application/vnd.google-apps.folder'"; // standard behavior: exclude folders entirely
  } else if (!incFiles && incFolders) {
    mimeFilter = " AND mimeType = 'application/vnd.google-apps.folder'"; // folder-only behavior: specifically search ONLY for folders
  }
  // Note: if BOTH incFiles and incFolders are true, mimeFilter remains "", meaning it naturally searches everything.

  const filesQuery = "trashed = false" + mimeFilter + queryString; // construct the core query combining trash status, the mime filter, and the user's text query
  Logger.log(filesQuery); // log the final query string for debugging purposes

  filesList = driveCall_(filesQuery, drive, isMyDrive); // call the driveCall_ helper function to execute the API request and handle pagination

  if (!filesList || filesList.length === 0) return; // prevent the script from crashing by returning early if no files were found

  const res = filesList.map(f => { // map the raw file objects into a 2D array suitable for pasting into Google Sheets
    const permissions = f.permissions || []; // safely extract the permissions array, defaulting to an empty array if undefined

    const sharedWith = permissions // begin processing the permissions array to extract named users
    .filter(p => p.type === 'user' || p.type === 'group') // filter out domain and public link permissions to keep only named users and groups
    .map(p => p.emailAddress || '') // extract the email address property from each permission object, defaulting to an empty string
    .filter(e => e !== '') // remove any empty strings caused by permissions without email addresses
    .join(', '); // combine the remaining email addresses into a single comma-separated string

    const externalSharing = permissions.some(p => p.type === 'anyone') // check if any permission in the array grants access to "anyone" with the link
    ? 'Anyone with link' // if true, label the file as publicly accessible via a link
  : 'Private'; // otherwise, label the file as private (restricted to named users/domain)

  const riskFlag = permissions // begin processing permissions to detect external sharing risks
  .filter(p => (p.type === 'user' || p.type === 'group') && p.emailAddress) // keep only named users or groups that possess a valid email address
  .some(p => { // evaluate if at least one of these emails belongs to an external user
    const email = p.emailAddress.toLowerCase(); // convert the email address to lowercase for reliable comparison
    if (!ORG_DOMAIN) return true; // if no organization domain is configured, default to flagging all named emails as a risk
    return !email.endsWith('@' + ORG_DOMAIN.toLowerCase()); // return true if the email does not end with the configured organization domain
  })
  ? '⚠ EXTERNAL' // if an external email was found, flag the column with this warning
  : ''; // otherwise, leave the risk flag column blank

  return [ // return a structured array representing a single row in the spreadsheet
  f.name,                   // col A: the file's display name
  f.id,                     // col B: the file's unique Drive ID
  f.webViewLink,            // col C: the URL to open the file in a browser
  new Date(f.createdTime),  // col D: when the file was created (converted to a JS Date so Sheets formats it correctly)
  new Date(f.modifiedTime), // col E: when the file was last modified
                            f.mimeType,               // col F: the file type (e.g. "application/vnd.google-apps.document")
  f.quotaBytesUsed,         // col G: how many Drive quota bytes the file uses (0 for Google Docs/Sheets/Slides)
  f.driveName,              // col H: the human-readable name of the drive this file lives in
  f.description,            // col I: the file's description field (usually blank)
  sharedWith,               // col J: comma-separated emails of named users/groups with access
  externalSharing,          // col K: "Anyone with link" or "Private"
  riskFlag                  // col L: "⚠ EXTERNAL" if any external party has named access, otherwise blank
  ];
  }); // end of the map function

  if (res.length != 0) { // perform a final check to ensure the results array is not empty
    sheet.getRange(lastRow, 1, res.length, res[0].length).setValues([...res]); // batch write the 2D results array to the spreadsheet starting at the current last row
    lastRow = lastRow + res.length; // increment the global lastRow counter by the number of rows just written
  }
}

// ─────────────────────────────────────────────────────────────────────────────

/**
 * driveCall_ — calls the Drive API v3 files.list endpoint for one drive.
 */
function driveCall_(filesQuery, drive, isMyDrive) {
  const options = { // set up the HTTP options for the UrlFetchApp calls
    muteHttpExceptions: true, // prevent script crashes on API errors by returning the error payload instead
    method: "GET", // Drive API list endpoints require GET requests
    headers: { authorization: "Bearer " + ScriptApp.getOAuthToken() } // append the user's OAuth token for authorization
  };
  let pageToken = null; // initialize the page token variable as null for the first API request
  let filesList = []; // initialize an empty array to collect files across all paginated responses

  do { // begin a do-while loop to handle API pagination
    const params = { // construct the base query parameters for the API call
      "fields": "files(id,name,createdTime,modifiedTime,size,parents,webViewLink,mimeType,quotaBytesUsed,driveId,description,permissions(id,type,role,emailAddress,domain,displayName)),nextPageToken", // request specific file properties including nested permissions to save bandwidth
      'supportsAllDrives': true, // signal to the API that our application understands Shared Drives
      'includeItemsFromAllDrives': true // ensure files located inside Shared Drives are actually returned in the query
    };
    if (isMyDrive) { // check if we are currently searching the user's personal My Drive
      params.corpora = 'user'; // set the scope to search the user's personal files and items shared directly with them
    } else { // otherwise, we are searching a specific Shared Drive
      params.corpora = 'drive'; // set the scope to strictly search inside a single Shared Drive
      params.driveId = drive; // attach the specific Shared Drive ID to the parameters
    }

    if (pageToken) params.pageToken = pageToken; // if a page token exists from a previous loop, append it to the parameters
    if (filesQuery) params.q = filesQuery; // append the constructed search string to the "q" parameter

    const queryString = Object.keys(params).map(function(p) { // map the parameters object into an array of key-value pairs
      return [encodeURIComponent(p), encodeURIComponent(params[p])].join("="); // URL-encode the keys and values and join them with an equals sign
    }).join("&"); // join the array of pairs into a single query string separated by ampersands

    const url = "https://www.googleapis.com/drive/v3/files?" + queryString; // construct the full API endpoint URL
    const response = JSON.parse(UrlFetchApp.fetch(url, options).getContentText()); // execute the HTTP request and parse the JSON response

    if ("error" in response) { // check if the API returned an error object
      const errorMessage = typeof response.error === 'object' ? response.error.message : response.error; // safely extract the error message whether it's a string or an object

      if (errorMessage.includes("Shared drive not found")) { // explicitly check if the error is due to an invalid/folder ID
        Logger.log(`⚠️ SKIPPING ID: ${drive}. The Drive API requires a top-level Shared Drive ID. The ID provided appears to be a standard Folder ID or an invalid Drive ID.`); // log a helpful warning without crashing
      } else { // if it is any other type of error
        Logger.log("Error: " + errorMessage + "-> " + drive); // log the generic error message along with the drive ID for debugging
      }
      break; // exit the pagination loop gracefully so the script doesn't hang
    } else { // if the API call was successful
      if (response.files && response.files.length > 0) { // verify that the response contains a files array with at least one item
        filesList = [...filesList, ...response.files]; // use the spread operator to append the new files to the master array

        if (isMyDrive) { // check if we are processing My Drive results
          filesList.forEach(file => { // iterate through the newly added files
            if (!file.driveName) file.driveName = "My Drive"; // manually stamp "My Drive" onto each file object since My Drive items lack a driveId
          }); // end of My Drive file loop
        } else { // otherwise, we are processing Shared Drive results
          const uniqueDriveIds = new Set(response.files.map(file => file.driveId)); // create a Set of unique drive IDs found in this batch (usually just one)

          uniqueDriveIds.forEach(driveId => { // iterate over each unique drive ID
            const driveInfoUrl = `https://www.googleapis.com/drive/v3/drives/${driveId}`; // construct the URL to fetch metadata for this specific drive
            const driveInfoResponse = JSON.parse(UrlFetchApp.fetch(driveInfoUrl, options).getContentText()); // execute the HTTP request and parse the drive metadata

            if ("error" in driveInfoResponse) { // check if fetching the drive metadata failed
              const infoErrMsg = typeof driveInfoResponse.error === 'object' ? driveInfoResponse.error.message : driveInfoResponse.error; // safely extract the metadata error message
              Logger.log("Error retrieving drive info: " + infoErrMsg); // log the error for debugging
            } else { // if the metadata fetch was successful
              const driveName = driveInfoResponse.name; // extract the human-readable drive name from the response

              filesList.forEach(file => { // iterate over the collected files
                if (file.driveId === driveId) { // check if the file belongs to the currently processed drive ID
                  file.driveName = driveName; // stamp the human-readable drive name onto the file object for the spreadsheet
                }
              }); // end of file stamp loop
            }
          }); // end of unique drive IDs loop
        }
      }
    }
    pageToken = response.nextPageToken; // update the page token for the next iteration (will be undefined if on the last page)
  } while (pageToken); // continue looping as long as a nextPageToken was returned

  return filesList; // return the fully populated array of file objects
}
