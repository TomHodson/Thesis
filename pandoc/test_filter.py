import panflute as pf
import logging
from pathlib import Path

src = Path("../figure_code/amk_chapter/visual_kitaev_1.svg")
base = Path("../")
new_base = Path("/assets/thesis_figs")

def action(elem, doc):
    if type(elem) == pf.RawInline and elem.format == "html" and "<img " in elem.text:
        img = pf.convert_text(elem.text, "html")[0].content[0]
        src = Path(img.url)
        if src.is_relative_to(base): 
            img.url = str(new_base / src.relative_to(base))
            logging.warning(f"rewrote {src} to {img.url}")
        if img.url.startswith("attachment:"):
            old_url = img.url
            _, name = img.url.split(":")
            img.url = str(new_base / name)
            logging.warning(f"rewrote {old_url} to {img.url}")
        return img

def main(doc=None):
    return pf.run_filter(action, doc=doc)

if __name__ == "__main__":
    main()