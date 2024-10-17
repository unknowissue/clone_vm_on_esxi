# clone_vm_on_esxi
<br>
在esxi上直接克隆虚拟机，并修改新虚拟机IP地址
<br>
配置
<br>


1、用户能够用 证书 登陆esxi主机
2、修改 clone.py 文件 为 自己的定义文件
```
    config = load_config('sig_config.yaml')
```

配置模板-单机 ( sig_config.yaml )
```
- vm_name: sig-test2
  new_ips:
      - network: ens34
        ip : 192.168.3.117
        
esxi_host: esxi-host
template_name: template2
template_vmx: template2.vmx
template_vmdks:
  - template2.vmdk
base_destination_path: /vmfs/volumes/datastore2_sas1
template_ip: 192.168.3.54
```

配置模板-集群 ( cluster_config.yaml )
```
vm_names:
- vm_name: cluster04-db01
  new_ips:
      - network: ens192
        ip : 192.168.3.115
      - network: ens224
        ip : 100.100.100.115
- vm_name: cluster04-db02
  new_ips:
      - network: ens192
        ip : 192.168.3.116
      - network: ens224
        ip : 100.100.100.116
        
esxi_host: esxi-host
template_name: rac_template1
template_vmx: rac_template1.vmx
template_vmdks:
  - rac_template1_1.vmdk
  - rac_template1_2.vmdk
base_destination_path: /vmfs/volumes/datastore2_sas1
template_ip: 192.168.3.52
```
解释
```
vm_name 主机名、虚拟机名称
new_ips 网卡名称和IP地址
esxi_host esxi主机
template_name 模板名称
template_vmx 模板vmx文件
template_vmdks 模板vmdk列表
base_destination_path 基础目录，模板和新虚拟机需要在这个目录下
```
3、开始克隆
```
python clone.py cluster_config_temp1.yaml
```
