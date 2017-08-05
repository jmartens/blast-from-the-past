FROM bamos/openface:latest

ADD requirements.txt /root/
RUN pip install -r /root/requirements.txt

WORKDIR /worker/
ADD bftp-scanner/ /worker/

CMD ["python", "main.py", "--path", "/var/bftp/images/"]