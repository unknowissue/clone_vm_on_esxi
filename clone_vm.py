import subprocess
import time

def run_ansible_command(command):
    result=subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result


def clone_vm_from_template(vm_name, template_name, esxi_host, template_vmx_path, template_vmdk_path, base_destination_path):
    destination_path = f"{base_destination_path}/{vm_name}"
    playbook_command = f"ansible-playbook clone_vm.yml -e 'vm_name={vm_name} template_name={template_name} esxi_host={esxi_host} template_vmx_path={template_vmx_path} template_vmdk_path={template_vmdk_path} destination_path={destination_path}' --tags Clone_and_setup_VM"
    run_ansible_command(playbook_command)

def wait_for_ssh_and_change_ip_hostname(vm_name, template_ip, new_ip, new_hostname, max_retries=10, sleep_interval=60):
    print(new_hostname)
    ssh_command = f"sshpass -p 'oracle' ssh -o StrictHostKeyChecking=no root@{template_ip} 'hostnamectl set-hostname {new_hostname} && nmcli con mod ens34 ipv4.addresses {new_ip}/24 ipv4.method manual && systemctl restart NetworkManager'"
    check_ip_command = f"sshpass -p 'oracle' ssh -o StrictHostKeyChecking=no root@{template_ip} 'ip a | grep {new_ip} | wc -l'"
    check_hostname_command = f"sshpass -p 'oracle' ssh -o StrictHostKeyChecking=no root@{template_ip} 'hostname | grep {new_hostname}  | wc -l'"
    shutdown_command = f"sshpass -p 'oracle' ssh -o StrictHostKeyChecking=no root@{template_ip} 'shutdown -h +1 '"
    for attempt in range(max_retries):
        try:
            run_ansible_command(ssh_command)
            check_ip_value=run_ansible_command(check_ip_command).stdout.decode()
            check_ip_value=check_ip_value.join(check_ip_value.split())
            check_hostname_value=run_ansible_command(check_hostname_command).stdout.decode()
            check_hostname_value=check_hostname_value.join(check_hostname_value.split())
            if check_ip_value == "1" and check_hostname_value == "1" :
               print(f"IP and hostname for {vm_name} changed successfully.")
            break
        except subprocess.CalledProcessError:
            print(f"Attempt {attempt + 1} failed, retrying in {sleep_interval} seconds...")
            time.sleep(sleep_interval)
    run_ansible_command(shutdown_command)

def power_on_vm(vm_name, esxi_host):
    playbook_command = f"ansible-playbook power_on_vm.yml -e 'vm_name={vm_name} esxi_host={esxi_host}'"
    run_ansible_command(playbook_command)

def power_off_vm(vm_name, esxi_host):
    playbook_command = f"ansible-playbook power_off_vm.yml -e 'vm_name={vm_name} esxi_host={esxi_host}'"
    run_ansible_command(playbook_command)

vm_names = ["CloneVM-01", "CloneVM-02", "CloneVM-03"]
template_name = "template2"
esxi_host = "esxi-host"
template_vmx_path = "/vmfs/volumes/datastore2_sas1/template2/template2.vmx"
template_vmdk_path = "/vmfs/volumes/datastore2_sas1/template2/template2.vmdk"
base_destination_path = "/vmfs/volumes/datastore2_sas1"
template_ip = "192.168.3.54"  # Template VM's IP address
new_ips = ["192.168.3.101", "192.168.3.102", "192.168.3.103"]
new_hostnames = ["new-host-01", "new-host-02", "new-host-03"]

for vm_name, new_ip, new_hostname in zip(vm_names, new_ips, new_hostnames):
    clone_vm_from_template(vm_name, template_name, esxi_host, template_vmx_path, template_vmdk_path, base_destination_path)
    power_on_vm(vm_name, esxi_host)
    time.sleep(120)  # Wait for VM to fully boot and SSH to be available
    wait_for_ssh_and_change_ip_hostname(vm_name, template_ip, new_ip, new_hostname)
    #power_off_vm(vm_name, esxi_host)

