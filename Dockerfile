FROM python:3.6

COPY xtract_keyword_main.py stop-words-en.txt words_dictionary.json requirements.txt /

RUN pip install -U nltk
RUN pip install -r requirements.txt
RUN pip install git+https://github.com/Parsl/parsl git+https://github.com/DLHub-Argonne/home_run

#ENTRYPOINT ["python", "xtract_keyword_main.py"]
