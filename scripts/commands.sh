#/bin/bash 

## removing marker tags
#for lang in `echo mr ml ta`
#do 
#    python preprocess.py  ../../data/monolingual/$lang/morph_marker.$lang ../../data/monolingual/$lang/morph.$lang & 
#done 

# create language models 
LM_SCRIPT="/usr/local/bin/smt/moses_job_scripts/train_srilm.sh"

order=5

#for lang in `echo mr ta te bn`
for lang in `echo ml`
do 
    mkdir -p ../../data/lm/$lang/
    for format in `echo morph_marker word`
    do     
        corpus=../../data/monolingual/$lang/$format.$lang
        lmfile=../../data/lm/$lang/$format.$lang.lm
        $LM_SCRIPT $corpus $order $lmfile & 
    done 
done 

