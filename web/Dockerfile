FROM django

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /usr/src/app
ADD . /usr/src/app/

CMD [ "python", "manage.py", "runserver",  "0.0.0.0:8000" ]