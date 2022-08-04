import panflute as pf
import logging
from pathlib import Path

src = Path("../figure_code/amk_chapter/visual_kitaev_1.svg")
base = Path("../figure_code/")
new_base = Path("/assets/thesis/figure_code/")

def action(elem, doc):
    # if type(elem) == pf.RawInline and elem.format == "html" and "<img " in elem.text:
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