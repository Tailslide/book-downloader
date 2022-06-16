# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD ["sh", "-c", "exec python3 -m downloader $NICK $READARR_URL $READARR_API_KEY $LOCAL_TEMP_FOLDER $READARR_TEMP_FOLDER"]
