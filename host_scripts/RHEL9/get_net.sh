#!/bin/bash

netname=$1
ip=$2

cat  /etc/NetworkManager/system-connections/$netname.nmconnection  | grep $ip | wc -l
