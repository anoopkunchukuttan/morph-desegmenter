import sys, codecs, re
from indicnlp import langinfo

def parse_meteor_file(fname): 
    with codecs.open(fname,'r','utf-8') as infile:
        lines=infile.readlines()

        fs=float(lines[-1].split(':')[1].strip())
        recall=float(lines[-6].split(':')[1].strip())
        precision=float(lines[-7].split(':')[1].strip())

        return (fs,precision,recall)

def parse_bleu_file(fname): 
    with codecs.open(fname,'r','utf-8') as infile:
        line=infile.readline()
        finalbleu=line.split('=')[1].split(',')[0].strip()
        bleu_1=line.split(',')[1].split('/')[0].strip()

        return (finalbleu,bleu_1)

def count_oov(fname,src,tgt):

    script_range_pat=ur'^[{}-{}]+$'.format(unichr(langinfo.SCRIPT_RANGES[src][0]),unichr(langinfo.SCRIPT_RANGES[src][1]))
    script_check_re=re.compile(script_range_pat)

    n_oov=0
    with codecs.open(fname,'r','utf-8') as infile:
        for line in infile:
            n_oov+=len(filter(script_check_re.match,line.split(' ')))
    
    return n_oov

if __name__ =='__main__':

    resdir=sys.argv[1]
    src='hi'
    tgts=['bn','ta','te','mr','ml']
    #src='ta'
    #tgts=['ml']
    
    # example line 
    # BLEU = 16.42, 43.1/21.0/11.9/6.8 (BP=0.998, ratio=0.998, hyp_len=41311, ref_len=41409)
   

    for tgt in tgts:
      
        #### BLEU 

        ## word based system
        #idx=0
    
        ## unseg output
        #f_wu='{resdir}/{src}-{tgt}/word/evaluation/results_with_tuning/bleu.txt'.format(resdir=resdir,src=src,tgt=tgt)
        #o_wu=parse_bleu_file(f_wu)
    
        ##segmented output
        #f_ws='{resdir}/{src}-{tgt}/word/evaluation/test.seg.{tgt}.bleu'.format(resdir=resdir,src=src,tgt=tgt)
        #o_ws=parse_bleu_file(f_ws)
        #

        ## morph marker based system 
    
        ## unseg output
        #f_mu='{resdir}/{src}-{tgt}/morph_marker/evaluation/test.deseg.{tgt}.bleu'.format(resdir=resdir,src=src,tgt=tgt)
        #o_mu=parse_bleu_file(f_mu)
    
        ##segmented output
        #f_ms='{resdir}/{src}-{tgt}/morph_marker/evaluation/results_with_tuning/bleu.txt'.format(resdir=resdir,src=src,tgt=tgt)
        #o_ms=parse_bleu_file(f_ms)
    
        #print '{}-{}|{}|{}|{}|{}'.format(src,tgt,o_wu[idx],o_mu[idx],o_ws[idx],o_ms[idx])

        ####### count number of oovs

        #t_w="{resdir}/{src}-{tgt}/word/evaluation/test.{tgt}".format(resdir=resdir,src=src,tgt=tgt)
        #t_m='{resdir}/{src}-{tgt}/morph_marker/evaluation/test.deseg.{tgt}'.format(resdir=resdir,src=src,tgt=tgt)

        #oov_w=count_oov(t_w,src,tgt)
        #oov_m=count_oov(t_m,src,tgt)

        #print '{}-{}|{}|{}'.format(src,tgt,oov_w,oov_m)


        ##### compute METEOR
        mtf_m='{resdir}/{src}-{tgt}/morph_marker/evaluation/test.deseg.{tgt}.meteor'.format(resdir=resdir,src=src,tgt=tgt)
        mto_m=parse_meteor_file(mtf_m)
        mtf_w='{resdir}/{src}-{tgt}/word/evaluation/results_with_tuning/meteor.txt'.format(resdir=resdir,src=src,tgt=tgt)
        mto_w=parse_meteor_file(mtf_w)

        idx=2
        print '{}-{}|{:.2f}|{:.2f}'.format(src,tgt,mto_w[idx]*100,mto_m[idx]*100)
