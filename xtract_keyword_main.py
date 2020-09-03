import re
import time
import json
import nltk
import PyPDF2
import argparse
import logging
import xlrd
import zipfile
from rake_nltk import Rake

from io import BytesIO, StringIO
from itertools import chain
from PIL import Image
from markdown import markdown
from xlrd.sheet import ctype_text

from pptx import Presentation

from xml.dom.minidom import parseString
try:
    from xml.etree.cElementTree import XML
except ImportError:
    from xml.etree.ElementTree import XML

ENCODING = 'utf-8'

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

def process_text(file_bytes, ext):

    image = set(['jpg', 'jpeg', 'png', 'tiff', 'tif', 'gif', 'bmp'])
    video = set(['3gp', '3g2', 'avi', 'f4v', 'flv', 'm4v', 'asf', 'wmv', 'mpeg', 'mp4', 'qt'])
    document = set(['txt', 'rtf', 'dotx', 'dot', 'odt', 'pages', 'tex',
                    'pdf', 'ps', 'eps', 'prn', 'md', 'py', 'java', 'scala'])
    open_office = set(['odt', 'ott', 'odm', 'oth', 'ods', 'ots', 'odg',
                       'otg', 'odp', 'otp', 'odf', 'odb', 'odp'])
    doc_x = set(['docx', 'doc'])
    web = set(['html', 'xhtml', 'php', 'js', 'xml', 'war', 'ear' 'dhtml', 'mhtml'])
    spreathseet =  set(['xls', 'xlsx', 'xltx', 'xlt', 'ods', 'xlsb', 'xlsm', 'xltm'])
    presentation = set(['ppt', 'pptx', 'pot', 'potx', 'ppsx',
                        'pps', 'pptm', 'potm', 'ppsm', 'key'])

    text = None

    if ext is None:
        return None

    if ext == "pdf":
        text = pdf_to_text(file_bytes, ENCODING)
    elif ext == "csv":
        text = csv_text_encode(file_bytes, ENCODING)
    elif ext == "tsv":
        text = csv_text_encode(file_bytes, ENCODING, "\t")
    elif ext == "doc":
        text = doc_text_encode(file_bytes, ENCODING)
    elif ext == "rtf":
        text = None #general_text_extract(file_bytes, ENCODING, "rtf")
    elif ext == "md":
        text = md_text_encode(file_bytes, ENCODING)
    elif ext == "html":
        text = general_text_extract(file_bytes, ENCODING, "html")
    elif ext == "json":
        text = None #general_text_extract(file_bytes, ENCODING, "json")
    elif ext in doc_x:
        text = docx_text_encode(file_bytes, ENCODING)
    elif ext in open_office:
        text = open_office_text_encode(file_bytes, ENCODING)
    elif ext in document:
        text = pure_text_encode(file_bytes, ENCODING)
    elif ext in image:
        text = img_text_encode(file_bytes, ENCODING)
    elif ext in spreathseet:
        text = spreadsheet_text_encode(file_bytes, ENCODING)
    elif ext in presentation:
        text = pptx_text_encode(file_bytes, ENCODING)

    if text is None:
        logging.info("Unprocessing extension: {0}".format(ext))

    return text

def pure_text_encode(f_bytes, encoding):
    return f_bytes.decode(encoding)

def csv_text_encode(f_bytes, encoding, delim = ","):
    return f_bytes.decode(encoding).replace(delim, " ")

def pdf_to_text(f_bytes, encoding):

    count = 0
    text = ""

    pdf_reader = PyPDF2.PdfFileReader(BytesIO(f_bytes))
    num_pages = pdf_reader.numPages
    while count < num_pages:
        pageObj = pdf_reader.getPage(count)
        count += 1
        text += pageObj.extractText()

    return text

def img_text_encode(f_bytes, encoding):
    im_to_txt = Image.open(BytesIO(f_bytes))
    return pytesseract.image_to_string(img)

def xml_text_encode(f_bytes, encoding):

    doc = parseString(f_bytes)
    paragraphs = doc.getElementsByTagName('text:p')

    text = [str(ch.data) for ch in filter(\
                                     lambda x: x.nodeType == x.TEXT_NODE, \
                                     chain(*[p.childNodes for p in paragraphs]))]
    return " ".join(text)

def open_office_text_encode(f_bytes, encoding):

    """
    Open office files are essentially zipped archives. The key file
    is the content.xml file within the archive, which can then
    be parsed to extract the text.
    """

    open_office_file = zipfile.ZipFile(BytesIO(f_bytes))
    return xml_text_encode(open_office_file.read('content.xml'), encoding)


#This could be improved...
def spreadsheet_text_encode(f_bytes, encoding):

    #UTF-8 is assumed for encoding, which isn't great. May want to modify later.

    wb = xlrd.open_workbook(file_contents = f_bytes)
    text = []
    for sheet in wb.sheets():
        for row in sheet.get_rows():
            filtered_row = filter(lambda x: ctype_text.get(x.ctype, 'not_text') == 'text', row)
            filtered_row = [s.value for s in filtered_row]
            text += [" ".join(filtered_row)]
    return " ".join(text)

#Reference: https://etienned.github.io/posts/extract-text-from-word-docx-simply/
def docx_text_encode(f_bytes, encoding):
    """
    Take the path of a docx file as argument, return the text in unicode.
    """

    WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    PARA = WORD_NAMESPACE + 'p'
    TEXT = WORD_NAMESPACE + 't'

    document = zipfile.ZipFile(BytesIO(f_bytes))
    xml_content = document.read('word/document.xml')
    document.close()
    tree = XML(xml_content)

    paragraphs = []
    for paragraph in tree.getiterator(PARA):
        texts = [node.text
                 for node in paragraph.getiterator(TEXT)
                 if node.text]
        if texts:
            paragraphs.append(''.join(texts))

    return '\n\n'.join(paragraphs)

def general_text_extract(f_bytes, encoding, ext):

    f_type = "_." + ext
    return fulltext.get(BytesIO(f_bytes), name = f_type)

def md_text_encode(f_bytes, encoding):
    html = markdown(f_bytes.decode('utf-8'))
    return fulltext.get(StringIO(html), name = "_.html")

def doc_text_encode(f_bytes, encoding):

    fake_fname = "_.doc"
    with open(fake_fname, "wb") as of:
        of.write(f_bytes)

    text = os.popen("antiword " + fake_fname).read()
    os.system("shred -u " + fake_fname)

    return text

def pptx_text_encode(f_bytes, encoding):

    prs = Presentation(BytesIO(f_bytes))

    text = ""

    for sld in prs.slides:
        for shape in sld.shapes:
            if not shape.has_text_frame:
                continue
            for p in shape.text_frame.paragraphs:
                text += str(p.text) + "\n"

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

    with open('/stop-words-en.txt', 'r') as f:
        stop_words += [x.strip() for x in f.readlines()]
    with open('/words_dictionary.json', 'r') as words_file:
        dict_of_words = json.load(words_file)

    if text_string is not None:
        docs = text_string
    elif pdf:
        docs = pdf_to_text(file_path)
    else:
        docs = read_files(file_path)

    if docs == None:
        return {'keywords': None, 'message': "Unable to extract text"}

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

    metadata = {"keywords": {}, "full_text": {}}
    metadata["keywords"].update(word_degrees[:top_n])
    metadata["full_text"] = docs
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
    parser.add_argument('--ext', help='File extension', default=None)

    args = parser.parse_args()

    #meta = pdf_to_text(args.path)

    with open(args.path, 'rb') as of:
        text = process_text(of.read(), args.ext)

    meta = extract_keyword(args.path, args.text_string or text, args.top_words, args.pdf)
    print(meta)
