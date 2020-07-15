FROM python:3.6

COPY stop-words-en.txt words_dictionary.json requirements.txt /

RUN pip install -U nltk
RUN pip install -r requirements.txt
RUN pip install git+https://github.com/DLHub-Argonne/home_run

RUN pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
ENV container_version=1

RUN pip install parsl==0.9.0
RUN pip install xtract-sdk==0.0.5
COPY xtract_keyword_main.py / 
