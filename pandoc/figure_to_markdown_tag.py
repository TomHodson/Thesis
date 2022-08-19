#!/usr/bin/env python3
from pathlib import Path
import argparse
import logging

parser = argparse.ArgumentParser(description='Convert figure tags to markdown tags')
parser.add_argument('--input', required=True, help='The input file')
parser.add_argument('--output', required=True, help='The output file')
args = parser.parse_args()

with open(args.input, 'r') as f:
    text = f.read()
    
from bs4 import BeautifulSoup
soup = BeautifulSoup(text, 'html.parser')

tags = list(soup.findAll("figure"))
for a in tags:
    caption = a.find("figcaption")
    if caption: caption = caption.text.strip()
    else: caption = ''

    tag_id = a.img.attrs.get('id', '')
    tag_class = a.img.attrs.get('class', '')
    src = a.img['src']
    name = Path(src).stem
    if not tag_id: tag_id = f"#fig:{name}"
    
    style = a.img.get('style', 'max-width:700px;')
    style = dict([l.split(':') for l in style.split(";") if l])

    title = a.img.get("title", "no title")

    width = style.get('max-width', "700px")
    if width.endswith("px"):
        width = int(width[:-2]) / 700 * 100
        width = f"{width:.0f}%"
    else:
        width = "100%"
    
    extra_info_string = f'{tag_id} {tag_class} width={width} short-caption="{title}"'.strip()

    markdown_tag = f'![{caption}]({src})'
    if extra_info_string: markdown_tag += f'{{{extra_info_string}}}'

    a.replace_with(markdown_tag)
    
for s in soup.findAll('style'): s.extract()
    
with open(args.output, 'w') as f:
    f.write(soup.decode(formatter = None))

logging.info(f"Converted {len(tags)} figure tags to markdown")