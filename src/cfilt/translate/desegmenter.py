import string, codecs, re, os, sys
import numpy
from srilm import * 

w_score= {  'ac':10,
            'aaa':100,
            'b':4,
            'abcba':10
         }                

class DesegmenterI(object): 

    def desegment(morph_sequence):
        """
        Desegments the input morpheme sequence and returns the sentence

        @params
        morph_sequence: list of morphemes

        @return (sentence, desegment_list)
            word_list: list of words after desegmentation
            desegment_list: list of indices of start of word positions after desegmentation
        """
        pass 


class ViterbiDesegmenter(DesegmenterI): 
    def __init__(self, lang_model_fname, order): 
        self._lm_model=initLM(order)
        readLM(self._lm_model,lang_model_fname)

class UnigramViterbiDesegmenter(ViterbiDesegmenter):

    def __init__(self, lang_model, order=1): 
        super(UnigramViterbiDesegmenter,self).__init__(lang_model,order)

    def _score_word(self,morph_sequence,start,end):

        word=u''.join( morph_sequence[start:end] )
        #return w_score.get(word,0.0)

        return getUnigramProb(self._lm_model,word.encode('utf-8'))

    def desegment(self,morph_sequence):

        # initialize 
        N=len(morph_sequence)
        total_score=numpy.zeros(N)
        split_tracker=[-1]*N

        # For each word end position look for word end position of prev word and evaluate

        # i: index of end position of word (0 to N-1)   
        # j: index of end position of previous word (-1 to N-2)  

        for i in xrange(N):
            maxj=0
            max_score= -numpy.inf
            for j in xrange(-1,i):
                # base case: total_score[-1]=0.0
                cur_score=  ( 0.0 if j<0 else total_score[j] ) + \
                            self._score_word(morph_sequence,j+1,i+1)
            
                if cur_score>max_score:
                    max_score=cur_score
                    maxj=j

            total_score[i]=max_score
            split_tracker[i]=maxj

        # create final desegmented output 
        word_list=[]
        desegment_list=[]

        wend=N-1
        condition=True
        while condition:
            p_wend=split_tracker[wend]
            word=''.join( morph_sequence[p_wend+1:wend+1] )
            word_list.insert(0,word)
            desegment_list.insert(0,p_wend+1)
            wend=p_wend 
            condition=wend!=-1 

        return (word_list,desegment_list)


if __name__ == '__main__': 

    #deseg=UnigramViterbiDesegmenter(None)

    #m_seq=['a','c','a','a','a','b','a','b','c','b','a',]
    #print deseg.desegment(m_seq)

    deseg=UnigramViterbiDesegmenter(sys.argv[2])

    import itertools
    with codecs.open(sys.argv[1],'r','utf-8') as infile:

        for line in itertools.islice(infile.readlines(),10):
            m_seq=line.strip().split(' ')
            print 'Input'
            print ' '.join(m_seq).encode('utf-8')
            print 'Output'
            words,wordpos=deseg.desegment(m_seq)
            print ' '.join(words).encode('utf-8')

