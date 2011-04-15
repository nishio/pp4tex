dir=`dirname $1`
base=`basename $1 .tex` 
python pp4tex.py $dir/$base.tex \
&& platex $dir/pp_$base.tex \
&& dvipdfmx pp_$base.dvi \
&& mv pp_$base.pdf $base.pdf

