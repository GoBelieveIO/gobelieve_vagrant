#!/bin/bash
apt-get -y update

#install mysql
apt-get install debconf-utils -y
debconf-set-selections <<< "mysql-server mysql-server/root_password password GoBelieve123456"
debconf-set-selections <<< "mysql-server mysql-server/root_password_again password GoBelieve123456"
apt-get install mysql-server -y




#install redis

if [ ! -f  "/usr/local/bin/redis-server" ]; then
    apt-get -y install make
    mkdir /opt/redis
    cd /opt/redis
    # Use latest stable
    wget -q http://download.redis.io/redis-stable.tar.gz
    # Only update newer files
    tar -xz --keep-newer-files -f redis-stable.tar.gz
     
    cd redis-stable
    make
    make install
    rm -f /etc/redis.conf
    cp -u /vagrant/redis.conf /etc/redis.conf
fi

#install python & python dep
apt-get install -y build-essential python2.7 python-dev

python /vagrant/get-pip.py
cd /vagrant/ && pip install -r requirements.txt


#create group database
mysql -u root -pGoBelieve123456 < /vagrant/db.sql


mkdir -p /data/redis
mkdir -p /data/im
mkdir -p /data/im_pending
mkdir -p /data/wwwroot
mkdir -p /data/logs/im
mkdir -p /data/logs/ims
mkdir -p /data/logs/imr

if [ ! -d "/data/wwwroot/im_bin" ]; then
    cp -r /vagrant/im_bin /data/wwwroot/im_bin
fi

if [ ! -d "/data/wwwroot/cli" ]; then
    cp -r /vagrant/cli /data/wwwroot/cli
fi
