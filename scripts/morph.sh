#!/bin/bash 

export INDIC_NLP_PATH=/home/development/anoop/installs/indic_nlp_library
export INDIC_NLP_RESOURCES=/usr/local/bin/indicnlp/indic_nlp_resources/

#export PYTHONPATH=$PYTHONPATH:$INDIC_NLP_PATH/src

MORPH_SCRIPT="$INDIC_NLP_PATH/src/indicnlp/morph/unsupervised_morph.py"

srclang='hi'

#for tgtlang in `echo bn te ta mr`
for tgtlang in `echo ml`
do 

indir="/home/development/anoop/experiments/rich_morphology/data/parallel/$srclang-$tgtlang/word/"
outdir="/home/development/anoop/experiments/rich_morphology/data/parallel/$srclang-$tgtlang/morph_marker/"

# morph form 
mkdir -p $outdir 

cp  $indir/train.$srclang $outdir/train.$srclang
python $MORPH_SCRIPT  $indir/train.$tgtlang $outdir/train.$tgtlang $tgtlang $INDIC_NLP_RESOURCES True &

cp  $indir/test.$srclang $outdir/test.$srclang
python $MORPH_SCRIPT  $indir/test.$tgtlang $outdir/test.$tgtlang $tgtlang $INDIC_NLP_RESOURCES True &

cp  $indir/tun.$srclang $outdir/tun.$srclang
python $MORPH_SCRIPT  $indir/tun.$tgtlang $outdir/tun.$tgtlang $tgtlang $INDIC_NLP_RESOURCES True &

done 
