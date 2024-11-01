##Import des libraries
from pyVim.connect import SmartConnect
from pyVmomi import vim
from task import wait_for_tasks

#iNFORMATIONS DE CONNEXION
host_ip = '192.168.235.129'
username = 'root'
password = 'mr@bel2.0'

#FONCTION DE CONNECTION À L'ESXi
def connect():
    service_instance = SmartConnect(host=host_ip, user=username, pwd=password, disableSslCertValidation=True)
    return service_instance.RetrieveContent()

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

def create_dummy_vm(vm_name, si, vm_folder, resource_pool, datastore):
    config = create_config_spec(datastore.name, vm_name)
    vm_folder.CreateVM_Task(config=config, pool=resource_pool)
    

#définition de la fonction principale 
def main():
    si = connect()
    datacenter = si.rootFolder.childEntity[0]
    vm_folder = datacenter.vmFolder
    resource_pool = datacenter.resourcePool.resourcePool[0]
    datastore = datacenter.datastore[0]
    
    create_dummy_vm('abel', si, vm_folder, resource_pool, datastore)
    

if __name__ == "__main__":
    main()
