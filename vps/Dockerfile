FROM python:3.7-slim

EXPOSE 5000

WORKDIR /app

COPY requirements.txt /tmp/
RUN \
pip install --no-cache-dir -r /tmp/requirements.txt

RUN \
openssl req -x509 -newkey rsa:4096 -nodes -out /tmp/us.crt -keyout /tmp/us.key -days 365 -subj "/C=RU/ST=/L=/O=/OU=/CN=UgraSage"

CMD ["gunicorn", "--certfile=/tmp/us.crt", "--keyfile=/tmp/us.key", "-b", "0.0.0.0:5000", "app:app"]
