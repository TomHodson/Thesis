 #!/bin/bash
set -e

#  pandoc -d pandoc/pandoc.yml \
#     --metadata title="The Amorphous Kitaev Model" \
#     3_Kitaev_Model/kitaev_model_chapter.tex \
#     -o /Users/tom/git/tomhodson.github.com/_posts/2022-07-14-kitaev_model_chapter.html \
    

# cp -r pandoc /Users/tom/git/tomhodson.github.com/

 pandoc -d pandoc/markdown_to_tex.yml \
    --metadata title="The Amorphous Kitaev Model" \
    3_Kitaev_Model/standard_kitaev_model.md \
    -o 3_Kitaev_Model/standard_kitaev_model.tex \



