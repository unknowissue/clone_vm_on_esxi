import subprocess
import time
import os
import yaml
import json
import argparse
import logging
from jsonsearch import JsonSearch

def run_ansible_command(command):
    """Execute an Ansible command using subprocess and return the result."""
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result

def clone_vm_from_template(vm_name, template_name, esxi_host, template_vmx, template_vmdks, base_destination_path):
    """Clone a VM from a template using multiple VMDK paths."""
    vm_path = os.path.join(base_destination_path, vm_name )
    template_vmx_path = os.path.join(base_destination_path , template_name , template_vmx )
    for template_vmdk in template_vmdks:
	    
        template_vmdk_path = os.path.join(base_destination_path, template_name, template_vmdk)
        # Build the destination path including the VM name and VMDK file name
        vmdk_filename = str(template_vmdk).replace(template_name,vm_name)
        destination_path = os.path.join(base_destination_path, vm_name, vmdk_filename)
        print(destination_path)
        playbook_command = f"ansible-playbook clone_vm_disk.yml -e 'esxi_host={esxi_host}  template_vmdk_path={template_vmdk_path} destination_path={destination_path} vm_path={vm_path}' -vvvv"
        run_ansible_command(playbook_command)
    playbook_command = f"ansible-playbook update_vmx_register.yml -e 'vm_name={vm_name} template_name={template_name} esxi_host={esxi_host} template_vmx_path={template_vmx_path}  vm_path={vm_path}' -vvvv"
    run_ansible_command(playbook_command)    

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def wait_for_ssh_and_change_ip_hostname(vm_name, template_ip, vm_config, max_retries=10, sleep_interval=60):
    """Wait for SSH to be available on the cloned VM and change its IP and hostname."""
    
    modify_hostname_command = f"sshpass -p 'oracle' ssh -o StrictHostKeyChecking=no root@{template_ip} 'hostnamectl set-hostname {vm_name}'"
    check_hostname_command = f"sshpass -p 'oracle' ssh -o StrictHostKeyChecking=no root@{template_ip} 'hostname | grep {vm_name} | wc -l'"
    shutdown_command = f"sshpass -p 'oracle' ssh -o StrictHostKeyChecking=no root@{template_ip} 'nohup sh /root/scripts/shut.sh &'"
    
    for attempt in range(max_retries):
        try:
            logging.info(f"Attempt {attempt + 1}: Starting IP and hostname configuration for VM: {vm_name}")
            check_ip_value = 0  # 重置 IP 检查计数器

            for new_ip in vm_config['new_ips']:
                modify_ip_command = f"sshpass -p 'oracle' ssh -o StrictHostKeyChecking=no root@{template_ip} 'sh /root/scripts/set_net.sh {new_ip['network']} {new_ip['ip']}'"
                logging.info(f"Executing IP modification command: {modify_ip_command}")
                
                result = run_ansible_command(modify_ip_command)
                logging.info(f"IP modification command output: {result.stdout.decode().strip()}")
                
                check_ip_command = f"sshpass -p 'oracle' ssh -o StrictHostKeyChecking=no root@{template_ip} 'sh /root/scripts/get_net.sh {new_ip['network']} {new_ip['ip']}'"
                logging.info(f"Executing IP check command: {check_ip_command}")
                
                check_result = run_ansible_command(check_ip_command)
                check_ip_value += int(check_result.stdout.decode().strip())
                logging.info(f"IP check command output: {check_result.stdout.decode().strip()}")

            logging.info(f"Total IP checks passed: {check_ip_value}/{len(vm_config['new_ips'])}")

            # 修改主机名
            logging.info(f"Executing hostname modification command: {modify_hostname_command}")
            run_ansible_command(modify_hostname_command)
            check_hostname_result = run_ansible_command(check_hostname_command)
            check_hostname_value = int(check_hostname_result.stdout.decode().strip())
            logging.info(f"Hostname check result: {check_hostname_value}")

            if check_ip_value == len(vm_config['new_ips']) and check_hostname_value == 1:
                logging.info(f"IP and hostname for {vm_name} changed successfully.")
                
                # 执行关机命令
                logging.info(f"Executing shutdown command: {shutdown_command}")
                run_ansible_command(shutdown_command)
                break

        except subprocess.CalledProcessError as e:
            logging.error(f"Attempt {attempt + 1} failed with error: {e}. Output: {e.output.decode().strip()}, Stderr: {e.stderr.decode().strip() if e.stderr else 'None'}")
            if attempt + 1 < max_retries:
                logging.info(f"Retrying in {sleep_interval} seconds...")
                time.sleep(sleep_interval)
            else:
                logging.error(f"Max retries reached for VM: {vm_name}. Exiting with failure.")
        except Exception as e:
            logging.exception(f"An unexpected error occurred on attempt {attempt + 1}: {e}")
            if attempt + 1 < max_retries:
                logging.info(f"Retrying in {sleep_interval} seconds...")
                time.sleep(sleep_interval)
            else:
                logging.error(f"Max retries reached for VM: {vm_name}. Exiting with failure.")


def power_on_vm(vm_name, esxi_host):
    """Power on a specified VM on a given ESXi host."""
    playbook_command = f"ansible-playbook power_on_vm.yml -e 'vm_name={vm_name} esxi_host={esxi_host}'"
    run_ansible_command(playbook_command)

def power_off_vm(vm_name, esxi_host):
    """Power off a specified VM on a given ESXi host."""
    playbook_command = f"ansible-playbook power_off_vm.yml -e 'vm_name={vm_name} esxi_host={esxi_host}'"
    run_ansible_command(playbook_command)

def power_status_vm(vm_name, esxi_host):
    """Power off a specified VM on a given ESXi host."""
    playbook_command = f"export ANSIBLE_STDOUT_CALLBACK=json  &&  ansible-playbook power_status_vm.yml -e 'vm_name={vm_name} esxi_host={esxi_host}'"
    res=run_ansible_command(playbook_command)
    jsondata = JsonSearch(object=res.stdout.decode("utf-8"), mode='s')
    vm_status=jsondata.search_all_value(key='stdout_lines')
    return vm_status
    

def load_config(config_file):
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)

def main():
    parser = argparse.ArgumentParser(description="读取指定的文件")
    parser.add_argument("filename", help="要读取的文件的路径")
    args = parser.parse_args()
    config = load_config(args.filename)
    #config = load_config('cluster_config.yaml')
    
    for vm_config   in (config['vm_names']):
        vm_name = vm_config['vm_name']
        print(vm_config['vm_name'])
        clone_vm_from_template(vm_config['vm_name'], config['template_name'], config['esxi_host'], config['template_vmx'], config['template_vmdks'], config['base_destination_path'])
        power_on_vm(vm_config['vm_name'], config['esxi_host'])
        print(power_status_vm(vm_config['vm_name'], config['esxi_host']))
        time.sleep(120)  # Wait for VM to fully boot and SSH to be available
        wait_for_ssh_and_change_ip_hostname(vm_config['vm_name'], config['template_ip'], vm_config)
        # The call to power_off_vm is commented out, you can enable it if needed
        # power_off_vm(vm_config['vm_name'], config['esxi_host'])

if __name__ == "__main__":

    main()
