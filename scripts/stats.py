from indicnlp.normalize.indic_normalize import IndicNormalizerFactory
from indicnlp.tokenize import indic_tokenize  
import sys, codecs

remove_nuktas=False
factory=IndicNormalizerFactory()
normalizer=factory.get_normalizer(sys.argv[2],remove_nuktas)

type_counts={}
token_count=0

with codecs.open(sys.argv[1],'r','utf-8') as infile:
    for s in infile: 
        normalized=normalizer.normalize(s.strip())
        for w in indic_tokenize.trivial_tokenize(normalized):
            type_counts[w]=type_counts.get(w,0)+1
            token_count+=1

print "Token to type ratio: {}".format(float(token_count)/float(len(type_counts.keys())))
print "Weighted Average type length: {}".format(
        float( reduce( lambda l1,w2: len(w2)*type_counts[w2]+l1 , type_counts.keys() ,0  ) ) / float(token_count)  )
print "Average type length: {}".format(
        float( reduce( lambda l1,w2: len(w2)+l1 , type_counts.keys() ,0  ) ) / float(len(type_counts.keys()))  )
