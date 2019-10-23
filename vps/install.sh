#! /bin/bash

pip3 install redis
pip3 install pytz

NAME=ugrasage
TAG=latest
SHNAME=ys

docker build -t ${NAME}:${TAG} -f ./Dockerfile ./

docker network create --subnet=172.19.0.0/16 ${SHNAME}net

docker create \
	--network ${SHNAME}net \
	--ip 172.19.0.2 \
	-p 443:5000 \
	--mount type=bind,source=../code,target=/app \
	--name ${NAME} \
	${NAME}:${TAG}

docker create \
	--network ${SHNAME}net \
	--ip 172.19.0.3 \
	--mount type=bind,source=redis/redis.conf,target=/usr/local/etc/redis/redis.conf \
	--mount type=bind,source=redis/data,target=/data \
	--name redis \
	redis:5.0.3-stretch redis-server /usr/local/etc/redis/redis.conf

sed "s,%p,$(pwd)/../code," ${SHNAME}cache_update.service > /etc/systemd/system/${SHNAME}cache_update.service
cp ${SHNAME}cache_update.timer /etc/systemd/system
systemctl daemon-reload
