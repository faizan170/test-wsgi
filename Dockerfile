FROM tiangolo/uwsgi-nginx-flask:python3.6

COPY ./requirements.txt .
RUN pip install -r requirements.txt
RUN pip install imutils
COPY ./app /app