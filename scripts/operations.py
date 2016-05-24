import codecs, sys, itertools,string,re
import morfessor 

# globals

SCRIPT_RANGES={
                 'pa':[0x0a00,0x0a7f] ,  
                 'gu':[0x0a80,0x0aff] ,  
                 'or':[0x0b00,0x0b7f] ,  
                 'ta':[0x0b80,0x0bff] ,  
                 'te':[0x0c00,0x0c7f] ,  
                 'kn':[0x0c80,0x0cff] ,  
                 'ml':[0x0d00,0x0d7f] ,  
                 'hi':[0x0900,0x097f] ,  
                 'mr':[0x0900,0x097f] ,   
                 'kK':[0x0900,0x097f] ,   
                 'sa':[0x0900,0x097f] ,   
                 'ne':[0x0900,0x097f] ,   
                 'bn':[0x0980,0x09ff] ,  
                 'as':[0x0980,0x09ff] ,  
              }

COORDINATED_RANGE_START_INCLUSIVE=0
COORDINATED_RANGE_END_INCLUSIVE=0x6f


# patter for removing scripts 

def remove_tags(infname,outfname): 
    with codecs.open(infname,'r','utf-8') as infile: 
        with codecs.open(outfname,'w','utf-8') as outfile: 
            for line in infile: 
                token_tags= [  t.split('\\')[0] for t in line.strip().split(' ')]
                outfile.write( string.join(token_tags,sep=' ') + '\n' )

def count_tokens(infname,outfname):
    with codecs.open(infname,'r','utf-8') as infile: 
        with codecs.open(outfname,'w','utf-8') as outfile: 
            count_map={}
            for line in infile:
                tokens=line.strip().split(' ')
                for token in tokens:
                    count_map[token]=count_map.get(token,0)+1

            for token,count in count_map.iteritems(): 
                if token!='':
                    outfile.write(u'{} {}\n'.format(count, token))

def count_total_tokens(infname):
    with codecs.open(infname,'r','utf-8') as infile: 
        total=0
        for line in infile:
            tokens=line.strip().split(' ')
            for token in tokens:
                total+=1
        print 'Total tokens: {}'.format(total)

def contains_number(text,lang):
    for c in text: 
        offset=ord(c)-SCRIPT_RANGES[lang][0]
        if offset >=0x66 and offset <= 0x6f:
            return True  
    return False     

def morphanalysis_needed(word,lang):
    script_range_pat=ur'^[{}-{}]+$'.format(unichr(SCRIPT_RANGES[lang][0]),unichr(SCRIPT_RANGES[lang][1]))
    script_check_re=re.compile(script_range_pat)
    return script_check_re.match(word) and not contains_number(word,lang)

def morph_analyze(word,model):
    val=model.viterbi_segment(word)
    return string.join(val[0],sep=' ')

def morph_analyze_file(infname,outfname,modelfname,lang):
    # morph model
    io = morfessor.MorfessorIO()
    morph_model=io.read_any_model(modelfname)

    with codecs.open(infname,'r','utf-8') as infile: 
        with codecs.open(outfname,'w','utf-8') as outfile: 
            for line in infile:
                out_tokens=[]
                for word in line.strip().split(' '): 
                    if morphanalysis_needed(word,lang): 
                        morphs=morph_model.viterbi_segment(word)
                        out_tokens.extend(morphs[0])
                    else:
                        out_tokens.append(word)

                outfile.write(string.join(out_tokens,sep=' ')+'\n')

#def filter_counts_file(infname,outfname,lang):
#    with codecs.open(infname,'r','utf-8') as infile: 
#        with codecs.open(outfname,'w','utf-8') as outfile: 
#            for outline in itertools.ifilter( lambda x: morphanalysis_needed( x.strip().split(' ')[1] )  , infile)
#                outfile.write(outline)

def generate_oov(infname,outfname,tar_lang):
    """
      The method simply considers any word which is not a punctuation and has a character not in the target language Unicode range to be an OOV
    """
    tgt_script_tokens_pat=ur'^[{}-{},{}\u0964\u0965]+$'.format(unichr(SCRIPT_RANGES[tar_lang][0]),unichr(SCRIPT_RANGES[tar_lang][1]),string.punctuation)
    tgt_script_tokens_check_re=re.compile(tgt_script_tokens_pat)

    with codecs.open(infname,'r','utf-8') as infile: 
        with codecs.open(outfname,'w','utf-8') as outfile: 
            for line in infile:
                out_tokens=[]
                intokens=[word for word in line.strip().split(' ')] 
                out_tokens=filter(lambda x: tgt_script_tokens_check_re.match(x) is None,intokens)
                outfile.write(string.join(out_tokens,sep=' ')+'\n')
    

if __name__ == '__main__':                
    commands={
             'remove_tags': remove_tags,
             'count_tokens':count_tokens,
             'count_total_tokens':count_total_tokens,
             'morph':morph_analyze_file,
             'generate_oov':generate_oov,
            }

    commands[sys.argv[1]](*sys.argv[2:])

