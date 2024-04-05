#!/bin/bash

netname=$1
ip=$2

cat  /etc/sysconfig/network-scripts/ifcfg-$netname  | grep $ip | wc -l
[root@cluster04-db01 ~]# cat scripts/set_net.sh 
#!/bin/bash

netname=$1
ip=$2

sed  "s/^.*IPADDR=.*$/IPADDR=$ip/" -i /etc/sysconfig/network-scripts/ifcfg-$netname
