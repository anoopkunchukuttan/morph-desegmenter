import codecs, re, sys, os, itertools 


from indicnlp.normalize.indic_normalize import IndicNormalizerFactory
from indicnlp.tokenize import indic_tokenize
from indicnlp.morph import unsupervised_morph
from indicnlp import common

def remove_markers(infname,outfname):
    with codecs.open(infname, 'r', 'utf-8') as infile: 
        with codecs.open(outfname, 'w', 'utf-8') as outfile: 
            for line in infile: 
                out_tokens= [ x[:-3] for x in line.strip().split(' ') ]
                outfile.write( u' '.join(out_tokens) + u'\n')                           

def select_lines(infname,outfname,lang):
    """
    To select good lines from the FIRE corpus 
    """
    normalizer=IndicNormalizerFactory().get_normalizer(lang)

    with codecs.open(infname, 'r', 'utf-8') as infile: 
        with codecs.open(outfname, 'w', 'utf-8') as outfile: 
            for line in infile: 
                out_tokens=indic_tokenize.trivial_tokenize(                     # tokenize 
                            normalizer.normalize(line.strip())              # normalize 
                            )
                if len(out_tokens)<7 or out_tokens[-1] not in ['.','?']:
                    continue
                outfile.write( u' '.join(out_tokens) + u'\n')                           

def process_file(infname,outfname,lang,do_segment): 

    normalizer=IndicNormalizerFactory().get_normalizer(lang)
    segmenter=None
    if do_segment:
        segmenter=unsupervised_morph.UnsupervisedMorphAnalyzer(lang,add_marker=True)

    sent_delim = u'\u0964' if lang in ['hi'] else u'.'

    with codecs.open(infname, 'r', 'utf-8') as infile: 
        with codecs.open(outfname, 'w', 'utf-8') as outfile: 
            for line in infile: 
                out_tokens=indic_tokenize.trivial_tokenize(                     # tokenize 
#                            indic_tokenize.triv_tokenizer_pat.sub(' ',       # remove punctuation     
                            normalizer.normalize(line.strip())              # normalize 
#                            ) + sent_delim                                  # restore sentence delimiter
                            )

                if do_segment: 
                    out_tokens=segmenter.morph_analyze_document(out_tokens)
                outfile.write( u' '.join(out_tokens) + u'\n')                           

if __name__=='__main__': 
    common.INDIC_RESOURCES_PATH='/usr/local/bin/indicnlp/indic_nlp_resources/'
    

    #process_file(sys.argv[1],sys.argv[2],sys.argv[3], True if sys.argv[4]=='True' else False)

    #select_lines(sys.argv[1],sys.argv[2],sys.argv[3])


    remove_markers(sys.argv[1],sys.argv[2])
