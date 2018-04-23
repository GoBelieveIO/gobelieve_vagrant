#gobelieve vagrant

1. vagrant box add ubuntu/xenial64
2. cd $dir(Vagrantfile) && vagrant up
3. vagrant ssh, sudo redis-server /etc/redis.conf, cd /data/wwwroot/im_bin && sudo ./run.sh start
4. 获取token
   python /data/wwwroot/cli/gobelieve_auth.py $uid $name

5. 群组操作
   python /data/wwwroot/cli/gobelieve_group.py create $master $group_name $is_super $m1 $m2 $m3...
   python /data/wwwroot/cli/gobelieve_group.py add_member $gid $m1 $m2 $m3...
   python /data/wwwroot/cli/gobelieve_group.py remove_member $gid $m1 $m2 $m3...
   python /data/wwwroot/cli/gobelieve_group.py delete $gid


