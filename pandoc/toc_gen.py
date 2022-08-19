#!/usr/bin/env python3
from pathlib import Path
import re
import sys
import logging

## User defined variables ##
upto_level = 2 #show headings up to level 2
output_type = "html"

def html_heading(current_level, level, heading, url):
    if level > current_level:
        print("  "*level + "<ul>" * (level - current_level))
    elif level < current_level:
        print("  "*level + "</ul>" * (current_level - level))
    current_level = level
    if url is None: print(f'{"  "*level}<li>{heading}</li>')
    else: print(f'{"  "*level}<li><a href="{url}">{heading}</a></li>')
    return current_level

def markdown_heading(current_level, level, heading, url):
    print(f'{"  "*level}{"#"*level} [{heading}]({url})')
    return current_level

base = Path("./build/markdown")
chapters = [
    dict(
    name = "Introduction",
    contents = "1_Introduction"
    ),
    dict(
    name = "Background",
    contents = "2_Background"
    ),
    dict(
    name = "Chapter 3: The Long Range Falikov-Kimball Model",
    contents = "3_Long_Range_Falikov_Kimball"
    ),
    dict(
    name = "Chapter 4: The Amorphous Kitaev Model",
    contents = "4_Amorphous_Kitaev_Model",
    ),
    dict(
    name = "Conclusion",
    contents = "5_Conclusion",
    ),
    dict(
    name = "Appendices",
    contents = "6_Appendices",
    )
]

current_level = 0
for chapter in chapters:
    current_level = html_heading(current_level, 1, heading=chapter["name"], url = None)
    chapter_filename = base / chapter["contents"]
    chapter_files = sorted(chapter_filename.glob("*.md"))
    
    for filepath in chapter_files:        
        with open(filepath, 'r') as f:
            for i, line in enumerate(f):
                if line.startswith('#'):
                    try:
                        level, heading = line.split(' ', maxsplit = 1)
                        level = len(level)
                        if level > upto_level: continue # Skip anything lower than this

                        heading = heading.strip()
                        file_url = filepath.parent.relative_to(base) / (filepath.stem + ".html")
                        url_id = heading.lower().replace(" ", "-")
                        url = f"./{file_url}#{url_id}"
                        
                        if output_type == "markdown":
                            current_level = markdown_heading(current_level, level+1, heading, url)
                        elif output_type == "html":
                            current_level = html_heading(current_level, level+1, heading, url)
                        else: 
                            sys.exit()
                    except Exception as e:
                        logging.warning(f"Exception {e} on line {i} of {filepath}: {line}")