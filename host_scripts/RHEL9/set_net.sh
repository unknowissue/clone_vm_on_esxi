#!/bin/bash

netname=$1
ip=$2

nmcli con mod $netname  ipv4.addresses $ip/24 ipv4.method manual
