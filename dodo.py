from pathlib import Path
pandoc = '/usr/local/Cellar/pandoc/2.18/bin/pandoc'

def task_svg_to_pdf():
    "convert inkscape .svg files to .pdf"
    files = Path("./").glob("figure_code/amk_chapter/*.svg")
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
        )
    

def task_markdown():
    "convert .ipynb files to .md files using nbconvert"
    jupyter_files = Path("./").glob("src/*.ipynb")
    for f in jupyter_files:
        target = Path("./build/markdown") / (f.stem + ".md")
        yield dict(
            name = str(f),
            file_dep = [f,],
            targets = [target,],
            actions = [
                f'jupyter nbconvert --TagRemovePreprocessor.remove_cell_tags=\'{"remove_cell"}\' --to markdown "{f}" --output-dir={target.parent} --output "{target.name}"',
                f'python pandoc/figure_to_markdown_tag.py --input "{target}" --output "{target}"'
                ],
        )

def task_json():
    "convert .md files to json using pandoc"
    pandoc_config = 'pandoc/markdown_to_tex.yml'
    latex_filter = 'pandoc/latex_filter.py'
    code_dependencies = [pandoc_config, latex_filter]
    inputs = Path("./").glob("./build/markdown/*.md")
    for f in inputs:
        target = Path("./build/json") / (f.stem + ".json")
        yield dict(
            name = str(f),
            file_dep = [f,] + code_dependencies,
            targets = [target,],
            actions = [f'{pandoc} -d {pandoc_config} --to json "{f}" -o "{target}"',],
        )

def task_latex():
    "convert .md files to .tex files using pandoc"
    pandoc_config = 'pandoc/markdown_to_tex.yml'
    latex_filter = 'pandoc/latex_filter.py'
    code_dependencies = [pandoc_config, latex_filter]
    markdown_files = Path("./").glob("./build/markdown/*.md")
    for f in markdown_files:
        target = Path("./build/tex") / (f.stem + ".tex")
        yield dict(
            name = str(f),
            file_dep = [f,] + code_dependencies,
            targets = [target,],
            actions = [
                f'{pandoc} -d {pandoc_config} "{f}" -o "{target}"',],
        )


def task_html():
    "convert .md files to .html files for jekyll using pandoc"
    pandoc_config = 'pandoc/markdown_to_html.yml'
    filter_file = 'pandoc/html_filter.py'
    template = 'pandoc/jekyll_template.html'
    markdown_files = Path("./").glob("./build/markdown/*.md")
    for f in markdown_files:
        target = Path("./build/html") / (f.stem + ".html")
        yield dict(
            name = str(f),
            file_dep = [pandoc_config, filter_file, template, f,],
            targets = [target,],
            actions = [
                f'{pandoc} -d {pandoc_config} "{f}" -o "{target}"',
                ],
        )

def task_toc():
    ""
    script = 'pandoc/toc_gen.py'
    markdown_files = Path("./").glob("./build/markdown/*.md")
    target = Path("./build/html") / ("toc.html")
    return dict(
        file_dep = [script,] + list(markdown_files),
        targets = [target,],
        actions = [f'python ./{script} > "{target}"',],
    )
def task_copy_html():
    yield dict(
        name = 'copy html over',
        actions = [
            'rm -r /Users/tom/git/tomhodson.github.com/_thesis/',
            'mkdir /Users/tom/git/tomhodson.github.com/_thesis/',
            'cp -r build/html/ /Users/tom/git/tomhodson.github.com/_thesis/',
            ],
        file_dep = list(Path("./").glob("./build/*.html")),
        targets = ['/Users/tom/git/tomhodson.github.com/_thesis',]
    )
    yield dict(
            name = 'copy images over',
            actions = [
                    "rsync -a --prune-empty-dirs --include '*/' --include '*.jpg' --include '*.jpeg' --include '*.png' --include '*.svg'  --include '*.gif' --exclude '*' figure_code /Users/tom/git/tomhodson.github.com/assets/thesis/",
                ],
            file_dep = list(Path("./").glob("./build/*.html")),
            targets = ['/Users/tom/git/tomhodson.github.com/assets/thesis_figs',]
    )

def task_pdf():
    'compile the pdf output using latexmk'
    static_latex_files = [Path("./thesis.preamble.tex"), Path("./thesis.tex")]
    built_latex_files = list(Path("./").glob("./build/tex/*.tex"))
    t = 'thesis'
    jobname = Path("./build/pdf/thesis")
    return dict(
        file_dep = ['pandoc/markdown_to_tex.yml',] + static_latex_files + built_latex_files,
        targets = ['{t}.pdf'],
        actions = [f'latexmk -pdf -f -file-line-error -shell-escape -interaction=nonstopmode -jobname="{jobname}" {t}.tex',
                   f'rm -f {t}.aux {t}.bbl {t}.blg {t}.fdb_latexmk {t}.fls {t}.lof {t}.log {t}.lot {t}.out'
        ],
        # verbosity = 0,
    )

def task_cleanup():
    'clean'
    t = 'thesis'
    return dict(
        actions = [f'rm -f {t}.aux {t}.bbl {t}.blg {t}.fdb_latexmk {t}.fls {t}.lof {t}.log {t}.lot {t}.out'
        ],
    )