import panflute as pf
import logging
from pathlib import Path

src = Path("../figure_code/amk_chapter/visual_kitaev_1.svg")
base = Path("../")
new_base = Path("pandoc/figs/")

def action(elem, doc):
    if type(elem) == pf.RawInline and elem.format == "html" and "<img " in elem.text:
        img = pf.convert_text(elem.text, "html")[0].content[0]
        src = Path(img.url)
        if src.is_relative_to(base): 
            src = new_base / src.relative_to(base)
        
        if img.url.startswith("attachment:"):
            _, name = img.url.split(":")
            src = new_base / name

        if img.url.endswith(".svg"):
            src = src.parent / (src.stem + ".pdf")
            
        img.url = str(src)
        return img

def main(doc=None):
    return pf.run_filter(action, doc=doc)

if __name__ == "__main__":
    main()