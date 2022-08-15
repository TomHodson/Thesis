cd ~/git/Late-Stage-Review/figs
rm ../pdf_figs/*.pdf

for filepath in ./*.eps
do
    filename=$(basename -- "$filepath")
    extension="${filename##*.}"
    name="${filename%.*}"
    
    echo "Converting $filepath to ../pdf_figs/${name}.pdf"
    epstopdf $filepath ../pdf_figs/${name}.pdf
    echo "Cropping it"
    pdfcrop ../pdf_figs/${name}.pdf ../pdf_figs/${name}.pdf
    
done