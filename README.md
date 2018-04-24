# gobelieve vagrant
1. vagrant box add ubuntu/xenial64

2. cd $dir(Vagrantfile) && vagrant up

3. vagrant ssh

4. sudo redis-server /etc/redis.conf

5. cd /data/wwwroot/im_bin && sudo ./run.sh start

6. 获取token

   python /data/wwwroot/cli/gobelieve_auth.py $uid $name

7. 群组操作

   python /data/wwwroot/cli/gobelieve_group.py create $master $group_name $is_super $m1 $m2 $m3...

   python /data/wwwroot/cli/gobelieve_group.py add_member $gid $m1 $m2 $m3...

   python /data/wwwroot/cli/gobelieve_group.py remove_member $gid $m1 $m2 $m3...

   python /data/wwwroot/cli/gobelieve_group.py delete $gid

   python /data/wwwroot/cli/gobelieve_group.py upgrade $gid

8. 测试
   python /data/wwwroot/cli/gobelieve_client.py
