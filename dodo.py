from pathlib import Path
import itertools as it
from collections import defaultdict

DOIT_CONFIG = {
               'continue': True,
               'reporter': 'executed-only'}

pandoc = '/usr/local/Cellar/pandoc/2.18/bin/pandoc'

def rebase(file, src_dir, target_dir, new_extension):
    """Takes a filepath file, makdirs' space for it in target
    dir and returns a path to it with a new extension"""
    parent_relative_to_src = file.relative_to(src_dir).parent
    new_parent = target_dir / parent_relative_to_src
    return new_parent, new_parent / (file.stem + new_extension)

#compute all the dependent files here
src_dir = Path("./src")
src_files = src_dir.glob("**/*.ipynb")
static_latex_files = [Path("./thesis.preamble.tex"), Path("./thesis.tex")]
bibliography_files = [Path("./entire_zotero_library.bib"), Path("./entire_zotero_library.json")]

target_dir = Path("./build/latex")

to_build = [
    [Path("./build/latex/"), ".tex"],
    [Path("./build/markdown/"), ".md"],
    [Path("./build/html/"), ".html"],
]
built_filepaths = []


for src_file in src_files:
    if any(p.startswith(".") for p in src_file.parts): continue
    this_file = {".ipynb" : src_file}
    for target_dir, extension in to_build:
        _, target = rebase(src_file, src_dir, target_dir, new_extension = extension)
        this_file[extension] = target
    built_filepaths.append(this_file)

built_tex = [file['.tex'] for file in built_filepaths]  

def task_svg_to_pdf():
    "convert inkscape .svg files to .pdf"
    folders = ["intro_chapter", "fk_chapter", "amk_chapter"]
    files = it.chain.from_iterable(Path("./").glob(f"figure_code/{folder}/*.svg") for folder in folders)
    for f in files:
        target = f.parent / (f.stem + ".pdf")
        yield dict(
            name = str(f),
            verbosity = 0,
            file_dep = [f,],
            targets = [target,],
            actions = [
                f'inkscape "{f}" --export-type=pdf --export-filename="{target}"',
                ],
            clean = True,
        )
    
def task_ipynb_check():
    r"Currently just checks citations are in the format\ [@key1; @key2]"
    for file in built_filepaths:
        f = file['.ipynb']
        yield dict(
            name = f"Check syntax of {f}",
            file_dep = [f,] + bibliography_files,
            actions = [f'python pandoc/syntax_checks.py "{f}"'],
        )

def task_latex_check(): 
    for f in built_tex + static_latex_files:
        yield dict(
            name = f"Chktex on {f}",
            file_dep = [f,],
            actions = [f'chktex "{f}"'],
        )

def task_markdown():
    "convert .ipynb files to .md files using nbconvert"
    for file in built_filepaths:
        f = file['.ipynb']
        target = file['.md']
        yield dict(
            name = str(f),
            file_dep = [f,],
            targets = [target,],
            actions = [
                f'mkdir -p {target.parent}',
                f'jupyter nbconvert --TagRemovePreprocessor.remove_cell_tags=\'{"remove_cell"}\' --to markdown "{f}" --output-dir={target.parent} --output "{target.name}"',
                f'python pandoc/figure_to_markdown_tag.py --input "{target}" --output "{target}"'
                ],
            clean = True,
            verbosity = 0,
        )

def task_latex():
    "convert .md files to .tex files using pandoc"
    pandoc_config = 'pandoc/markdown_to_tex.yml'
    latex_filter = 'pandoc/latex_filter.py'
    code_dependencies = [pandoc_config, latex_filter]
    for file in built_filepaths:
        f = file[".md"]
        target = file[".tex"]
        yield dict(
            name = str(f),
            file_dep = [f,] + code_dependencies,
            targets = [target,],
            actions = [
                f'mkdir -p {target.parent}',
                f'{pandoc} -d {pandoc_config} "{f}" -o "{target}"',],
            clean = True,
        )


def task_html():
    "convert .md files to .html files for jekyll using pandoc"
    pandoc_config = 'pandoc/markdown_to_html.yml'
    filter_file = 'pandoc/html_filter.py'
    template = 'pandoc/jekyll_template.html'
    for file in built_filepaths:
        f = file[".md"]
        target = file[".html"]
        yield dict(
            name = str(f),
            file_dep = [pandoc_config, filter_file, template, f,] + bibliography_files,
            targets = [target,],
            actions = [
                f'mkdir -p {target.parent}',
                f'{pandoc} -d {pandoc_config} "{f}" -o "{target}"',
                ],
            clean = True,
        )

def task_toc():
    ""
    script = 'pandoc/toc_gen.py'
    markdown_files = [file['.md'] for file in built_filepaths]  
    target = Path("./build/html") / ("toc.html")
    return dict(
        file_dep = [script,] + list(markdown_files),
        targets = [target,],
        actions = [f'mkdir -p {target.parent}', f'python ./{script} > "{target}"',],
        clean = True,
    )
def task_copy_html():
    src_dir = Path("./build/html/")
    target_dir = Path("/Users/tom/git/tomhodson.github.com/_thesis/")
    image_src_dir = Path("./figure_code/")
    image_target_dir = Path("/Users/tom/git/tomhodson.github.com/assets/thesis/")

    html_files = [file['.html'] for file in built_filepaths]  
    html_files.append(Path("./build/html") / ("toc.html"))

    images = [f for t in ['jpeg', 'jpg', 'png', 'svg', 'gif'] for f in image_src_dir.glob(f"**/*.{t}")]
    def copy_job(f, t): 
        return dict(
            name = f"{f}", file_dep = [f,], clean = True,
            targets = [t,], actions = [f'mkdir -p {t.parent}', f'cp "{f}" "{t}"'],
        )

    for f in html_files:
        t = target_dir / f.relative_to(src_dir)
        yield copy_job(f, t)
    
    for f in images:
        t = image_target_dir / f.relative_to(image_src_dir)
        yield copy_job(f, t)

def task_pdf():
    'compile the pdf output using latexmk'
    name = 'thesis'
    target_dir = Path("./build/pdf/")

    # built_latex_files = list(src_dir.glob("**/*.tex"))
    jobname = target_dir / name # tells latexmk to make all the files look like /target/dir/thesis.*
    return dict(
        file_dep = ['pandoc/markdown_to_tex.yml',] + static_latex_files + built_tex + bibliography_files,
        targets = [target_dir / f'{name}.pdf',],
        actions = [
                f'mkdir -p "{target_dir}"',
                f'latexmk -pdf -g -f -file-line-error -silent -shell-escape -interaction=nonstopmode -jobname="{jobname}" {name}.tex || exit 0',
                f'cat {jobname}.log | grep -e Warning -e Error',
        ],
        clean = [
            'latexmk -c -jobname="{jobname}" {name}.tex',
            "rm -rf `biber --cache`",
        ],
        verbosity = 2,
    )