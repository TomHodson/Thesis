#!/usr/bin/env python3
from pathlib import Path
import re
import sys
import logging
import json
from collections import OrderedDict

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

def add_to_section_list(id, chapter_id, path, line, level, heading, index):
    if id in lookup_table: 
        logging.warning(f"Repeated id '{id} in {path.name} line {line}'")
    else:
        lookup_table[id] = dict(
            filepath = str(path),
            section_id = id,
            chapter_id = chapter_id,
            level = level,
            heading = heading,
            index = index,
            line = line,
        )
        index += 1
    return index


base = Path("./build/markdown")
chapters = [
    dict(
    name = "1 Introduction",
    contents = "1_Introduction"
    ),
    dict(
    name = "2 Background",
    contents = "2_Background"
    ),
    dict(
    name = "3 The Long Range Falikov-Kimball Model",
    contents = "3_Long_Range_Falikov_Kimball"
    ),
    dict(
    name = "4 The Amorphous Kitaev Model",
    contents = "4_Amorphous_Kitaev_Model",
    ),
    dict(
    name = "5 Conclusion",
    contents = "5_Conclusion",
    ),
    dict(
    name = "Appendices",
    contents = "6_Appendices",
    )
]

pattern = re.compile(r"(#+)\s+([^{]+)\s*?(\{#[^}]+\})?")
lookup_table = OrderedDict()

current_level = 0
index = 0 #a monotonic increasing ordering for every heading
for chapter in chapters:
    chapter_filename = base / chapter["contents"]
    chapter_id = chapter["name"].lower().replace(" ", "-")
    chapter_files = sorted(chapter_filename.glob("*.md"))
    first_thing_in_chapter = True

    #Add the chapter to our table of contents datastructure
    index = add_to_section_list(
        id = chapter_id,
        chapter_id = chapter_id,
        path = Path(chapter["contents"]),
        line = 0, 
        level = 0,
        heading = chapter["name"], 
        index = index)
    
    for filepath in chapter_files:        
        with open(filepath, 'r') as f:
            for i, line in enumerate(f):
                if line.startswith('#'):
                    try:
                        m = re.match(pattern, line)
                        level, heading, section_id = m.groups()
                        heading = heading.strip()
                        level = len(level)
                        if section_id is not None: section_id = re.match(r"\{#([^\}]+)\}", section_id).group(1)
                        else: section_id = heading.lower().replace(" ", "-")
                        
                        # save the section ids to a python dict for later lookup
                        # this enables cross file links later
                        index = add_to_section_list(id = section_id,
                            chapter_id=chapter_id,
                            path = filepath.relative_to("build/markdown/"),
                            line = i, 
                            level = level,
                            heading = heading, 
                            index = index)
                        
                        file_url = filepath.parent.relative_to(base) / (filepath.stem + ".html")
                        url_id = heading.lower().replace(" ", "-")
                        
                        #use fragments in the url if it's not the first thing on the page that 
                        #we're linking to
                        url = f"./{file_url}" if first_thing_in_chapter else f"./{file_url}#{url_id}"
                        
                        #output a chapter heading too
                        if first_thing_in_chapter:
                            current_level = emit_heading(current_level, 1, heading=chapter["name"], url = url, format=output_type)
                            first_thing_in_chapter = False

                        
                        if level > upto_level: continue # Skip anything lower than this

                        current_level = emit_heading(current_level, level+1, heading, url, output_type)

                    except Exception as e:
                        logging.warning(f"Exception {e} on line {i} of {filepath}: {line}")

with open("./build/html/section_id_lookup_table.json", 'w') as f:
    json.dump(lookup_table, f, indent=4) 