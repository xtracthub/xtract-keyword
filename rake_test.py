from rake_nltk import Rake
import nltk
import re
import enchant
import os
import time

d = enchant.Dict('en_US')


def read_files(files):
    '''Reads in each file in files and returns a list of docs'''
    docs = list()
    for name in files:
        with open(name, 'rb') as f:
            t = f.read()
            t = t.decode('utf-8', errors='replace')
            docs.append(t)
    return docs


def extract_with_rake(file_path):
    docs = read_files([file_path])
    tokens = []

    stop_words = ['\n']
    with open(os.getcwd() + '/stop-words-en.txt', 'r') as f:
        stop_words += [x.strip() for x in f.readlines()]

    for doc in docs:
        tokens.extend([x for x in nltk.word_tokenize(doc.lower()) if re.match("[a-zA-Z]{2,}", x)])

    for idx, word in enumerate(tokens):
        #print(word)
        try:
            word.decode('utf-8')
            if not d.check(word):
                #print("false " + word)
                del tokens[idx]
            #else:
                #print("true " + word)
        except:
            #print("false " + word)
            del tokens[idx]
    tokens = ' '.join(map(str, tokens))
    print(tokens)
    r = Rake(stopwords=stop_words)
    r.extract_keywords_from_text(tokens)
    word_degrees = sorted(r.get_word_degrees().items(), key=lambda item: item[1], reverse=True)
    print(word_degrees)

t0 = time.time()
extract_with_rake(r"/Users/Ryan/Documents/CS/CDAC/official_xtract/sampler_dataset/pub8/CdiacBundles/35MJ/metadata_coli12mar24mar2015.doc")
#extract_with_rake("test_files/freetext")
print(time.time() - t0)