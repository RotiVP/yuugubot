# нет компилятора и других инструментов для установки модулей
# use musl libc instead of glibc and friends
#FROM python:3-alpine3.9

FROM python:3-slim

VOLUME /app
WORKDIR /app
COPY . /app
#COPY app.py requirements.txt ybapi.py /app/
#ADD database /app

EXPOSE 5000

RUN \
pip install --no-cache-dir -r requirements.txt

#CMD FLASK_APP=index.py flask run --host="0.0.0.0" --port="5000"
CMD ["python", "app.py"]
