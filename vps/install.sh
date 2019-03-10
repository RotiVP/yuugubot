#! /bin/bash

pip3 install --user redis
pip3 install --user pytz

NAME=yuugubot
TAG=latest
SHNAME=yb

#if [[ -z "$(docker images -q ${NAME}:${TAG})" ]]; then
	docker build -t ${NAME}:${TAG} -f ./Dockerfile ./
#fi

docker network create --subnet=172.19.0.0/16 ${SHNAME}net 2> /dev/null

#run -d --rm
docker create \
	--network ${SHNAME}net \
	--ip 172.19.0.2 \
	-p 443:5000 \
	--mount type=bind,source="$(pwd)"/../code,target=/app \
	--name ${NAME} \
	${NAME}:${TAG}
#docker rmi ${NAME}:${TAG}

#	--publish 6379:6379 \
# /data is working directory in the container
docker create \
	--network ${SHNAME}net \
	--ip 172.19.0.3 \
	--mount type=bind,source="$(pwd)"/redis/redis.conf,target=/usr/local/etc/redis/redis.conf \
	--mount type=bind,source="$(pwd)"/redis/data,target=/data \
	--name redis \
	redis:5.0.3-stretch redis-server /usr/local/etc/redis/redis.conf

#docker start -i <name>

cp ybcache_updater.* /etc/systemd/system
systemctl daemon-reload
