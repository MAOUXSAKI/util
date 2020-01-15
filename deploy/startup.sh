#!/usr/bin/env bash
while_loop=0
local_ip=`ifconfig eth0|grep inet|grep -v 127.0.0.1|grep -v inet6|awk '{print $3}'|tr -d "addr:"`
if [[ $local_ip == netmsk ]];then
  local_ip=`ifconfig eth0|grep inet|grep -v 127.0.0.1|grep -v inet6|awk '{print $2}'|tr -d "addr:"`
fi
echo $local_ip
if [[ $local_ip == 10.32.*  ]];then
  repository=10.32.233.112
else
    repository=image.kaifa-empower.com
fi
while getopts "wv:" opt; do
  case $opt in
    w)
      while_loop=1
      ;;
    v)
    version=$OPTARG
    ;;
    \?)
      echo "Invalid option: -$OPTARG"
      ;;
  esac
done

[[ -z $version ]] && version=0.62

docker run --rm --privileged=true -v `pwd`/config.yml:/etc/config.yml -v `pwd`/docker-compose:/data $repository/library/init:$version

if [[ $while_loop -eq 1 ]];then
    while [ 0 -eq 0 ]
    do
       {
         docker-compose -f docker-compose/ami/docker-compose.yml pull && flag=1
       } || {
         flag=0
       }
       if [ $flag -eq 1 ];then
         break
       else
         echo pull fail
       fi
    done
fi
docker-compose -f docker-compose/ami/docker-compose.yml up -d
