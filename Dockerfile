FROM python:3.6

COPY xtract_keyword_main.py stop-words-en.txt words_dictionary.json /

RUN pip install nltk PyPDF2 rake_nltk
RUN pip install git+https://github.com/Parsl/parsl
RUN pip install git+https://github.com/DLHub-Argonne/home_run

#ENTRYPOINT ["python", "xtract_keyword_rake_main.py"]
