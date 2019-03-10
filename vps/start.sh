docker start redis
docker start yuugubot
python3 ../code/ybcache.py
systemctl start ybcache_updater.timer
#docker logs redis
