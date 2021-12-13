FROM python:3.6

COPY stop-words-en.txt words_dictionary.json requirements.txt /

RUN pip install -U nltk
RUN pip install -r requirements.txt
# RUN python -m nltk.downloader all
# RUN pip install git+https://github.com/DLHub-Argonne/home_run
# RUN wget https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/tokenizers/punkt.zip && unzip punkt.zip
# RUN mkdir tokenizers

# RUN mv /punkt tokenizers
RUN python -m nltk.downloader punkt

# RUN pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
ENV container_version=1.0

# RUN pip install parsl==0.9.0
RUN pip install xtract-sdk==0.0.7a2
RUN pip uninstall globus_sdk -y && pip install globus_sdk==2.0.1
COPY xtract_keyword_main.py funcx_xtract_keyword.py / 
