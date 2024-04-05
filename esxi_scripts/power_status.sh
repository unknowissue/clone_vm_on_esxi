#!/bin/bash
vm_name=$1

vm_id=`vim-cmd vmsvc/getallvms | grep "$vm_name" | awk '{print $1}'`
status=`vim-cmd vmsvc/power.getstate $vm_id | grep Powered | awk '{print $2}'`
echo $status
