#!/bin/bash
vm_name=$1

vm_id=`vim-cmd vmsvc/getallvms | grep "$vm_name" | awk '{print $1}'`
echo $vm_id
nohup vim-cmd vmsvc/power.on  $vm_id & 
sleep 30
message_id=`vim-cmd vmsvc/message $vm_id |  grep "Virtual machine message" | awk '{print $1}'` | sed 's/://'
echo $message_id
nohup vim-cmd vmsvc/message $vm_id $message_id 2 &
