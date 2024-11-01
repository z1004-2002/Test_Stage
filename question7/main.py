##Import des libraries
from pyVim.connect import SmartConnect
from pyVmomi import vim
from task import wait_for_tasks
import json

"""
Mon code n'a pas fonctionné
"""

#iNFORMATIONS DE CONNEXION
host_ip = '192.168.235.129'
username = 'root'
password = 'mr@bel2.0'

#FONCTION DE CONNECTION À L'ESXi
def connect():
    service_instance = SmartConnect(host=host_ip, user=username, pwd=password, disableSslCertValidation=True)
    return service_instance.RetrieveContent()


##fonction de définition des configuration
def create_config_spec(datastore_name, name, memory=1, guest="Guest",
                       annotation="Sample", cpus=1):
    config = vim.vm.ConfigSpec()
    config.annotation = annotation
    config.memoryMB = int(memory)
    config.guestId = guest
    config.name = name
    config.numCPUs = cpus
    files = vim.vm.FileInfo()
    files.vmPathName = "["+datastore_name+"]"
    config.files = files
    return config

##fonction de création de la VM
def create_dummy_vm(vm_name, si, vm_folder, resource_pool, datastore):
    config = vim.vm.ConfigSpec(name=vm_name, memoryMB=4096, numCPUs=2, guestId='otherGuest')
    datastore_path = f'[{datastore}] {vm_name}/{vm_name}.vmx'
    config.files = vim.vm.FileInfo(vmPathName=datastore_path)
    resource_pool.CreateVM_Task(config=config)
    #config = create_config_spec(datastore.name, vm_name)
    #vm_folder.CreateVM_Task(config=config, pool=resource_pool)
   
#fonction pour attacher l'ISO 
def attach_iso(si, vm_name, iso_path):
    vm = si.content.searchIndex.FindByDnsName(dnsName=vm_name, vmSearch=True)
    if vm:
        cdrom_spec = vim.vm.device.VirtualDeviceSpec()
        cdrom_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
        cdrom_spec.device = vim.vm.device.VirtualCdrom()
        cdrom_spec.device.backing = vim.vm.device.VirtualCdromIsoBackingInfo()
        cdrom_spec.device.backing.fileName = iso_path
        cdrom_spec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
        cdrom_spec.device.connectable.startConnected = True
        cdrom_spec.device.connectable.allowGuestControl = True
        vm.config.hardware.device.append(cdrom_spec.device)
        task = vm.ReconfigVM_Task(spec=vim.vm.ConfigSpec(deviceChange=[cdrom_spec]))
        

# Utilisation

#définition de la fonction principale 
def main():
    si = connect()
    datacenter = si.rootFolder.childEntity[0]
    vm_folder = datacenter.vmFolder
    resource_pool = datacenter.resourcePool.resourcePool[0]
    datastore = datacenter.datastore[0]
    
    create_dummy_vm('abel', si, vm_folder, resource_pool, datastore)
    attach_iso(si, 'abel', '[datastore1] test/Core-5.4.iso')

if __name__ == "__main__":
    main()
