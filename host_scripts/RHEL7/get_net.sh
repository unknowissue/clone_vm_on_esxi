#!/bin/bash

netname=$1
ip=$2

cat  /etc/sysconfig/network-scripts/ifcfg-$netname  | grep $ip | wc -l
