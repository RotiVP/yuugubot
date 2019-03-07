#! /bin/bash

NAME=yuugubot
TAG=latest
SHNAME=yb

#if [[ -z "$(docker images -q ${NAME}:${TAG})" ]]; then
	docker build -t ${NAME}:${TAG} docker
#fi

docker network create --subnet=172.19.0.0/16 ${SHNAME}net 2> /dev/null

#run -d --rm
docker create \
	--network ${SHNAME}net \
	--ip 172.19.0.2 \
	-p 443:5000 \
	--mount type=bind,source="$(pwd)"/docker,target=/app \
	--name ${NAME} \
	${NAME}:${TAG}
#docker rmi ${NAME}:${TAG}

#publish лучше закомментить потом. Доступ по внутренней сети
docker create \
	--network ${SHNAME}net \
	--ip 172.19.0.3 \
	--publish 6379:6379 \
	--mount type=bind,source="$(pwd)"/redis/redis.conf,target=/usr/local/etc/redis/redis.conf \
	--mount type=bind,source="$(pwd)"/redis/data,target=/data \
	--name redis \
	redis:5.0.3-stretch redis-server /usr/local/etc/redis/redis.conf

#docker start -i <name>
