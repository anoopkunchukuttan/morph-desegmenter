#!/bin/bash 

export INDIC_NLP_PATH=/home/development/anoop/installs/indic_nlp_library
export INDIC_NLP_RESOURCES=/usr/local/bin/indicnlp/indic_nlp_resources/

export PYTHONPATH=$PYTHONPATH:$INDIC_NLP_PATH/src

srclang='ta'
tgtlang='ml'

indir="/home/development/anoop/tmp/$srclang-$tgtlang"


outdir="/home/development/anoop/experiments/rich_morphology/experiments/baseline_experiment_hi_ma/data/parallel/$srclang-$tgtlang/morph_marker/"

# morph form 
mkdir -p $outdir 

python preprocess.py  $indir/train.$srclang $outdir/train.$srclang $srclang True &
python preprocess.py  $indir/train.$tgtlang $outdir/train.$tgtlang $tgtlang True &

python preprocess.py  $indir/test.$srclang $outdir/test.$srclang $srclang True & 
python preprocess.py  $indir/test.$tgtlang $outdir/test.$tgtlang $tgtlang True &

python preprocess.py  $indir/tun.$srclang $outdir/tun.$srclang $srclang True &
python preprocess.py  $indir/tun.$tgtlang $outdir/tun.$tgtlang $tgtlang True &

outdir="/home/development/anoop/experiments/rich_morphology/experiments/baseline_experiment_hi_ma/data/parallel/$srclang-$tgtlang/word/"

mkdir -p $outdir 

# surface form 

python preprocess.py  $indir/train.$srclang $outdir/train.$srclang $srclang False &
python preprocess.py  $indir/train.$tgtlang $outdir/train.$tgtlang $tgtlang False &

python preprocess.py  $indir/test.$srclang $outdir/test.$srclang $srclang False & 
python preprocess.py  $indir/test.$tgtlang $outdir/test.$tgtlang $tgtlang False &

python preprocess.py  $indir/tun.$srclang $outdir/tun.$srclang $srclang False &
python preprocess.py  $indir/tun.$tgtlang $outdir/tun.$tgtlang $tgtlang False &

## monolingual 
#
#python preprocess.py  /home/development/anoop/experiments/rich_morphology/data/monolingual/mah_times/maharashtra_times.tokenized.mr \
#             /home/development/anoop/experiments/rich_morphology/experiments/baseline_experiment_hi_ma/data/monolingual/mr/morph_marker.mr \
#             $tgtlang True & 
#
#python preprocess.py  /home/development/anoop/experiments/rich_morphology/data/monolingual/mah_times/maharashtra_times.tokenized.mr \
#             /home/development/anoop/experiments/rich_morphology/experiments/baseline_experiment_hi_ma/data/monolingual/mr/word.mr \
#             $tgtlang False & 
#
#python preprocess.py  /home/development/anoop/experiments/rich_morphology/data/monolingual/FIRE.selected.mr \
#             /home/development/anoop/experiments/rich_morphology/experiments/baseline_experiment_hi_ma/data/monolingual/mr/morph_marker.FIRE.mr \
#             $tgtlang True & 
#
#python preprocess.py  /home/development/anoop/experiments/rich_morphology/data/monolingual/FIRE.selected.mr \
#             /home/development/anoop/experiments/rich_morphology/experiments/baseline_experiment_hi_ma/data/monolingual/mr/word.FIRE.mr \
#             $tgtlang False & 
#
