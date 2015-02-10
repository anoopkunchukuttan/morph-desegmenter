import string, codecs, re, os, sys, itertools, functools
import numpy
from srilm import * 
import logging

logger = logging.getLogger(__name__)

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


class MarkerDesegmenter(DesegmenterI):
    def __init__(self):
        self.P='P' #prefix
        self.S='S' #suffix
        self.R='R' #root
        self.E='E' #other like numbers, punctuations which are not morph analyzed 
        self.DELIMITER='_'

    def desegment(self,morph_sequence):

        marker_tags=[ x[-3:].strip(self.DELIMITER)  for x in morph_sequence ]
        true_morpheme_sequence=[ x[:-3] for x in morph_sequence ]

        word_list=[]
        desegment_list=[]

        desegment_list.append(0)
        cur_word=[]
        for i in xrange(len(true_morpheme_sequence)):
            cur_word.append(true_morpheme_sequence[i])

            if (i==len(true_morpheme_sequence)-1) or \
                (marker_tags[i],marker_tags[i+1]) not in \
                [ (self.R,self.S), (self.S,self.S), (self.P,self.P), (self.P,self.R), ] :
                word_list.append(''.join(cur_word))
                cur_word=[]

                if (i!=len(true_morpheme_sequence)-1):
                    desegment_list.append(i+1)

        return (word_list,desegment_list)

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
    
    def _ngram_from_perm(self,morph_sequence,perm): 
        words=[]

        for i in xrange(len(perm)-1): 
            words.append(u''.join(morph_sequence[perm[i+1]+1:perm[i]+1]))
            if perm[i+1]==-1:
                break

        return words                

    def _score_ngram(self,morph_sequence,perm):

        words=self._ngram_from_perm(morph_sequence,perm)
        words.reverse()
        #print u' '.join(words).encode('utf-8')

        val = getNgramProb(self._lm_model,u' '.join(words).encode('utf-8'),len(words))
        #return val 
        return -5.0 if val==-99.0 else val 

    def desegment(self,morph_sequence):
       
        # add senetence boundary markers 
        morph_sequence.insert(0,'<s>')
        morph_sequence.append('</s>')

        logger.debug(  ' '.join([ w+'({})'.format(i) for i,w in enumerate(morph_sequence) ]) )

        # initialize 
        N=len(morph_sequence)
        total_score={}
        split_tracker={}

        for cur_perm in _permutation_generator(N,self._order): 

            logger.debug('Computing for substring ending in ngram: {}'.format( ' '.join([str(x) for x in cur_perm]) ) ) 
            logger.debug(u'Details: {}'.format (  u' '.join(reversed(self._ngram_from_perm(morph_sequence,cur_perm))) ) )

            if cur_perm[len(cur_perm)-1]==-1:
                # base case
                total_score[cur_perm]=self._score_ngram(morph_sequence,cur_perm)
                split_tracker[cur_perm]=None
            else:    
                max_score= -numpy.inf
                best_split=None

                #for hist_perm in itertools.ifilter(functools.partial(_is_child_perm,parent_perm=cur_perm),_permutation_generator(N,self._order)): 
                for hist_perm in  _child_permutation_generator(cur_perm):
                    cur_score= total_score[hist_perm] + self._score_ngram(morph_sequence,cur_perm)

                    logger.debug('Child perm: {} : {} '.format( ' '.join([str(x) for x in hist_perm]) ,  total_score[hist_perm] ) ) 
                    #logger.debug(u'Details: {}'.format (  u' '.join(reversed(self._ngram_from_perm(morph_sequence,hist_perm))) ) )
                    logger.debug(cur_score)

                    if cur_score>max_score:
                        max_score=cur_score
                        best_split=hist_perm

                total_score[cur_perm]=max_score
                split_tracker[cur_perm]=best_split

        # create final desegmented output 
        print '********* finding best desegmentation ********'
        word_list=[]
        desegment_list=[]

        best_ngram,score=max(itertools.ifilter(lambda x: x[0][0]==N-1 , total_score.iteritems()),
                                key=lambda x: x[1] )
        print best_ngram
        
        word_list.extend( self._ngram_from_perm(morph_sequence,best_ngram)  )
        #TODO desegment list inti

        condition=True 
        while best_ngram[-1]!=-1:

            best_ngram=split_tracker[best_ngram]
            print best_ngram

            # extract word 
            word=''.join( morph_sequence[best_ngram[-1]+1:best_ngram[-2]+1] )

            # construct sentence frag
            word_list.append(word)
            desegment_list.append(best_ngram[-1]+1)

            # termination condition 
            condition=best_ngram[-1]!=-1

        word_list.reverse()
        desegment_list.reverse()
        return (word_list,desegment_list)

if __name__ == '__main__': 

    logging.basicConfig(level=logging.INFO)


    ## test the Marker Desegmenter
    ## good input
    #morph_list= ['worker_R_', 's_S_', 'want_R_', 'to_R_', 'post_P_', 'pone_R_', 'the_R_', 'meeting_R_', ',_E_', 'due_R_ ', 'to_R_', 'the_R_', 'vacation_R_', 's_S_', '._E_']
    ## bad input
    #morph_list= ['worker_R_', 'want_R_', 'to_R_', 's_S_', 'post_P_', 'pone_R_', 'the_R_', 'meeting_R_', ',_E_', 'due_R_ ', 'to_R_', 'the_R_', 'vacation_R_', 's_S_', '._E_']
    #deseg=MarkerDesegmenter()
    #print deseg.desegment(morph_list)

    #deseg=MarkerDesegmenter()
    deseg=UnigramViterbiDesegmenter(sys.argv[3])
    #deseg=NgramViterbiDesegmenter(sys.argv[3],2)

    with codecs.open(sys.argv[1],'r','utf-8') as infile:
        with codecs.open(sys.argv[2],'w','utf-8') as outfile:
            for line in infile:
                m_seq=line.strip().split(' ')
                words,wordpos=deseg.desegment(m_seq)
                outfile.write(' '.join(words)+'\n')

    ###### testing language modelling
    ##text= u'\u0938\u094d\u0935\u091a\u094d\u091b \u0909\u091a\u094d\u091b\u094d\u0935\u093e\u0938 \u0906\u0923\u093f \u0926\u093e\u0924 \u0939\u0947 \u0906\u092a\u0932\u0947 \u0935\u094d\u092f\u0915\u094d\u0924\u093f\u092e\u0924\u094d\u0935 \u0916\u0941\u0932\u0935\u0924\u0940\u0932 .'
    #text= u'\u0938\u094d\u0935\u091a\u094d\u091b \u0909\u091a\u094d\u091b\u094d\u0935\u093e\u0938 \u0906\u0923\u093f \u0926\u093e\u0924 \u0939\u0947 \u0906\u092a\u0932\u0947 \u0935\u094d\u092f\u0915\u094d\u0924\u093f\u092e\u0924\u094d\u0935 \u0916\u0941\u0932\u0935\u0924\u0940\u0932 \u0905\u0928\u0942\u092a .' 

    #words=text.split(' ')
    #print len(words)
    #print 

    #order=5
    #lm_model=initLM(order)
    #readLM(lm_model,sys.argv[3])

    #sprob = getSentenceProb(lm_model,text.encode('utf-8'),len(words))
    #print sprob

    #words.insert(0,'<s>')
    #words.append('</s>')
    #
    #print 

    #cprob=0.0
    #for i in xrange(0,len(words)-order+1):
    #    ws=u' '.join(words[i:i+order])
    #    print ws.encode('utf-8')
    #    sc=getNgramProb(lm_model,ws.encode('utf-8'),order)
    #    cprob+=sc
    #    print sc

    #for i in xrange(2,order):        
    #    ws=u' '.join(words[0:i])
    #    print ws.encode('utf-8')
    #    sc=getNgramProb(lm_model,ws.encode('utf-8'),i)
    #    cprob+=sc
    #    print sc

    #print
    #print cprob
