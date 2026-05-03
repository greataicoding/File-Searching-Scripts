#!/usr/bin/env python3
"""
Drive Auditor Icon Generator — Enhanced Edition
================================================

Generates a matching icon set for the Drive File Search & Auditor tool.
Icons match the warm, vintage steampunk postal aesthetic of the Gmail Cleaner.

ENHANCEMENTS:
- Vintage postage stamp edges (scalloped/wavy borders)
- Mechanical detail: rivets, bolts, weathering
- Postal badge variants (circular stamps with text rings)
- Subtle aging effects and shadows for authenticity

The colour palette is extracted from the Gmail Cleaner design system:
- Cream/off-white backgrounds (#F5F1E8, #FBF7F0)
- Warm browns (#8B6F47, #A0826D)
- Steel/mechanical greys (#5A6B78, #7A8A9A)
- Pale blues (#7BA9C8, #9FBFD8)
- Accent reds (#C85A3A)
- Gold accents (#D4AF6F)

Each icon is generated at multiple sizes: 32×32, 48×48, 96×96, 128×128.
Output format: PNG files with transparent backgrounds.

Author: Claude
Date: 2024
"""

from PIL import Image, ImageDraw, ImageFont
import os
import math
from random import random

# ==================== COLOUR PALETTE ====================
# Extracted from the Gmail Cleaner design system — warm, vintage, postal aesthetic.

CREAM_BG = "#FBF7F0"          # Main background — creamy off-white
CREAM_ALT = "#F5F1E8"         # Alternative cream for subtle variations
DARK_TEXT = "#2C2416"         # Deep brown-black for text and outlines
BROWN_MID = "#8B6F47"         # Mid-tone brown — used for shadows and detail
BROWN_DARK = "#6B4E2F"        # Dark brown for strong outlines
STEEL_GREY = "#5A6B78"        # Steel grey — for mechanical parts
STEEL_LIGHT = "#7A8A9A"       # Lighter steel grey
BLUE_PALE = "#7BA9C8"         # Pale blue — mechanical/technical accents
BLUE_LIGHT = "#9FBFD8"        # Lighter pale blue
RED_ACCENT = "#C85A3A"        # Warm rust red — for highlights and warnings
GOLD_ACCENT = "#D4AF6F"       # Warm gold — for decorative elements
TRANSPARENT = (0, 0, 0, 0)    # For alpha channel operations


# ==================== UTILITY FUNCTIONS ====================

def hex_to_rgb(hex_colour):
    """
    Convert a hex colour string to RGB tuple.
    
    Parameters:
        hex_colour (str): Hex colour like "#FBF7F0"
    
    Returns:
        tuple: (R, G, B) values 0-255
    """
    hex_colour = hex_colour.lstrip("#")
    return tuple(int(hex_colour[i:i+2], 16) for i in (0, 2, 4))


def scale_size(base_size, target_size, base_coords):
    """
    Scale drawing coordinates from one size to another.
    Used to maintain proportions when drawing icons at different resolutions.
    
    Parameters:
        base_size (int): Original size (e.g., 128)
        target_size (int): Target size (e.g., 32)
        base_coords (tuple): Original (x, y) coordinate
    
    Returns:
        tuple: Scaled (x, y) coordinate
    """
    scale_factor = target_size / base_size
    return (int(base_coords[0] * scale_factor), int(base_coords[1] * scale_factor))


def draw_rounded_rect(draw, bbox, radius, outline=None, fill=None, width=1):
    """
    Draw a rounded rectangle on a PIL ImageDraw object.
    PIL doesn't have built-in rounded rects, so this approximates with arcs.
    
    Parameters:
        draw: PIL ImageDraw object
        bbox (tuple): Bounding box (x1, y1, x2, y2)
        radius (int): Corner radius in pixels
        outline (str): Outline colour (hex or RGB)
        fill (str): Fill colour (hex or RGB)
        width (int): Outline width
    """
    x1, y1, x2, y2 = bbox
    
    # Draw four corner arcs
    draw.arc([x1, y1, x1 + radius * 2, y1 + radius * 2], 180, 270, outline, width)
    draw.arc([x2 - radius * 2, y1, x2, y1 + radius * 2], 270, 360, outline, width)
    draw.arc([x2 - radius * 2, y2 - radius * 2, x2, y2], 0, 90, outline, width)
    draw.arc([x1, y2 - radius * 2, x1 + radius * 2, y2], 90, 180, outline, width)
    
    # Draw connecting lines
    draw.line([(x1 + radius, y1), (x2 - radius, y1)], outline, width)
    draw.line([(x1 + radius, y2), (x2 - radius, y2)], outline, width)
    draw.line([(x1, y1 + radius), (x1, y2 - radius)], outline, width)
    draw.line([(x2, y1 + radius), (x2, y2 - radius)], outline, width)
    
    # Fill if requested
    if fill:
        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill)
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill)


def draw_circle_outline(draw, xy, radius, outline=None, width=1):
    """
    Draw a circle outline using a bounding box.
    
    Parameters:
        draw: PIL ImageDraw object
        xy (tuple): Center point (x, y)
        radius (int): Radius in pixels
        outline (str): Outline colour
        width (int): Line width
    """
    x, y = xy
    bbox = [x - radius, y - radius, x + radius, y + radius]
    draw.ellipse(bbox, outline=outline, width=width)


def draw_postage_stamp_border(draw, size, indent_size=6):
    """
    Draw a vintage postage stamp scalloped/wavy edge around the entire icon.
    Creates the iconic perforated edge look of old stamps.
    
    Parameters:
        draw: PIL ImageDraw object
        size (int): Canvas size in pixels
        indent_size (int): How deep each scallop indents (larger = more pronounced)
    """
    # Draw scalloped border using circles at the edges — creates the perforated postage stamp look
    step = indent_size * 2  # Distance between scallop centres
    margin = indent_size  # Distance from edge
    
    # Top and bottom edges (horizontal scallops)
    for x in range(0, size, step):
        # Top edge scallops (dent inward) — simulate the tear pattern of old stamps
        draw.ellipse([x, 0, x + indent_size * 2, indent_size * 2],
                    outline=hex_to_rgb(DARK_TEXT), width=1)
        # Bottom edge scallops — same pattern repeated
        draw.ellipse([x, size - indent_size * 2, x + indent_size * 2, size],
                    outline=hex_to_rgb(DARK_TEXT), width=1)
    
    # Left and right edges (vertical scallops)
    for y in range(0, size, step):
        # Left edge scallops — continue the perforated pattern down the sides
        draw.ellipse([0, y, indent_size * 2, y + indent_size * 2],
                    outline=hex_to_rgb(DARK_TEXT), width=1)
        # Right edge scallops — mirror of the left side
        draw.ellipse([size - indent_size * 2, y, size, y + indent_size * 2],
                    outline=hex_to_rgb(DARK_TEXT), width=1)


def draw_rivets(draw, xy_list, rivet_size=3):
    """
    Draw mechanical rivets at specified points.
    Rivets give the icon a steampunk, mechanical appearance — they suggest bolted metal plates.
    
    Parameters:
        draw: PIL ImageDraw object
        xy_list (list): List of (x, y) tuples where rivets should appear
        rivet_size (int): Radius of the rivet circle in pixels
    """
    for x, y in xy_list:
        # Outer rivet circle (grey) — this is the metal head of the rivet
        draw.ellipse([x - rivet_size, y - rivet_size,
                     x + rivet_size, y + rivet_size],
                    fill=hex_to_rgb(STEEL_GREY), outline=hex_to_rgb(DARK_TEXT), width=1)
        
        # Inner highlight (lighter grey) to give 3D effect — simulates light reflection on metal
        # Only draw if highlight size is large enough to be visible
        highlight_size = max(1, rivet_size // 2)
        if rivet_size > 2:  # Only add highlight if rivet is large enough
            draw.ellipse([x - highlight_size + 1, y - highlight_size + 1,
                         x + highlight_size - 1, y + highlight_size - 1],
                        fill=hex_to_rgb(STEEL_LIGHT))


def draw_weathering_marks(draw, size, density=0.03):
    """
    Add subtle weathering/aging marks to give the icon vintage authenticity.
    Draws random small lines and spots to simulate wear and age — as if the stamp has been in a drawer for decades.
    
    Parameters:
        draw: PIL ImageDraw object
        size (int): Canvas size in pixels
        density (float): How many marks (0.0 to 1.0, where 1.0 is very worn)
    """
    import random
    random.seed(42)  # Reproducible results — same seed always makes same marks every time the script runs
    
    # Draw random small wear marks as short lines — simulate creases, folds, and dust
    mark_count = int(size * size * density / 1000)  # Density scales with canvas size
    for _ in range(mark_count):
        x = random.randint(0, size)  # Random x position across the canvas
        y = random.randint(0, size)  # Random y position across the canvas
        length = random.randint(2, 6)  # Mark length in pixels
        angle = random.uniform(0, 2 * math.pi)  # Random direction in any direction
        
        # Calculate endpoint of the wear mark using trigonometry
        x2 = x + int(length * math.cos(angle))
        y2 = y + int(length * math.sin(angle))
        
        # Draw the mark in a muted brown/grey — alternates between brown and steel for variety
        mark_colour = hex_to_rgb(BROWN_MID) if random.choice([True, False]) else hex_to_rgb(STEEL_LIGHT)
        draw.line([(x, y), (x2, y2)], fill=mark_colour, width=1)


def draw_postal_badge_border(draw, size):
    """
    Draw a circular postal badge border (like the Gmail Cleaner stamp badges).
    This creates the "official document" appearance with a decorative circular frame.
    
    Parameters:
        draw: PIL ImageDraw object
        size (int): Canvas size in pixels
    """
    centre = size // 2  # Find the centre point of the canvas
    outer_radius = size // 2 - 3  # Leave small margin so border doesn't touch edge
    inner_radius = outer_radius - 8  # Thickness of the border ring
    
    # Draw outer circle — the perimeter of the badge
    draw.ellipse([centre - outer_radius, centre - outer_radius,
                 centre + outer_radius, centre + outer_radius],
                outline=hex_to_rgb(DARK_TEXT), width=2)
    
    # Draw inner circle to create ring effect — the inner boundary of the decorative ring
    draw.ellipse([centre - inner_radius, centre - inner_radius,
                 centre + inner_radius, centre + inner_radius],
                outline=hex_to_rgb(DARK_TEXT), width=1)
    
    # Draw decorative stars at cardinal points — adds authenticity like the Gmail Cleaner stamps
    star_positions = [
        (centre, centre - outer_radius + 4),  # Top star
        (centre + outer_radius - 4, centre),  # Right star
        (centre, centre + outer_radius - 4),  # Bottom star
        (centre - outer_radius + 4, centre),  # Left star
    ]
    
    for x, y in star_positions:
        # Simple 4-pointed star (a diamond shape)
        star_size = 3
        draw.polygon([(x, y - star_size), (x + star_size, y),
                     (x, y + star_size), (x - star_size, y)],
                    fill=hex_to_rgb(GOLD_ACCENT))


def apply_subtle_shadow(img, shadow_offset=2, shadow_opacity=30):
    """
    Apply a very subtle drop shadow to an icon for depth.
    This simulates a light source and makes icons appear slightly raised off the background.
    
    Parameters:
        img: PIL Image object (RGBA)
        shadow_offset (int): How many pixels to offset the shadow (direction)
        shadow_opacity (int): Shadow darkness (0-255, where 255 is solid black)
    
    Returns:
        Image: A new RGBA image with the shadow applied
    """
    # Create shadow layer — a transparent canvas to draw the shadow on
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    
    # Find all non-transparent pixels and draw slightly offset copies
    pixels = img.load()  # Access image pixels directly
    shadow_pixels = shadow.load()  # Access shadow pixels for modification
    
    # Loop through every pixel in the image
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if pixels[x, y][3] > 200:  # If pixel is mostly opaque (alpha > 200)
                # Add shadow pixel offset down and to the right
                shadow_x = x + shadow_offset  # Offset right
                shadow_y = y + shadow_offset  # Offset down
                if 0 <= shadow_x < shadow.size[0] and 0 <= shadow_y < shadow.size[1]:
                    shadow_pixels[shadow_x, shadow_y] = (0, 0, 0, shadow_opacity)  # Dark, semi-transparent
    
    # Composite: shadow behind original — layer the shadow under the original image
    result = Image.new("RGBA", img.size, (255, 255, 255, 0))
    result.paste(shadow, (0, 0), shadow)  # Paste shadow with its transparency mask
    result.paste(img, (0, 0), img)  # Paste original image on top
    
    return result


# ==================== ICON DRAWING FUNCTIONS ====================
# Each function draws a complete icon at the BASE SIZE (128×128).
# The main export loop will scale these down to 32, 48, 96.


def draw_magnifying_glass_icon(draw, size):
    """
    Draw a magnifying glass searching for files — represents "search" functionality.
    
    Visual: A large magnifying glass lens with binary/file symbols visible through it,
    plus mechanical rivets on the handle for a steampunk look.
    
    Parameters:
        draw: PIL ImageDraw object
        size (int): Canvas size in pixels (typically 128)
    """
    centre_x, centre_y = size / 2, size / 2
    
    # Draw magnifying glass lens (large circle)
    lens_radius = int(size * 0.35)  # Radius of the magnifying glass
    
    # Draw lens outline with thick brown border — gives it substance and weight
    draw_circle_outline(draw, (centre_x - 10, centre_y - 10), lens_radius, 
                       outline=hex_to_rgb(BROWN_DARK), width=4)
    
    # Fill lens with slight tint — the glass colour
    draw.ellipse([centre_x - 10 - lens_radius, centre_y - 10 - lens_radius,
                  centre_x - 10 + lens_radius, centre_y - 10 + lens_radius],
                fill=hex_to_rgb(BLUE_LIGHT), outline=hex_to_rgb(BROWN_DARK), width=2)
    
    # Draw handle (stick extending bottom-right at 45 degrees) — typical magnifying glass handle
    handle_start_x = centre_x - 10 + lens_radius * 0.7
    handle_start_y = centre_y - 10 + lens_radius * 0.7
    handle_end_x = centre_x + 30
    handle_end_y = centre_y + 30
    draw.line([(handle_start_x, handle_start_y), (handle_end_x, handle_end_y)],
             fill=hex_to_rgb(BROWN_DARK), width=5)
    
    # Draw file symbols inside the lens (simple rectangles for "files")
    file_x1 = centre_x - 30
    file_y1 = centre_y - 30
    file_x2 = centre_x - 15
    file_y2 = centre_y - 15
    draw.rectangle([file_x1, file_y1, file_x2, file_y2],
                  outline=hex_to_rgb(DARK_TEXT), width=2)
    
    file_x1 = centre_x - 5
    file_y1 = centre_y - 5
    file_x2 = centre_x + 10
    file_y2 = centre_y + 10
    draw.rectangle([file_x1, file_y1, file_x2, file_y2],
                  outline=hex_to_rgb(DARK_TEXT), width=2)
    
    # Add mechanical rivets along the handle for steampunk aesthetic
    rivet_count = 4  # Number of rivets to place along the handle
    rivet_positions = []
    for i in range(1, rivet_count + 1):
        # Distribute rivets evenly along the handle
        ratio = i / (rivet_count + 1)
        rivet_x = handle_start_x + ratio * (handle_end_x - handle_start_x)
        rivet_y = handle_start_y + ratio * (handle_end_y - handle_start_y)
        rivet_positions.append((int(rivet_x), int(rivet_y)))
    
    # Draw all the rivets
    draw_rivets(draw, rivet_positions, rivet_size=2)


def draw_stacked_folders_icon(draw, size):
    """
    Draw stacked/nested folders — represents "multiple shared drives".
    
    Visual: Three folders overlapping, each slightly offset, with mechanical rivets
    and a postal badge circular frame.
    
    Parameters:
        draw: PIL ImageDraw object
        size (int): Canvas size in pixels
    """
    centre_x, centre_y = size / 2, size / 2
    
    # Draw postal badge background (circular frame)
    draw_postal_badge_border(draw, size)
    
    # Draw three folders, stacked with offset
    folder_width = int(size * 0.35)
    folder_height = int(size * 0.28)
    tab_width = int(folder_width * 0.3)
    tab_height = int(folder_height * 0.2)
    
    # Back folder (darkest)
    x_offset = centre_x - folder_width / 2 - 12
    y_offset = centre_y - folder_height / 2 - 12
    
    # Folder body (rectangle)
    draw.rectangle([x_offset, y_offset + tab_height, 
                   x_offset + folder_width, y_offset + folder_height + tab_height],
                  outline=hex_to_rgb(BROWN_DARK), fill=hex_to_rgb(BROWN_MID), width=2)
    
    # Folder tab (small rectangle on top-left) — the paper tab on the folder
    draw.rectangle([x_offset, y_offset,
                   x_offset + tab_width, y_offset + tab_height],
                  outline=hex_to_rgb(BROWN_DARK), fill=hex_to_rgb(BROWN_DARK), width=1)
    
    # Add rivet to back folder
    draw_rivets(draw, [(x_offset + folder_width * 0.8, y_offset + folder_height * 0.4)], rivet_size=2)
    
    # Middle folder (medium tone)
    x_offset += 15
    y_offset += 15
    
    draw.rectangle([x_offset, y_offset + tab_height,
                   x_offset + folder_width, y_offset + folder_height + tab_height],
                  outline=hex_to_rgb(DARK_TEXT), fill=hex_to_rgb(BROWN_MID), width=2)
    
    draw.rectangle([x_offset, y_offset,
                   x_offset + tab_width, y_offset + tab_height],
                  outline=hex_to_rgb(DARK_TEXT), fill=hex_to_rgb(BROWN_MID), width=1)
    
    # Add rivet to middle folder
    draw_rivets(draw, [(x_offset + folder_width * 0.8, y_offset + folder_height * 0.4)], rivet_size=2)
    
    # Front folder (lightest, highlighted)
    x_offset += 15
    y_offset += 15
    
    draw.rectangle([x_offset, y_offset + tab_height,
                   x_offset + folder_width, y_offset + folder_height + tab_height],
                  outline=hex_to_rgb(DARK_TEXT), fill=hex_to_rgb(BLUE_PALE), width=3)
    
    draw.rectangle([x_offset, y_offset,
                   x_offset + tab_width, y_offset + tab_height],
                  outline=hex_to_rgb(DARK_TEXT), fill=hex_to_rgb(BLUE_PALE), width=1)
    
    # Add rivet to front folder
    draw_rivets(draw, [(x_offset + folder_width * 0.8, y_offset + folder_height * 0.4)], rivet_size=2)


def draw_lock_and_folder_icon(draw, size):
    """
    Draw a lock symbol overlaid on a folder — represents "permissions & security".
    
    Visual: A folder with a small padlock on the bottom-right corner,
    with mechanical rivets for authenticity.
    
    Parameters:
        draw: PIL ImageDraw object
        size (int): Canvas size in pixels
    """
    centre_x, centre_y = size / 2, size / 2
    
    # Draw the folder (simplified)
    folder_width = int(size * 0.45)
    folder_height = int(size * 0.35)
    folder_x = centre_x - folder_width / 2
    folder_y = centre_y - folder_height / 2
    tab_height = int(folder_height * 0.25)
    
    # Folder body
    draw.rectangle([folder_x, folder_y + tab_height,
                   folder_x + folder_width, folder_y + folder_height + tab_height],
                  outline=hex_to_rgb(BROWN_DARK), fill=hex_to_rgb(BROWN_MID), width=3)
    
    # Folder tab
    draw.rectangle([folder_x, folder_y,
                   folder_x + folder_width * 0.4, folder_y + tab_height],
                  outline=hex_to_rgb(BROWN_DARK), fill=hex_to_rgb(BROWN_MID), width=2)
    
    # Add rivets to the folder for mechanical appearance
    rivet_positions = [
        (folder_x + folder_width * 0.25, folder_y + folder_height * 0.2),
        (folder_x + folder_width * 0.75, folder_y + folder_height * 0.7),
    ]
    draw_rivets(draw, rivet_positions, rivet_size=2)
    
    # Draw a padlock on the bottom-right of the folder — represents security/permissions
    lock_x = folder_x + folder_width - 20
    lock_y = folder_y + folder_height
    lock_size = 16
    
    # Lock body (rectangle)
    draw.rectangle([lock_x - lock_size / 3, lock_y - lock_size / 2.5,
                   lock_x + lock_size / 3, lock_y],
                  outline=hex_to_rgb(RED_ACCENT), fill=hex_to_rgb(RED_ACCENT), width=2)
    
    # Lock shackle (arc/circle on top)
    draw.arc([lock_x - lock_size / 2, lock_y - lock_size,
             lock_x + lock_size / 2, lock_y - lock_size / 3],
            0, 180, fill=hex_to_rgb(RED_ACCENT), width=3)
    
    # Keyhole (small circle in centre of lock body) — shows it's a working lock
    keyhole_x, keyhole_y = lock_x, lock_y - lock_size / 4
    draw.ellipse([keyhole_x - 2, keyhole_y - 2, keyhole_x + 2, keyhole_y + 2],
                outline=hex_to_rgb(DARK_TEXT), fill=hex_to_rgb(DARK_TEXT), width=1)


def draw_document_with_checkmark_icon(draw, size):
    """
    Draw a document/file with a checkmark — represents "audit results" or "verified".
    
    Visual: A document (rectangle) with a green checkmark overlaid.
    
    Parameters:
        draw: PIL ImageDraw object
        size (int): Canvas size in pixels
    """
    centre_x, centre_y = size / 2, size / 2
    
    # Draw the document (main rectangle)
    doc_width = int(size * 0.35)
    doc_height = int(size * 0.5)
    doc_x = centre_x - doc_width / 2 - 10
    doc_y = centre_y - doc_height / 2
    
    draw.rectangle([doc_x, doc_y, doc_x + doc_width, doc_y + doc_height],
                  outline=hex_to_rgb(DARK_TEXT), fill=hex_to_rgb(CREAM_BG), width=3)
    
    # Draw horizontal lines on the document (simulating text)
    line_spacing = int(doc_height / 6)
    for i in range(1, 5):
        line_y = doc_y + i * line_spacing
        draw.line([(doc_x + 5, line_y), (doc_x + doc_width - 5, line_y)],
                 fill=hex_to_rgb(BROWN_MID), width=1)
    
    # Draw a large checkmark on the right side (green/accent colour)
    check_centre_x = centre_x + 15
    check_centre_y = centre_y
    check_size = 25
    
    # Checkmark: two diagonal lines forming a tick
    # Short diagonal (left part of the tick)
    draw.line([(check_centre_x - check_size / 2, check_centre_y),
              (check_centre_x - check_size / 4, check_centre_y + check_size / 3)],
             fill=hex_to_rgb(RED_ACCENT), width=4)
    
    # Long diagonal (right part of the tick)
    draw.line([(check_centre_x - check_size / 4, check_centre_y + check_size / 3),
              (check_centre_x + check_size / 2, check_centre_y - check_size / 3)],
             fill=hex_to_rgb(RED_ACCENT), width=4)


def draw_gear_and_document_icon(draw, size):
    """
    Draw a gear overlaid on a document — represents "settings & configuration".
    
    Visual: A document with a mechanical gear symbol overlaid.
    
    Parameters:
        draw: PIL ImageDraw object
        size (int): Canvas size in pixels
    """
    centre_x, centre_y = size / 2, size / 2
    
    # Draw document
    doc_width = int(size * 0.4)
    doc_height = int(size * 0.5)
    doc_x = centre_x - doc_width / 2 - 10
    doc_y = centre_y - doc_height / 2
    
    draw.rectangle([doc_x, doc_y, doc_x + doc_width, doc_y + doc_height],
                  outline=hex_to_rgb(DARK_TEXT), fill=hex_to_rgb(CREAM_BG), width=3)
    
    # Draw text lines on document
    line_spacing = int(doc_height / 6)
    for i in range(1, 5):
        line_y = doc_y + i * line_spacing
        draw.line([(doc_x + 5, line_y), (doc_x + doc_width - 5, line_y)],
                 fill=hex_to_rgb(BROWN_MID), width=1)
    
    # Draw gear on top-right (simplified gear with teeth)
    gear_x = centre_x + 20
    gear_y = centre_y - 15
    gear_radius = 15
    tooth_count = 8
    
    # Draw gear teeth (small circles around the perimeter)
    for i in range(tooth_count):
        angle = (i / tooth_count) * 2 * math.pi
        tooth_x = gear_x + (gear_radius + 4) * math.cos(angle)
        tooth_y = gear_y + (gear_radius + 4) * math.sin(angle)
        draw.ellipse([tooth_x - 3, tooth_y - 3, tooth_x + 3, tooth_y + 3],
                    fill=hex_to_rgb(STEEL_GREY), outline=hex_to_rgb(DARK_TEXT), width=1)
    
    # Draw gear center circle
    draw_circle_outline(draw, (gear_x, gear_y), gear_radius,
                       outline=hex_to_rgb(STEEL_GREY), width=3)
    
    # Gear hub (small centre circle)
    draw.ellipse([gear_x - 5, gear_y - 5, gear_x + 5, gear_y + 5],
                fill=hex_to_rgb(STEEL_GREY), outline=hex_to_rgb(DARK_TEXT), width=1)


def draw_report_with_graph_icon(draw, size):
    """
    Draw a document with a bar graph/chart — represents "reporting & analytics".
    
    Visual: A document with a small bar chart illustration on it.
    
    Parameters:
        draw: PIL ImageDraw object
        size (int): Canvas size in pixels
    """
    centre_x, centre_y = size / 2, size / 2
    
    # Draw document background
    doc_width = int(size * 0.45)
    doc_height = int(size * 0.55)
    doc_x = centre_x - doc_width / 2
    doc_y = centre_y - doc_height / 2
    
    draw.rectangle([doc_x, doc_y, doc_x + doc_width, doc_y + doc_height],
                  outline=hex_to_rgb(DARK_TEXT), fill=hex_to_rgb(CREAM_ALT), width=3)
    
    # Draw a simple bar chart inside the document
    chart_x_start = doc_x + int(doc_width * 0.1)
    chart_y_start = doc_y + int(doc_height * 0.6)
    chart_width = int(doc_width * 0.8)
    chart_height = int(doc_height * 0.3)
    
    # Draw three bars of increasing height
    bar_width = chart_width / 5
    bar_heights = [chart_height * 0.4, chart_height * 0.7, chart_height * 0.9]
    
    for i, bar_height in enumerate(bar_heights):
        bar_x1 = chart_x_start + (i + 1) * bar_width
        bar_y1 = chart_y_start - bar_height
        bar_x2 = bar_x1 + bar_width * 0.6
        bar_y2 = chart_y_start
        
        # Alternate between steel and blue for visual interest
        colour = STEEL_GREY if i % 2 == 0 else BLUE_PALE
        draw.rectangle([bar_x1, bar_y1, bar_x2, bar_y2],
                      outline=hex_to_rgb(DARK_TEXT), fill=hex_to_rgb(colour), width=2)
    
    # Draw chart axis (simple L-shape)
    axis_x = chart_x_start
    axis_y = chart_y_start
    draw.line([(axis_x, axis_y), (axis_x + chart_width, axis_y)],
             fill=hex_to_rgb(DARK_TEXT), width=2)
    draw.line([(axis_x, axis_y), (axis_x, axis_y - chart_height)],
             fill=hex_to_rgb(DARK_TEXT), width=2)


# ==================== ICON EXPORT FUNCTION ====================

def export_icons(output_dir="./drive_auditor_icons"):
    """
    Generate and export all Drive Auditor icons at multiple sizes.
    
    Creates output directory if it doesn't exist and generates PNG files for:
    - 32×32 (toolbar icon)
    - 48×48 (standard icon)
    - 96×96 (high-res thumbnail)
    - 128×128 (primary icon, Marketplace)
    
    Each icon includes:
    - Vintage postage stamp borders (scalloped edges)
    - Mechanical details (rivets, gears)
    - Subtle weathering marks for authenticity
    
    Parameters:
        output_dir (str): Directory path to save generated PNGs
    """
    
    # Create output directory — ensure it exists before we start writing
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"✓ Created output directory: {output_dir}")
    
    # Define all icons to generate — each maps to a drawing function
    icons = {
        "magnifying_glass": draw_magnifying_glass_icon,
        "stacked_folders": draw_stacked_folders_icon,
        "lock_and_folder": draw_lock_and_folder_icon,
        "document_checkmark": draw_document_with_checkmark_icon,
        "gear_and_document": draw_gear_and_document_icon,
        "report_with_graph": draw_report_with_graph_icon,
    }
    
    # Export sizes: (width, height) in pixels — standard icon sizes for different contexts
    sizes = [32, 48, 96, 128]
    
    # Base size for drawing (all icons drawn at this size, then scaled down)
    base_size = 128
    
    # For each icon design...
    for icon_name, draw_function in icons.items():
        print(f"\n📌 Generating: {icon_name}")
        
        # For each target size...
        for target_size in sizes:
            # Create a new image with cream background and transparency support
            img = Image.new("RGBA", (target_size, target_size), hex_to_rgb(CREAM_BG) + (255,))
            draw = ImageDraw.Draw(img)
            
            # Draw the icon itself at the target size
            draw_function(draw, target_size)
            
            # Add vintage postage stamp borders (scalloped/perforated edges)
            # Scale the indent size based on the target size so it looks right at all resolutions
            indent_size = max(3, int(target_size / 20))  # Proportional indent based on size
            draw_postage_stamp_border(draw, target_size, indent_size=indent_size)
            
            # Add subtle weathering marks — gives it an antique stamp appearance
            draw_weathering_marks(draw, target_size, density=0.02)
            
            # Apply a very subtle shadow for depth — makes it appear slightly raised
            img = apply_subtle_shadow(img, shadow_offset=1, shadow_opacity=20)
            
            # Construct filename — includes icon name and size for easy identification
            filename = f"drive_auditor_icon_{icon_name}_{target_size}x{target_size}.png"
            filepath = os.path.join(output_dir, filename)
            
            # Save the PNG — write to disk with all layers and effects
            img.save(filepath)
            print(f"  ✓ Saved: {filename}")
    
    print(f"\n✅ All icons generated and saved to: {output_dir}")
    print(f"   Total files: {len(icons) * len(sizes)} PNG files")
    print(f"   Features: vintage stamp borders, mechanical rivets, weathering effects")


# ==================== MAIN EXECUTION ====================

if __name__ == "__main__":
    print("=" * 60)
    print("Drive Auditor Icon Generator — Enhanced Edition")
    print("=" * 60)
    print("\nGenerating vintage steampunk postal icon set...")
    print("Features: stamp borders, rivets, weathering, shadows\n")
    
    # Export all icons at all sizes to your local folder
    export_icons("/home/temple/Documents/AppsScript/FileSearchScripts/Graphics/")
    
    print("\n" + "=" * 60)
    print("Generation complete!")
    print("=" * 60)
