#!/usr/bin/env bash
while_loop=0
while getopts "wv:" opt; do
  case $opt in
    w)
      while_loop=1
      ;;
    b)
    version=$OPTARG
    ;;
    \?)
      echo "Invalid option: -$OPTARG"
      ;;
  esac
done

[[ -z $version ]] && version=0.61

docker run --rm --privileged=true -v `pwd`/config.yml:/etc/config.yml -v `pwd`/docker-compose:/data 10.32.233.112/library/init:$version

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