import panflute as pf
import logging
from pathlib import Path
import json

src = Path("../figure_code/amk_chapter/visual_kitaev_1.svg")
base = Path("../../figure_code/")
new_base = Path("/assets/thesis/")

with open("./build/html/section_id_lookup_table.json", 'r') as f:
    lookup_table = json.load(f)

def url_to(section, fragment = True):
    # if section["level"] == 0: #different logic for chapters
    #     section = list(lookup_table.values())[section["index"] + 1]
    #     fragment = False
    filepath = Path(section['filepath'])
    url = "../" + str(filepath.parent / filepath.stem) + ".html"
    if fragment: url += "#" + section['section_id']
    return url

def next_section(doc): return None

def action(elem, doc):
    if type(elem) == pf.Link:
        if elem.url.startswith("#") and not elem.url.startswith("#fig:") and not elem.url.startswith("#eq:"):
            if elem.url[1:] not in lookup_table:
                logging.warning(f"Can't find section ref to {elem.url}")
            else:
                section = lookup_table[elem.url[1:]]
                new_url = url_to(section, fragment = section['level'] > 0)
                # logging.warning(f"Rewriting {elem} to have url = {new_url}")
                elem.url = new_url
        # 6_Appendices/A.1_Particle_Hole_Symmetry.html#particle-hole-symmetry
        return elem
    if type(elem) == pf.Image:
        # img = pf.convert_text(elem.text, "html")[0].content[0]
        img = elem
        src = Path(img.url)
        img.identifier = img.identifier.replace(":", "-").replace("#", "")  #: is not valid in HTML id attributes, use - instead
        if src.is_relative_to(base): 
            src = new_base / src.relative_to(base)
        
        if img.url.startswith("attachment:"):
            _, name = img.url.split(":")
            src = new_base / name
            
        img.url = str(src)
        return img

def add_header(doc, lookup_table, chapter_id):
    chapter = lookup_table[chapter_id]
    header = pf.Div(pf.Para(pf.Str(chapter["heading"])), pf.HorizontalRule(), identifier = "page-header")
    doc.content.insert(0, header)

def finalize(doc):
    # Add a next section/chapter link at the end of each page
    try:
        added_header = False
        if 'chapterId' in doc.metadata:
            chapter_id = pf.stringify(doc.metadata['chapterId'])
            add_header(doc, lookup_table, chapter_id)
            added_header = True

        #Get the last heading in the document
        headers = [h for h in doc.content if type(h) == pf.Header]
        first_header_id = headers[0].identifier
        first_header = lookup_table[first_header_id]
        last_header_id = headers[-1].identifier
        last_header = lookup_table[last_header_id]
        chapter_id = last_header["chapter_id"]
        
        # We try to add the chapter heading two different ways because
        # I currently don't have a good way to know what file we're actually in!
        if not added_header:
            add_header(doc, lookup_table, chapter_id)
            added_header = True

        previous_header = list(lookup_table.values())[first_header["index"] - 1]
        # logging.warning(previous_header)
        if previous_header["level"] == 0: #i.e if this the first section after a new chapter
            doc.content.insert(1, pf.Header(pf.Str(previous_header["heading"]), level = 1, identifier = previous_header["chapter_id"]))

        last_header_index = last_header["index"]
        next_section, nextnext_section = list(lookup_table.values())[last_header_index + 1:last_header_index+3]
        level = next_section["level"]
        url = url_to(next_section, fragment=False)
        # pf.debug(next_section)
        link = pf.Link(pf.Str(next_section['heading']), url=url)
        level = next_section["level"]
        name = "Chapter" if level == 0 else "Section"
        doc.content.append(pf.Para(pf.Str(f"Next {name}: "), link))
        # pf.debug(doc.content[0:5])
    except (IndexError, ValueError):
        pass #either there were no headers 
        #or it's the last document so has no next header
    except KeyError:
        logging.warning(f"KeyError: {first_header_id} not found in toc data structure")

    # toclink = pf.Link(pf.Str("Table of Contents"), url="/thesis")
    # doc.content.append(pf.Para(toclink))

def main(doc=None):
    return pf.run_filter(action, finalize=finalize, doc=doc)

if __name__ == "__main__":
    main()