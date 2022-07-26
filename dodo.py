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
    

def task_jupyter_to_markdown():
    "convert .ipynb files to .md files using nbconvert"
    jupyter_files = Path("./").glob("*/*.ipynb")
    for f in jupyter_files:
        target = f.parent / (f.stem + ".md")
        yield dict(
            name = str(f),
            file_dep = [f,],
            targets = [target,],
            actions = [
                f'jupyter nbconvert --to markdown "{f}" --output {target.name}',],
        )

def task_markdown_to_json():
    "convert .md files to json using pandoc"
    pandoc_config = 'pandoc/markdown_to_tex.yml'
    latex_filter = 'pandoc/latex_filter.py'
    latex_filter_figure = 'pandoc/latex_filter_figure.py'
    code_dependencies = [pandoc_config, latex_filter, latex_filter_figure]
    inputs = Path("./").glob("*/*.md")
    for f in inputs:
        target = f.parent / (f.stem + ".json")
        yield dict(
            name = str(f),
            file_dep = [f,] + code_dependencies,
            targets = [target,],
            actions = [f'{pandoc} -d {pandoc_config} --to json {f} -o {target}',],
        )

def task_latex():
    "convert .md files to .tex files using pandoc"
    pandoc_config = 'pandoc/markdown_to_tex.yml'
    latex_filter = 'pandoc/latex_filter.py'
    latex_filter_figure = 'pandoc/latex_filter_figure.py'
    code_dependencies = [pandoc_config, latex_filter, latex_filter_figure]
    markdown_files = Path("./").glob("*/*.md")
    for f in markdown_files:
        target = f.parent / (f.stem + ".tex")
        yield dict(
            name = str(f),
            file_dep = [f,] + code_dependencies,
            targets = [target,],
            actions = [
                f'{pandoc} -d {pandoc_config} {f} -o {target}',],
        )

def task_pdf():
    'compile the pdf output using latexmk'
    latex_files = list(Path("./").glob("*/*.tex"))
    t = 'thesis'
    return dict(
        file_dep = ['pandoc/markdown_to_tex.yml',] + latex_files,
        targets = ['thesis.pdf'],
        actions = ['latexmk -pdf -f -shell-escape -interaction=nonstopmode thesis.tex',
                   'rm {t}.aux {t}.bbl {t}.blg {t}.fdb_latexmk {t}.fls {t}.lof {t}.log {t}.lot {t}.out {}'
        ],
        verbosity = 0,
    )

def task_cleanup():
    'clean'
    t = 'thesis'
    return dict(
        actions = [f'rm {t}.aux {t}.bbl {t}.blg {t}.fdb_latexmk {t}.fls {t}.lof {t}.log {t}.lot {t}.out'
        ],
    )


def task_blog():
    "convert .md files to .html files for jekyll using pandoc"
    pandoc_config = 'pandoc/markdown_to_html.yml'
    markdown_files = Path("./").glob("*/*.md")
    for f in markdown_files:
        target = Path("/Users/tom/git/tomhodson.github.com/_thesis/") / (f.stem + ".html")
        yield dict(
            name = str(f),
            file_dep = [pandoc_config, f,],
            targets = [target,],
            actions = [
                f'{pandoc} -d {pandoc_config} {f} -o {target}',
                ],
        )
    yield dict(
            name = 'copy images over',
            actions = ['cp -r pandoc/figs/* /Users/tom/git/tomhodson.github.com/assets/thesis_figs/'],
            file_dep = list(Path("./").glob("*/*.html")),
            targets = ['/Users/tom/git/tomhodson.github.com/assets/thesis_figs',]
    )