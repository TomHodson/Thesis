"""
Check for syntax errors that I have made frequently.
"""
import json
import re
import sys
import logging
from pathlib import Path

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def highlight_matches(string, matches, color = bcolors.FAIL):
    "given a string and a sequence of match objects, highlight them"
    offset = 0 #we're adding to the string so the spans off the matches need to be offset
    for m in matches:
        start, end = m
        start += offset
        end += offset
        string = string[:start] + color + string[start:end] + bcolors.ENDC + string[end:]
        offset += len(color) + len(bcolors.ENDC)
    return string
    
malformed_reference_regexes = {
    "Missing starting @" : re.compile("\[[^@\[][^\[]+\][^\(]"),
    "Comma in citation list": re.compile("\[[^\[]*,[^\[]*\][^\(]"),
}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("requires one argument: the file to the ipynb file to check")
        sys.exit(-1)
    
    file = Path(sys.argv[1])

    # logging.warning(sys.argv[1])
    with open(file) as f:
        ipynb_notebook = json.load(f)
    
    with open("entire_zotero_library.bib", 'r') as f:
        bibs = f.read()
    cite_keys = re.findall("@[\S]+{([^,]+),", bibs)

    cells = ipynb_notebook['cells']
    citekeys_found = set()

    for cell_number, cell in enumerate(cells):
        if 'remove_cell' in cell.get('metadata', {}).get('tags', []): continue
        if cell.get('cell_type', '') != 'markdown': continue
        src_lines = cell['source']
        # print(src)
        for line_number, src_line in enumerate(src_lines):
            error_msgs = []
            errors = []
            for cite_key in cite_keys:
                i = src_line.find(cite_key)
                if i > 0:
                    # print(cite_key, src_line[i-1:i+len(cite_key)+1], src_line[i-1], src_line[i + len(cite_key)])
                    citekeys_found.add(cite_key)
                    if not (src_line[i-3:i] == "; @" or src_line[i-4:i] == r'\ [@' or src_line[i-4:i] == '\\\xa0[@'):
                        # breakpoint()
                        error_msgs.append(f"'{src_line[i-3:i].encode('unicode-escape')}' != '; @' or '\xa0[@'")
                        errors.append((i, i+len(cite_key)))
                    
                    if src_line[i + len(cite_key)] not in ["]", ";"]:
                        error_msgs.append(f"Ending is '{src_line[i + len(cite_key)]}' when it should be ']' or ';'")
                        errors.append((i, i+len(cite_key)))
            
            if errors:
                logging.warning(f"""{file.name} Line {line_number} of cell {cell_number}
                Errors: {', '.join(error_msgs)}
                {highlight_matches(src_line, errors)}""")

    with open("build/pdf/for_zotero_import.aux", 'a') as f:
        f.write("\n".join(f"\citation{{{citekey}}}" for citekey in citekeys_found))