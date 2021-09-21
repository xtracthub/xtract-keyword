#!/bin/bash

IMAGE_NAME='xtract-keyword'

docker rmi -f $IMAGE_NAME

docker build -t $IMAGE_NAME .

#ENTRYPOINT ["python", "xtract_keyword_main.py"]
