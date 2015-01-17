import string, codecs, re, os, sys, itertools, functools
import numpy
from srilm import * 
import logging

logger = logging.getLogger(__name__)

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
        self._order=order
        self._lm_model=initLM(order)
        readLM(self._lm_model,lang_model_fname)

class UnigramViterbiDesegmenter(ViterbiDesegmenter):

    def __init__(self, lang_model):
        super(UnigramViterbiDesegmenter,self).__init__(lang_model,1)

    def _score_word(self,morph_sequence,start,end):

        word=u''.join( morph_sequence[start:end] )

        return getUnigramProb(self._lm_model,word.encode('utf-8'))

    def desegment(self,morph_sequence):

        # initialize 
        N=len(morph_sequence)
        total_score=numpy.zeros(N)
        split_tracker=[-1]*N

        logger.debug(  ' '.join([ w+'({})'.format(i) for i,w in enumerate(morph_sequence) ]) )
        # For each word end position look for word end position of prev word and evaluate

        # i: index of end position of word (0 to N-1)   
        # j: index of end position of previous word (-1 to N-2)  

        for i in xrange(N):
            logger.debug('Computing for position {}'.format(i))
            maxj=-1
            max_score= -numpy.inf
            for j in xrange(-1,i):
                # base case: total_score[-1]=0.0
                cur_score=  ( 0.0 if j<0 else total_score[j] ) + \
                            self._score_word(morph_sequence,j+1,i+1)
           
                logger.debug('Score {} {} = {} = {} + {} '.format(i,j,cur_score,( 0.0 if j<0 else total_score[j] ),self._score_word(morph_sequence,j+1,i+1)))
                if cur_score>max_score:
                    max_score=cur_score
                    maxj=j

            total_score[i]=max_score
            split_tracker[i]=maxj
            logger.debug('Best split ending at {} = {}'.format(i,maxj))

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

def _is_child_perm(child_perm,parent_perm):
    return child_perm[:-1] == parent_perm[1:]

def _child_permutation_generator(parent_perm): 
    child_perm_head=list(parent_perm[1:])
    for i in xrange(-1,parent_perm[-1]):
        yield tuple(child_perm_head + [i])

def _is_perm_descending_order(perm): 

        for i in xrange(1,len(perm)):
            if perm[i]>=perm[i-1] and (perm[i]!=-1 and perm[i-1]!=-1):
                return False 
            if perm[i]>perm[i-1] and perm[i-1]==-1:
                return False

        return False if perm[0]==-1 else True 

def _permutation_generator(sent_length,order): 
        """ 
         each element is a pair specifying start and end range for that variable 
        """
        input_list=[range(-1,sent_length)]*(order+1)
        return itertools.ifilter(_is_perm_descending_order,itertools.product(*input_list))

class NgramViterbiDesegmenter(ViterbiDesegmenter):

    def __init__(self, lang_model, order=1): 
        super(NgramViterbiDesegmenter,self).__init__(lang_model,order)


    def _score_ngram(self,morph_sequence,perm):
        words=[]

        if perm[0]==0:
            words.append('<s>')
        else:
            for i in xrange(len(perm)-1): 
                words.append(u''.join(morph_sequence[perm[i+1]+1:perm[i]+1]))
                if perm[i+1]==-1:
                    break

        words.reverse()
        #print u' '.join(words).encode('utf-8')

        return getNgramProb(self._lm_model,u' '.join(words).encode('utf-8'),len(words))

    def desegment(self,morph_sequence):
       
        # add senetence boundary markers 
        morph_sequence.insert(0,'<s>')
        morph_sequence.append('</s>')

        print ' '.join(morph_sequence).encode('utf-8')

        # initialize 
        N=len(morph_sequence)
        total_score={}

        for cur_perm in _permutation_generator(N,self._order): 

            if cur_perm[len(cur_perm)-1]==-1:
                # base case
                total_score[cur_perm]=self._score_ngram(morph_sequence,cur_perm)
            else:    
                max_score= -numpy.inf
                print 'XXXXXXX'
                print cur_perm
                #for hist_perm in itertools.ifilter(functools.partial(_is_child_perm,parent_perm=cur_perm),_permutation_generator(N,self._order)): 
                for hist_perm in  _child_permutation_generator(cur_perm):
                    print hist_perm
                    cur_score= total_score[hist_perm] + self._score_ngram(morph_sequence,cur_perm)

                    if cur_score>max_score:
                        max_score=cur_score

                total_score[cur_perm]=max_score

        # create final desegmented output 

if __name__ == '__main__': 

    logging.basicConfig(level=logging.INFO)
    #deseg=UnigramViterbiDesegmenter(None)

    #m_seq=['a','c','a','a','a','b','a','b','c','b','a',]
    #print deseg.desegment(m_seq)

    #deseg=UnigramViterbiDesegmenter(sys.argv[3])
    deseg=NgramViterbiDesegmenter(sys.argv[3],5)

    with codecs.open(sys.argv[1],'r','utf-8') as infile:
        with codecs.open(sys.argv[2],'w','utf-8') as outfile:
            for line in infile:
                m_seq=line.strip().split(' ')
                #words,wordpos=deseg.desegment(m_seq)
                deseg.desegment(m_seq)
                #outfile.write(' '.join(words)+'\n')

   
