docker start redis
docker start ugrasage
python3 ../code/yscache.py
systemctl start yscache_update.timer
