from doc_vectors import docs_to_keywords, files_to_keywords, directory_to_keywords
from pdf_to_text import extract_Text_Directly
import argparse
import time


class BadFreetextTypeException(Exception):
    """Throw this when we can't process a file. Means the input is bad. """


def extract_keyword(type_arg, target_path):

    if type_arg == 'subtext':
        # Add document as string (for partial file).
        keywords = docs_to_keywords([target_path])

    elif type_arg == 'file':

        if target_path.endswith(".pdf"):
            keywords = docs_to_keywords([extract_Text_Directly(target_path)])

        else:
            keywords = files_to_keywords([target_path])[0]

    elif type_arg == 'directory':
        # Add directory full of documents represented as files.
        keywords = directory_to_keywords(target_path)

    else:
        raise BadFreetextTypeException("Bad format for freetext topic extractor. ")

    ex_freetext = {"type": type_arg, "keywords": {}}
    for item in keywords:
        if len(item[0]) > 20:
            ex_freetext = None
            break
        ex_freetext["keywords"][item[0]] = str(item[1])

    return ex_freetext


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', help='subtext, file, or directory',
                        required=True, type=str)
    parser.add_argument('--path', help='Document as a string, filepath, '
                                       'or directory path',
                        required=True, type=str)

    args = parser.parse_args()

    t0 = time.time()
    meta = {"keyword": extract_keyword(args.type, args.path)}
    print(meta)
    t1 = time.time()
    print(t1 - t0)






