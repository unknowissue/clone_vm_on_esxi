#!/bin/bash
vm_name=$1

vm_id=`vim-cmd vmsvc/getallvms | grep "$vm_name" | awk '{print $1}'`
echo $vm_id
nohup vim-cmd vmsvc/power.off  $vm_id > log_$vm_id_off.log 2>&1 & 
