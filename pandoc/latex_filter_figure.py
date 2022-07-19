import panflute as pf
import logging
from pathlib import Path
from bs4 import BeautifulSoup

def replace_ranges(l, ranges):
    """Given a list and ranges = [(i,j,el), (k,l,el)...] 
    return elements in list whose indices are not in those ranges
    but replace each range with el
    i,j,k,l must be strickly increasing, no overlaps or repeats are allowed
    """
    ranges = iter(ranges)
    start, end, replacement = next(ranges, (None,None,None))
    keeping = True
    for i, el in enumerate(l):
        if i == start: 
            keeping = False
            yield replacement
        if i == end:
            keeping = True
            start, end, replacement = next(ranges, (None,None,None))
        
        if keeping: yield el

def action(elem, doc):
    pass


def prepare(doc):
    start = None
    end = None
    doc.to_replace = []

    for elem in doc.content:
        if type(elem) == pf.RawBlock and elem.text == "<figure>":
            start = elem
        if type(elem) == pf.RawBlock and elem.text == "</figure>":
            end = elem
        
        if start is not None and end is not None:
            figure = doc.content[start.index : end.index]
            html = pf.stringify(pf.Doc(*figure.list))
            soup = BeautifulSoup(html, features="html.parser")
            
            url = soup.img['src']
            caption = pf.convert_text(soup.figcaption.text, 'html')[0].content
            identifier = soup.img.id or ''
            
            image = pf.Image(*caption, url = url, identifier=identifier)
            doc.to_replace.append((start.index, end.index+1, pf.Plain(image)))
            start = None
            end = None

def finalize(doc):
    logging.warning([[s,e] for s,e,el in doc.to_replace])
    doc.content.list = list(replace_ranges(doc.content.list, doc.to_replace))

def main(doc=None):
    return pf.run_filter(action,
                        prepare = prepare,
                        finalize=finalize,
                         doc=doc)


if __name__ == "__main__":
    main()