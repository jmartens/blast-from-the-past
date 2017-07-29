FROM bamos/openface:latest

ADD . /worker
WORKDIR /worker

RUN pip install -r requirements.txt

CMD ["python", "bftp-scanner/main.py", "/opt/bftp/worker/"]