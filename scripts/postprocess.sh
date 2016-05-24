#!/bin/bash 

DESEG_PROJ=/home/development/anoop/experiments/rich_morphology/src/morph-desegmenter

export INDIC_NLP_PATH=/home/development/anoop/installs/indic_nlp_library
export INDIC_NLP_RESOURCES=/usr/local/bin/indicnlp/indic_nlp_resources/
export MORPH_SCRIPT="$INDIC_NLP_PATH/src/indicnlp/morph/unsupervised_morph.py"
export BLEU_SCRIPT="/usr/local/bin/smt/mosesdecoder-2.1.1/scripts/generic/multi-bleu.perl"
export METEOR_HOME="/usr/local/bin/smt/smt_eval_metrics/meteor"

export PYTHONPATH=$PYTHONPATH:$DESEG_PROJ/src

resultdir="/home/development/anoop/experiments/rich_morphology/experiments/"
gold_dir="/home/development/anoop/experiments/rich_morphology/data/parallel/"

s='hi'

for t in `echo ta te mr bn ml`
do 

### desegment out of morpu_marker
#python $DESEG_PROJ/src/cfilt/translate/desegmenter.py $resultdir/$s-$t/morph_marker/evaluation/test.$t $resultdir/$s-$t/morph_marker/evaluation/test.deseg.$t
#
## compute BLEU for 
#$BLEU_SCRIPT $gold_dir/$s-$t/word/test.$t < $resultdir/$s-$t/morph_marker/evaluation/test.deseg.$t > $resultdir/$s-$t/morph_marker/evaluation/test.deseg.$t.bleu
#
#
## segment out of word 
#python $MORPH_SCRIPT  $resultdir/$s-$t/word/evaluation/test.$t $resultdir/$s-$t/word/evaluation/test.seg.$t \
#                         $t $INDIC_NLP_RESOURCES True 
#
## compute BLEU for 
#$BLEU_SCRIPT $gold_dir/$s-$t/morph_marker/test.$t < $resultdir/$s-$t/word/evaluation/test.seg.$t > $resultdir/$s-$t/word/evaluation/test.seg.$t.bleu

#### compute METEOR scores 
cd $METEOR_HOME

# for marker based 
java -Xmx512m -jar meteor-*.jar $resultdir/$s-$t/morph_marker/evaluation/test.deseg.$t \
                                $gold_dir/$s-$t/word/test.$t  \
                                -l $t > $resultdir/$s-$t/morph_marker/evaluation/test.deseg.$t.meteor

# for word based 
java -Xmx512m -jar meteor-*.jar $resultdir/$s-$t/word/evaluation/test.$t \
                                $gold_dir/$s-$t/word/test.$t  \
                                -l $t > $resultdir/$s-$t/word/evaluation/results_with_tuning/meteor.txt

done 

