docker stop redis yuugubot
docker rm redis yuugubot

docker rmi redis:5.0.3-stretch yuugubot:latest

docker network rm ybnet

systemctl stop ybcache_updater.timer
rm /etc/systemd/system/ybcache_updater.*
