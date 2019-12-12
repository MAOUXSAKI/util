#!/usr/bin/env bash
[[ -z $1 ]] && version=0.5
[[ -z $1 ]] || version=$1
docker run --rm --privileged=true -v `pwd`/config.yml:/etc/config.yml -v `pwd`/docker-compose:/data image.kaifa-empower.com/library/init:$version
docker-compose -f docker-compose/ami/docker-compose.yml up -d