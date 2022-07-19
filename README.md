
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