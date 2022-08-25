#!/usr/bin/env python3
from pathlib import Path
import re
import sys
import logging

## User defined variables ##
upto_level = 1 #show headings up to level 2
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

def emit_heading(current_level, level, heading, url, format):
    func = dict(html = html_heading, markdown = markdown_heading)[format]
    return func(current_level, level, heading, url)

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

pattern = re.compile(r"(#+)\s+([^{]+)\s*?(\{#sec:[^}]+\})?")

current_level = 0
for chapter in chapters:
    chapter_filename = base / chapter["contents"]
    chapter_files = sorted(chapter_filename.glob("*.md"))
    first_thing_in_chapter = True
    
    for filepath in chapter_files:        
        with open(filepath, 'r') as f:
            for i, line in enumerate(f):
                if line.startswith('#'):
                    try:
                        m = re.match(pattern, line)
                        level, heading, section_id = m.groups()
                        heading = heading.strip()
                        level = len(level)
                        if section_id is not None: section_id = re.match(r"\{#sec:([^\}]+)\}", section_id).group(1)
                        
                        file_url = filepath.parent.relative_to(base) / (filepath.stem + ".html")
                        url_id = heading.lower().replace(" ", "-")
                        url = f"./{file_url}#{url_id}"
                        
                        if first_thing_in_chapter:
                            current_level = emit_heading(current_level, 1, heading=chapter["name"], url = url, format=output_type)
                            first_thing_in_chapter = False

                        
                        if level > upto_level: continue # Skip anything lower than this

                        current_level = emit_heading(current_level, level+1, heading, url, output_type)

                    except Exception as e:
                        logging.warning(f"Exception {e} on line {i} of {filepath}: {line}")