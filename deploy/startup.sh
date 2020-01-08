#!/usr/bin/env bash
[[ -z $1 ]] && version=0.6
[[ -z $1 ]] || version=$1
docker run --rm --privileged=true -v `pwd`/config.yml:/etc/config.yml -v `pwd`/docker-compose:/data image.kaifa-empower.com/library/init:$version
while [ 0 -eq 0 ]
do
  {
    docker pull docker-compose/ami/docker-compose.yml && flag=1
  } || {
    flag=0
  }

  if [ $flag -eq 1 ];then
    break
  else
    echo pull fail
  fi
done

docker-compose -f docker-compose/ami/docker-compose.yml up -d