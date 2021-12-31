from funcx_xtract_keyword import extract_keyword
import re
import os
import time
import json
import decimal
import nltk
import PyPDF2
import argparse
import docx
from rake_nltk import Rake



# TODO: Create a system for xtract_keyword_main to take in arguments
# without explicity sending them in... perhaps a JSON config file?

def execute_extractor(filename):
    """
    Test version 1... let's see if this works. Should be straightforward.
    
    """
    t0 = time.time()
    if not filename:
        return None
    metadata = extract_keyword(file_path=filename)
    t1 = time.time()
    metadata.update({"extract time": (t1 - t0)})
    return metadata


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


def getText(filename):
    doc = docx.Document(filename)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    return '\n'.join(fullText)


class ExtractorRunner:
    def __init__(self, docs, dict_of_words, stop_words, timeout, retry_kb):
        self.docs = docs
        self.word_degrees = None
        
        self.dict_of_words = dict_of_words
        self.stop_words = stop_words

        import multiprocessing as mp
        # print("A")
        pool = mp.Pool(processes=1)
        result = pool.apply_async(self.token_proc_thread, args=(), kwds={})

        must_retry = False
        try:
            # print("B")
            val = result.get(timeout=timeout)
            self.word_degrees = val
        except mp.TimeoutError:
            print(f"Threadpool timed out after {timeout} seconds! Trimming size to {retry_kb}")
            pool.terminate()
            must_retry = True
        else: 
            pool.close()
            pool.join()
            # print("SUCCESS ON FIRST TRY!")
        
        # print("C")
        if must_retry: 
            # print("D?")
            try:
                bytes_to_read = retry_kb * 1024
                if len(self.docs) > retry_kb:
                    self.docs = self.docs[0:1024]
                    pool = mp.Pool(processes=1)
                    result = pool.apply_async(self.token_proc_thread, args=(), kwds={})
                
                    val = result.get(timeout=timeout)
            except mp.TimeoutError:
                print(f"Threadpool timed out second time on {retry_kb}. It is likely these are not freetext data...")
                pool.terminate()
            else:
                pool.close()
                pool.join()
                self.word_degrees = val
                # print("SUCCESS ON SECOND TRY!")

        print(f"Great job! Word degrees: {self.word_degrees}")
            


    def token_proc_thread(self): 
        tokens = []

        # print("YO")
        tokens.extend([x for x in nltk.word_tokenize(self.docs.lower()) if re.match("[a-zA-Z]{2,}", x)])
        for word in tokens[:]:
            try:
                if not(word.lower() in self.dict_of_words.keys()):
                    tokens.remove(word)
            except:
                pass
        tokens = ' '.join(map(str, tokens))

        r = Rake(stopwords=self.stop_words)
        r.extract_keywords_from_text(tokens)
        # word_degrees = []
        word_degrees = sorted(r.get_word_degrees().items(), key=lambda item: item[1], reverse=True)
        print(word_degrees)
        for word_tuple in word_degrees[:]:
            if len(word_tuple[0]) <= 4:
                word_degrees.remove(word_tuple)
        
        return word_degrees
    

# TODO: Find a smarter way to filter out junk words that slip through the english word check
# def extract_keyword(file_path, text_string=None, top_n=20, pdf=False):
def extract_keyword(file_path, text_string=None, top_n=50, timeout=180, retry_kb=10):
    """Extracts keywords from a file.

    Parameters:
    file_path (str): File path of file to extract keywords from.
    text_string (str): String of text to extract keywords from.
    top_n (int): Number of keywords to return.

    Return:
    metadata (dict): Dictionary containing top_n words and their scores.
    """
    t0 = time.time()
    package_dir = os.path.dirname(__file__) + "/"
    # package_dir = ""  # TODO: TYLER

    stop_words = ['\n']
    pdf = False

    is_docx = False
    if file_path.endswith('.pdf'):
        pdf = True
    if file_path.endswith('.docx'):
        is_docx = True
    with open(f'{package_dir}stop-words-en.txt', 'r') as f:
        stop_words += [x.strip() for x in f.readlines()]
    with open(f'{package_dir}words_dictionary.json', 'r') as words_file:
        dict_of_words = json.load(words_file)
    
    try: 
        if text_string is not None:
            docs = text_string
        elif pdf:
            docs = pdf_to_text(file_path)
        elif is_docx:
            docs = getText(file_path)
        else:
            docs = read_files(file_path)

        if docs == None:
            return {'keywords': None, 'message': "Unable to extract text"}
    
    except decimal.InvalidOperation as e:
        return {'keywords': None, 'message': f"Decimal Error: {e}"}
    except ValueError as e: 
        return {'keywords': None, 'message': f"ValueError: {e}"}
    
    xtr_runner = ExtractorRunner(docs=docs, dict_of_words=dict_of_words, stop_words=stop_words, timeout=timeout, retry_kb=retry_kb)
    
    metadata = {"keywords": {}}
    
    word_degrees = xtr_runner.word_degrees
    if len(xtr_runner.word_degrees) >= top_n:
        metadata["keywords"].update(xtr_runner.word_degrees[:top_n])
    else:
        metadata["keywords"].update(xtr_runner.word_degrees)
    metadata.update({"extract time": time.time() - t0})

    return metadata


if __name__ == "__main__":
    """Takes file paths from command line and returns metadata.

    Arguments:
    --path (File path): File path of text file.

    Returns:
    meta (insert type here): Metadata of text file.
    t1 - t0 (float): Time it took to retrieve text metadata.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('--path', help='Filepath to extract keywords from',
                        required=True, type=str)
    parser.add_argument('--text_string', help='Filepath to extract keywords from',
                        default=None, type=str)
    parser.add_argument('--top_words', help='Number of words to return',
                        default=10)

    args = parser.parse_args()
    meta = extract_keyword(args.path, args.text_string, args.top_words)
    print(meta)
