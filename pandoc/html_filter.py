import panflute as pf
import logging
from pathlib import Path
import json

src = Path("../figure_code/amk_chapter/visual_kitaev_1.svg")
base = Path("../../figure_code/")
new_base = Path("/assets/thesis/")

with open("./build/html/section_id_lookup_table.json", 'r') as f:
    lookup_table = json.load(f)

def action(elem, doc):
    if type(elem) == pf.Link:
        if elem.url.startswith("#") and ':' not in elem.url:
            if elem.url[1:] not in lookup_table:
                logging.warning(f"Can't find section ref to {elem.url}")
            else:
                info = lookup_table[elem.url[1:]]
                filepath = Path(info['filepath'])
                new_url = "../" + str(filepath.parent / filepath.stem) + ".html#" + info['section_id']
                logging.warning(f"Rewriting {elem} to have url = {new_url}")
                elem.url = new_url
        # 6_Appendices/A.1_Particle_Hole_Symmetry.html#particle-hole-symmetry
        return elem
    if type(elem) == pf.Image:
        # img = pf.convert_text(elem.text, "html")[0].content[0]
        img = elem
        src = Path(img.url)
        if src.is_relative_to(base): 
            src = new_base / src.relative_to(base)
        
        if img.url.startswith("attachment:"):
            _, name = img.url.split(":")
            src = new_base / name

        # if img.url.endswith(".svg") or img.url.endswith(".gif"):
        #     src = src.parent / (src.stem + ".pdf")
            
        img.url = str(src)
        return img

def main(doc=None):
    return pf.run_filter(action, doc=doc)

if __name__ == "__main__":
    main()