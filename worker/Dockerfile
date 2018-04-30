FROM bamos/openface:latest

ADD requirements.txt /root/

RUN pip install --upgrade pip
RUN pip install -r /root/requirements.txt

WORKDIR /app
ADD bftp-scanner/ /app/

CMD ["python", "main.py", "--path", "/app/static/images/"]