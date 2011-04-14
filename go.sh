base=`basename $1 .tex` 
python pp4tex.py $1 && platex pp_$1 && dvipdfmx pp_$base.dvi && mv pp_$base.pdf $base.pdf