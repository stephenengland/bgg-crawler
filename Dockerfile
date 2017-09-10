FROM python:3.6.1

WORKDIR /opt/app/

CMD ["python", "-u", "./main.py"]

ADD requirements.txt /opt/app/requirements.txt
RUN pip install -r /opt/app/requirements.txt

ADD src /opt/app/