FROM python:latest

MAINTAINER Ryan Wong

# Copy files
COPY stop-words-en.txt corpus.py preprocessing.py vectorizers.py doc_vectors.py pdf_to_text.py xtract_keyword_main.py /

# Install dependencies
RUN pip install nltk numpy pdfminer.six chardet git+https://github.com/Parsl/parsl git+https://github.com/DLHub-Argonne/home_run
RUN python -m nltk.downloader punkt

#ENTRYPOINT ["python", "xtract_keyword_main.py"]
