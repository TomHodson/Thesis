# Building
The current build process is labrinthine and I regret it somewhat, but it works. It's broken down into a series of steps:

## Jupyter Notebooks -> Markdown
Config files: dodo.py:task_markdown, pandoc/figure_to_markdown.py
Uses NbConvert to convert notebooks to markdown.
figure_to_markdown.py converts `<figure>` tags to markdown images and parses a bunch of metadata from the figure tags 
```html
<figure>
<img src="src" style="max-width:700px;" title="title">
<figcaption>
Caption
</figcaption>
</figure>
```
giving output in the form:
```markdown
![alt_text](src)(href){#fig:label  width=100% short-caption="title"}
```
I use html `<figure>` tags in Jupyter rather than plain markdown image tags because it allows me to preview the captions and center them with css.

## Markdown -> HTML
Config files: dodo.py:task_html, pandoc/markdown_to_html.yml pandoc/html_filter.py
For a jekyll website version. 
html_filter fixes the relative image links.

## Markdown -> Latex 
Config files: dodo.py:task_latex, pandoc/markdown_to_latex.yml pandoc/latex_filter.py pandoc/latex_short_caption.lua
For the PDF version
latex_filter sorts out image paths and adds "Animated version online" to images that have a gif version.
latex_short_caption.lua allows the title from markdown tags that look like `[alt_text](src){short-caption="title" extra = metadata}` to be incorporated into latex figures using `\caption[title]{alt_text}`

## Doing compilation locally
Once:
```
# install texlive, mine was already installed so I'll skip this step, google it.
# make sure you have tlmgr, I think this comes with texlive

sudo tlmgr update --self #update tlmgr because it always complains
sudo tlmgr install latexmk # latexmk manages latex compilation with the latexmkrc file
sudo tlmgr install texliveonfly # this package can autoinstall dependencies

# auto install dependencies in thesis.tex
# this will install everything and then eventually fail but don't worry
sudo texliveonfly thesis.tex 

# actually compile
latexmk -pdf -shell-escape -interaction=nonstopmode thesis.tex
```

## Getting it working in visual studio code
Install Latex Workshop
Add the `-shell-escape` arg to the latexmk commandd invocation by adding this to settings.json:
```json
    "latex-workshop.latex.recipes": [
        {
          "name": "latexmk 🔃",
          "tools": [
            "latexmk"
          ]
        }
      ],
    "latex-workshop.latex.tools": [
        {
          "name": "latexmk",
          "command": "latexmk",
          "args": [
            "-synctex=1",
            "-interaction=nonstopmode",
            "-file-line-error",
            "-pdf",
            "-outdir=%OUTDIR%",
            "-shell-escape", // The non default line for the minted package  to work
            "%DOC%"
          ],
          "env": {}
        }],
```

[Reproducing overleaf compilation locally]()

[Using a custom latexmkrc](https://www.overleaf.com/learn/how-to/How_does_Overleaf_compile_my_project%3F)

[How to put .sty files in a subfolder](https://www.overleaf.com/learn/latex/Questions/I_have_a_lot_of_.cls%2C_.sty%2C_.bst_files%2C_and_I_want_to_put_them_in_a_folder_to_keep_my_project_uncluttered._But_my_project_is_not_finding_them_to_compile_correctly)


## Conda environment
To install 
```
conda env create --file environment.yml
```

To update after changing environment.yml
```
conda env update --file environment.yml --prune
```