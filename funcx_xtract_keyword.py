import re
import time
import json
import decimal
import nltk
import PyPDF2
import argparse
from rake_nltk import Rake
# import tabula

def read_files(file):
    """Reads a file and returns a string of contents.

    Parameter:
    file (str): File path to file to extract contents of.

    Return:
    docs (str): String of contents from file.
    """
    docs = ""
    with open(file, 'rb') as f:
        t = f.read()
        t = t.decode('utf-8', errors='replace')
        docs += t
    return docs


def pdf_to_text(filepath):
    count = 0
    text = ""

    with open(filepath, 'rb') as pdfFileObj:
        pdf_reader = PyPDF2.PdfFileReader(pdfFileObj)
        num_pages = pdf_reader.numPages

        while count < num_pages:
            pageObj = pdf_reader.getPage(count)
            count += 1
            text += pageObj.extractText()

    if text == "":
        # Try another method here...
        return None
    return text

# TODO: Find a smarter way to filter out junk words that slip through the english word check
def extract_keyword(file_path, text_string=None, top_n=20, pdf=False):
    """Extracts keywords from a file.

    Parameters:
    file_path (str): File path of file to extract keywords from.
    text_string (str): String of text to extract keywords from.
    top_n (int): Number of keywords to return.

    Return:
    metadata (dict): Dictionary containing top_n words and their scores.
    """
    t0 = time.time()
    tokens = []
    stop_words = ['\n']

    with open('stop-words-en.txt', 'r') as f:
        stop_words += [x.strip() for x in f.readlines()]
    with open('words_dictionary.json', 'r') as words_file:
        dict_of_words = json.load(words_file)
    
    try: 
        if text_string is not None:
            docs = text_string
        elif pdf:
            docs = pdf_to_text(file_path)
        else:
            docs = read_files(file_path)

        if docs == None:
            return {'keywords': None, 'message': "Unable to extract text"}
    
    except decimal.InvalidOperation as e:
        return {'keywords': None, 'message': f"Decimal Error: {e}"}
    except ValueError as e: 
        return {'keywords': None, 'message': f"ValueError: {e}"}

    tokens.extend([x for x in nltk.word_tokenize(docs.lower()) if re.match("[a-zA-Z]{2,}", x)])
    for word in tokens[:]:
        try:
            if not(word.lower() in dict_of_words.keys()):
                tokens.remove(word)
        except:
            pass
    tokens = ' '.join(map(str, tokens))

    r = Rake(stopwords=stop_words)
    r.extract_keywords_from_text(tokens)
    word_degrees = sorted(r.get_word_degrees().items(), key=lambda item: item[1], reverse=True)

    for word_tuple in word_degrees[:]:
        if len(word_tuple[0]) <= 4:
            word_degrees.remove(word_tuple)

    metadata = {"keywords": {}}
    metadata["keywords"].update(word_degrees[:top_n])
    metadata.update({"extract time": time.time() - t0})

    return metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', help='Filepath to extract keywords from',
                        required=False, type=str)
    parser.add_argument('--text_string', help='Filepath to extract keywords from',
                        default=None, type=str)
    parser.add_argument('--top_words', help='Number of words to return',
                        default=10)
    parser.add_argument('--pdf', help='Bool is pdf', default=True)

    args = parser.parse_args()

    #meta = pdf_to_text(args.path)
    meta = extract_keyword(args.path, args.text_string, args.top_words, args.pdf)
    print(meta)
