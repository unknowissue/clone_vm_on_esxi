# clone_vm_on_esxi
<br>
在esxi上直接克隆虚拟机，并修改新虚拟机IP地址
<br>
配置
<br>

```
1、用户能够用 证书 登陆esxi主机
2、修改clone_vm.py 文件
#模板名称 ，模板需要关机
template_name = "template2"
#esxi主机名
esxi_host = "esxi-host"
#模板的vmx和vmdk路径
template_vmx_path = "/vmfs/volumes/datastore2_sas1/template2/template2.vmx"
template_vmdk_path = "/vmfs/volumes/datastore2_sas1/template2/template2.vmdk"
#创建虚拟机的路径
base_destination_path = "/vmfs/volumes/datastore2_sas1"
#模板的IP地址
template_ip = "192.168.3.54"  # Template VM's IP address
#新虚拟机的IP和主机名
new_ips = ["192.168.3.101", "192.168.3.102", "192.168.3.103"]
new_hostnames = ["new-host-01", "new-host-02", "new-host-03"]
```
