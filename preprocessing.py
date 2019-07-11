import re
import nltk
import os


def preprocess(doc):
    """Extracts a list of words from a long string, strips punctuation,
    and eliminates short words or stop words, returning a list of tokens.

    Parameter:
    doc (str): Long string to extract tokens from.

    Return:
    tokens (list(str)): A list of tokens extracted from doc.
    """
    current_dir = os.getcwd()
    stop_words = ['\n']
    with open(current_dir + '/stop-words-en.txt', 'r') as f:
        stop_words += [x.strip() for x in f.readlines()]
    tokens = [x for x in nltk.word_tokenize(doc.lower())
              if x not in stop_words and re.match("[a-zA-Z]{2,}", x)]
    return tokens

