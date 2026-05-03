# Drive Auditor Icon Set — Enhanced Edition

## Overview

A complete icon set for the **Drive File Search & Auditor** Google Workspace add-on, designed in the warm, vintage steampunk postal aesthetic matching the **Gmail Cleaner** visual language.

**24 PNG files** — 6 icon designs × 4 sizes (32×32, 48×48, 96×96, 128×128)

---

## Icon Designs

### 1. **Magnifying Glass** (`magnifying_glass`)
- **Purpose**: Search & discovery functionality
- **Visual**: Large magnifying glass lens with file symbols visible inside
- **Details**: Mechanical rivets along the handle for steampunk authenticity
- **Use**: Search interface, toolbar icon

### 2. **Stacked Folders** (`stacked_folders`)
- **Purpose**: Multiple shared drives / cross-drive searching
- **Visual**: Three overlapping folders in brown and blue tones
- **Details**: 
  - Postal badge circular frame (like the Gmail Cleaner stamps)
  - Decorative stars at cardinal points
  - Mechanical rivets on each folder
- **Use**: Multi-drive search, folder browser

### 3. **Lock & Folder** (`lock_and_folder`)
- **Purpose**: Permissions & security auditing
- **Visual**: Folder with a red padlock overlay
- **Details**:
  - Red accent padlock with keyhole
  - Mechanical rivets showing bolted construction
- **Use**: Security/permissions features, settings

### 4. **Document Checkmark** (`document_checkmark`)
- **Purpose**: Audit results / verification
- **Visual**: Document with a large red checkmark
- **Details**:
  - Text lines simulating document content
  - Bold checkmark for clear verification status
- **Use**: Results display, confirmation screens

### 5. **Gear & Document** (`gear_and_document`)
- **Purpose**: Settings & configuration
- **Visual**: Document with mechanical gear overlay
- **Details**:
  - 8-tooth mechanical gear (steampunk aesthetic)
  - Gear hub with metallic finish
- **Use**: Settings, configuration, preferences

### 6. **Report with Graph** (`report_with_graph`)
- **Purpose**: Analytics & reporting
- **Visual**: Document with bar chart illustration
- **Details**:
  - Three bars of increasing height (upward trend)
  - Axes showing coordinate system
- **Use**: Reports, analytics, data visualization

---

## Visual Enhancements

### ✓ Vintage Postage Stamp Borders
- **Scalloped/perforated edges** around every icon — the iconic postal stamp look
- Creates visual consistency with the Gmail Cleaner aesthetic
- Dynamically sized based on icon resolution

### ✓ Mechanical Rivets
- **Steel grey rivets with 3D highlights** placed on folders, handles, and structural elements
- Rivet size adapts to the icon's overall size
- Reinforces the steampunk, bolted-construction theme

### ✓ Subtle Weathering Marks
- **Random wear lines and marks** simulating age and authenticity
- Uses a fixed random seed for **reproducible results** — every generation creates identical weathering
- Adds vintage patina without overwhelming the design

### ✓ Drop Shadows
- **Subtle shadows** offset down and right
- Very low opacity (20/255) for depth without harshness
- Makes icons appear slightly raised off the background

---

## Colour Palette

All icons use this warm, vintage steampunk palette (extracted from Gmail Cleaner):

| Colour | Hex | Usage |
|--------|-----|-------|
| Cream Background | `#FBF7F0` | Primary background |
| Cream Alt | `#F5F1E8` | Subtle variations |
| Dark Text | `#2C2416` | Outlines, strong contrast |
| Brown Mid | `#8B6F47` | Shadows, mid-tones |
| Brown Dark | `#6B4E2F` | Strong outlines, depth |
| Steel Grey | `#5A6B78` | Mechanical parts, rivets |
| Steel Light | `#7A8A9A` | Highlights, reflection |
| Blue Pale | `#7BA9C8` | Technical accents, highlights |
| Blue Light | `#9FBFD8` | Lighter accents |
| Red Accent | `#C85A3A` | Warnings, locks, checkmarks |
| Gold Accent | `#D4AF6F` | Decorative elements, stars |

---

## File Sizes

Generated at multiple resolutions:

| Size | Use Case | Typical File Size |
|------|----------|-------------------|
| 32×32 | Toolbar icons, small UI elements | ~200–300 bytes |
| 48×48 | Standard menu icons | ~250–400 bytes |
| 96×96 | High-res thumbnails, preview panes | ~500–800 bytes |
| 128×128 | Marketplace listings, primary icon | ~700–1600 bytes |

---

## Technical Details

### Generated With
- **Python 3** + **PIL/Pillow** (image processing)
- **Mathematical precision** for consistent sizing across all resolutions
- **Procedural generation** — no raster scaling, all drawn at target size

### Quality Assurance
- ✓ Transparent backgrounds (RGBA format)
- ✓ Crisp anti-aliasing at small sizes
- ✓ Consistent proportions across all scales
- ✓ Reproducible generation (same seed = identical results)

---

## Usage

### For Google Workspace Marketplace

1. **Main Icon (128×128)**
   - Use `drive_auditor_icon_stacked_folders_128x128.png` as the primary marketplace icon
   - Or choose another design that best represents your primary feature

2. **Toolbar Icons (32×32, 48×48)**
   - Use different icons for different features (search, audit, report, settings)
   - Icons scale cleanly at small sizes thanks to the perforated borders

3. **Banners & Headers**
   - Can be combined with text or used as header backgrounds
   - The cream background integrates seamlessly with vintage-themed UIs

### Within Your Google Sheet

- Insert icons into custom menus using `SpreadsheetApp.getUi().createAddonMenu()`
- Use 32×32 or 48×48 for button icons
- Use 96×96 or 128×128 for splash screens or about dialogs

---

## Customization

The script is **fully commented** and modular. To modify the icons:

1. **Change colours**: Edit the `CREAM_BG`, `BROWN_DARK`, `STEEL_GREY`, etc. hex values at the top
2. **Adjust details**: Increase/decrease rivet density, weathering marks, or shadow intensity
3. **Add new icons**: Create a new `draw_your_icon(draw, size)` function and add it to the `icons` dictionary
4. **Resize**: Icons are drawn at the target size directly — no quality loss at any resolution

### Running the Script

```bash
python3 drive_auditor_icon_generator.py
```

The script will:
- Auto-create the output directory if it doesn't exist
- Generate all 24 PNG files
- Print progress for each icon and size
- Report total file count and feature summary

---

## Design Philosophy

These icons embody the **"postal auditor" theme**:
- **Vintage aesthetic** — old office, archival, vintage postage stamps
- **Mechanical detail** — steampunk rivets and gears (suggesting precision and engineering)
- **Authenticity** — weathering marks simulate aged documents
- **Clear symbolism** — each icon's purpose is immediately recognizable

The design is **professional yet approachable**, making the Drive Auditor feel like a trusted tool for managing Google Workspace security.

---

## Version History

**v2.0 — Enhanced Edition (2024-04-27)**
- ✨ Added vintage postage stamp borders (scalloped edges)
- ✨ Integrated mechanical rivets for steampunk aesthetic
- ✨ Included subtle weathering marks for authenticity
- ✨ Applied drop shadows for depth
- 🎨 Postal badge circular frames on multi-icon designs
- 🐛 Fixed rivet rendering at small sizes
- 📝 Fully commented code (every line explains its intent)

**v1.0 — Initial Release (2024-04-26)**
- 6 icon designs at 4 sizes
- Basic warm/cool colour palette
- Minimal mechanical details

---

## License & Attribution

These icons were generated using a custom Python script matching the visual language of the **Gmail Cleaner** add-on.

Feel free to:
- ✓ Use in your Google Workspace Marketplace add-on
- ✓ Modify the script to suit your needs
- ✓ Share the generator script with your team

---

## Support

If you need to:
- **Regenerate icons**: Run the Python script with your preferred output directory
- **Modify specific icons**: Edit the corresponding `draw_*_icon()` function
- **Create new designs**: Copy an existing icon function and adapt it

The script is designed to be maintainable and easy to understand — every function has detailed comments explaining what it does and why.

---

**Generated by**: Drive Auditor Icon Generator (Enhanced Edition)  
**Date**: 2024-04-27  
**Output Directory**: `/home/temple/Documents/AppsScript/FileSearchScripts/Graphics/`
