#!/usr/bin/env bash
shell=$1
param=$2
result=$3
{
    bash "$shell" "$param" "$result"
    code=200
} || {
    code=500
}
data=`cat $result`

[[ "$data" == [* ]] || data='"'$data'"'

echo {'"code"':$code',''"data"':"$data"} > $result