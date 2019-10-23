docker stop redis ugrasage
docker rm redis ugrasage

docker rmi redis:5.0.3-stretch ugrasage:latest

docker network rm ysnet

systemctl stop yscache_update.timer
rm /etc/systemd/system/yscache_update.*
