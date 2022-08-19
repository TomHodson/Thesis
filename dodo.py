from pathlib import Path
pandoc = '/usr/local/Cellar/pandoc/2.18/bin/pandoc'
import logging

def rebase(file, src_dir, target_dir, new_extension):
    """Takes a filepath file, makdirs' space for it in target
    dir and returns a path to it with a new extension"""
    parent_relative_to_src = file.relative_to(src_dir).parent
    new_parent = target_dir / parent_relative_to_src
    return new_parent, new_parent / (file.stem + new_extension)

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
            clean = True,
        )
    

def task_markdown():
    "convert .ipynb files to .md files using nbconvert"
    src_dir = Path("./src")
    target_dir = Path("./build/markdown")
    jupyter_files = src_dir.glob("**/*.ipynb")
    for f in jupyter_files:
        if any(p.startswith(".") for p in f.parts): continue
        new_parents, target = rebase(f, src_dir, target_dir, new_extension = ".md")
        yield dict(
            name = str(f),
            file_dep = [f,],
            targets = [target,],
            actions = [
                f'mkdir -p {new_parents}',
                f'jupyter nbconvert --TagRemovePreprocessor.remove_cell_tags=\'{"remove_cell"}\' --to markdown "{f}" --output-dir={target.parent} --output "{target.name}"',
                f'python pandoc/figure_to_markdown_tag.py --input "{target}" --output "{target}"'
                ],
            clean = True,
        )

def task_json():
    "convert .md files to json using pandoc"
    pandoc_config = 'pandoc/markdown_to_tex.yml'
    latex_filter = 'pandoc/latex_filter.py'
    code_dependencies = [pandoc_config, latex_filter]
    src_dir = Path("./build/markdown/")
    target_dir = Path("./build/json/")
    inputs = src_dir.glob("**/*.md")
    for f in inputs:
        if any(p.startswith(".") for p in f.parts): continue
        new_parents, target = rebase(f, src_dir, target_dir, new_extension = ".md")
        yield dict(
            name = str(f),
            file_dep = [f,] + code_dependencies,
            targets = [target,],
            actions = [
                f'mkdir -p {new_parents}',
                f'{pandoc} -d {pandoc_config} --to json "{f}" -o "{target}"',],
            clean = True,
        )

def task_latex():
    "convert .md files to .tex files using pandoc"
    pandoc_config = 'pandoc/markdown_to_tex.yml'
    latex_filter = 'pandoc/latex_filter.py'
    code_dependencies = [pandoc_config, latex_filter]
    src_dir = Path("./build/markdown/")
    target_dir = Path("./build/latex/")
    inputs = src_dir.glob("**/*.md")
    for f in inputs:
        new_parents, target = rebase(f, src_dir, target_dir, new_extension = ".tex")
        # target = target_dir / target.name
        yield dict(
            name = str(f),
            file_dep = [f,] + code_dependencies,
            targets = [target,],
            actions = [
                f'mkdir -p {new_parents}',
                f'{pandoc} -d {pandoc_config} "{f}" -o "{target}"',],
            clean = True,
        )


def task_html():
    "convert .md files to .html files for jekyll using pandoc"
    pandoc_config = 'pandoc/markdown_to_html.yml'
    filter_file = 'pandoc/html_filter.py'
    template = 'pandoc/jekyll_template.html'
    src_dir = Path("./build/markdown/")
    target_dir = Path("./build/html/")
    inputs = src_dir.glob("**/*.md")
    for f in inputs:
        new_parents, target = rebase(f, src_dir, target_dir, new_extension = ".html")
        yield dict(
            name = str(f),
            file_dep = [pandoc_config, filter_file, template, f,],
            targets = [target,],
            actions = [
                f'mkdir -p {new_parents}',
                f'{pandoc} -d {pandoc_config} "{f}" -o "{target}"',
                ],
            clean = True,
        )

def task_toc():
    ""
    script = 'pandoc/toc_gen.py'
    markdown_files = Path("./").glob("./build/markdown/*.md")
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

    built_html = list(src_dir.glob("**/*.html"))
    images = [f for t in ['jpeg', 'jpg', 'png', 'svg', 'gif'] for f in image_src_dir.glob(f"**/*.{t}")]
    def copy_job(f, t): 
        return dict(
            name = f"{f}", file_dep = [f,], clean = True,
            targets = [t,], actions = [f'mkdir -p {t.parent}', f'cp "{f}" "{t}"'],
        )

    for f in built_html:
        t = target_dir / f.relative_to(src_dir)
        yield copy_job(f, t)
    
    for f in images:
        t = image_target_dir / f.relative_to(image_src_dir)
        yield copy_job(f, t)

def task_pdf():
    'compile the pdf output using latexmk'
    name = 'thesis'
    src_dir = Path("./build/latex/")
    target_dir = Path("./build/pdf/")
    static_latex_files = [Path("./thesis.preamble.tex"), Path("./thesis.tex")]
    built_latex_files = list(src_dir.glob("**/*.tex"))
    jobname = target_dir / name # tells latexmk to make all the files look like /target/dir/thesis.*
    return dict(
        file_dep = ['pandoc/markdown_to_tex.yml',] + static_latex_files + built_latex_files,
        targets = [target_dir / f'{name}.pdf',],
        actions = [
                f'mkdir -p "{target_dir}"',
                f'latexmk -pdf -f -file-line-error -shell-escape -interaction=nonstopmode -jobname="{jobname}" {name}.tex',
        ],
        clean = True,
        # verbosity = 0,
    )

# def task_rebuild():
#     folders_to_wipe = [
#         "./build",
#         "/Users/tom/git/tomhodson.github.com/_thesis/",
#         "/Users/tom/git/tomhodson.github.com/assets/thesis/",
#     ]

#     for f in folders_to_wipe:
#         if 'src' in Path(f).resolve().parts: continue #extra protection!
#         yield dict(
#             name = f"Wipe {f}", actions = [f'rm -r "{f}"'],
#         )