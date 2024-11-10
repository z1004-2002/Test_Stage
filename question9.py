import json
from pyVmomi import vim # type: ignore
from pyVim.task import WaitForTask # type: ignore
import time
from question7 import connect_to_esxi


def get_resource_pool(datacenter):
    #Ici nous utilisont la première ressource pool
    return datacenter.hostFolder.childEntity[0].resourcePool

def get_datastore(content, datastore_name):
    for ds in content.viewManager.CreateContainerView(content.rootFolder, [vim.Datastore], True).view:
        if ds.name == datastore_name:
            return ds
    return None

def get_vm_by_name(content, vm_name):
    for vm in content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True).view:
        if vm.name == vm_name:
            return vm
    return None


def create_dummy_vm(vm_name, si,datastore_name,datacenter_name):

    content = si.RetrieveServiceContent()
    #datastore = get_datastore(content, datastore_name)
    
    datastore_path = '[' + datastore_name + '] ' + vm_name
    datacenter = next(dc for dc in content.rootFolder.childEntity if dc.name == datacenter_name)
    vm_folder = datacenter.vmFolder
    resource_pool = get_resource_pool(datacenter)

    # bare minimum VM shell, no disks. Feel free to edit
    vmx_file = vim.vm.FileInfo(logDirectory=None,
                               snapshotDirectory=None,
                               suspendDirectory=None,
                               vmPathName=datastore_path)

    config = vim.vm.ConfigSpec(name=vm_name, memoryMB=128, numCPUs=1,
                               files=vmx_file, guestId='otherLinuxGuest',
                               version='vmx-07')

    print("Creating VM {}...".format(vm_name))
    task = vm_folder.CreateVM_Task(config=config, pool=resource_pool)
    
    while task.info.state == vim.TaskInfo.State.running:
        print("Creation in progress...")
    
    if task.info.state == vim.TaskInfo.State.success:
        print("Empty VM created successfully.")
    else:
        print(f"Failed to clone VM: {task.info.error}")

def find_free_ide_controller(vm):
    for dev in vm.config.hardware.device:
        if isinstance(dev, vim.vm.device.VirtualIDEController):
            # If there are less than 2 devices attached, we can use it.
            if len(dev.device) < 2:
                return dev
    return None

def get_physical_cdrom(host):
    for lun in host.configManager.storageSystem.storageDeviceInfo.scsiLun:
        if lun.lunType == 'cdrom':
            return lun
    return None

def new_cdrom_spec(controller_key, backing):
    connectable = vim.vm.device.VirtualDevice.ConnectInfo()
    connectable.allowGuestControl = True
    connectable.startConnected = True

    cdrom = vim.vm.device.VirtualCdrom()
    cdrom.controllerKey = controller_key
    cdrom.key = -1
    cdrom.connectable = connectable
    cdrom.backing = backing
    return cdrom

def find_device(vm, device_type):
    result = []
    for dev in vm.config.hardware.device:
        if isinstance(dev, device_type):
            result.append(dev)
    return result

def cdrom(si, vm_name, iso_path):
    content = si.RetrieveServiceContent()
    vm = get_vm_by_name(content, vm_name)
    
    controller = find_free_ide_controller(vm)
    
    if controller is None:
        raise Exception('Failed to find a free slot on the IDE controller')

    cdrom = None

    cdrom_lun = get_physical_cdrom(vm.runtime.host)
    
    if cdrom_lun is not None:
        backing = vim.vm.device.VirtualCdrom.AtapiBackingInfo()
        backing.deviceName = cdrom_lun.deviceName
        device_spec = vim.vm.device.VirtualDeviceSpec()
        device_spec.device = new_cdrom_spec(controller.key, backing)
        device_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
        config_spec = vim.vm.ConfigSpec(deviceChange=[device_spec])
        WaitForTask(vm.Reconfigure(config_spec))

        cdroms = find_device(vm, vim.vm.device.VirtualCdrom)
        # TODO isinstance(x.backing, type(backing))
        cdrom = next(filter(lambda x: type(x.backing) == type(backing) and
                     x.backing.deviceName == cdrom_lun.deviceName, cdroms))
    else:
        print('Skipping physical CD-Rom test as no device present.')

    cdrom_operation = vim.vm.device.VirtualDeviceSpec.Operation
    iso = iso_path
    if iso is not None:
        device_spec = vim.vm.device.VirtualDeviceSpec()
        if cdrom is None:  # add a cdrom
            backing = vim.vm.device.VirtualCdrom.IsoBackingInfo(fileName=iso)
            cdrom = new_cdrom_spec(controller.key, backing)
            device_spec.operation = cdrom_operation.add
        else:  # edit an existing cdrom
            backing = vim.vm.device.VirtualCdrom.IsoBackingInfo(fileName=iso)
            cdrom.backing = backing
            device_spec.operation = cdrom_operation.edit
        device_spec.device = cdrom
        config_spec = vim.vm.ConfigSpec(deviceChange=[device_spec])
        WaitForTask(vm.Reconfigure(config_spec))

        cdroms = find_device(vm, vim.vm.device.VirtualCdrom)
        
        cdrom = next(filter(lambda x: type(x.backing) == type(backing) and
                     x.backing.fileName == iso, cdroms))
    else:
        print('Skipping ISO test as no iso provided.')
     
def power_on_vm(si,vm_name):
    content = si.RetrieveServiceContent()
    virtual_machine = get_vm_by_name(content, vm_name)
    print(f"ma VM : {virtual_machine.name}, est {virtual_machine.runtime.powerState}")
    virtual_machine.PowerOnVM_Task()
    time.sleep(2)
    print(f"ma VM : {virtual_machine.name}, est {virtual_machine.runtime.powerState}")   
        
# Fonction principale
def main():
    # Lecture du fichier de configuration JSON
    with open('config_question9.json', 'r') as f:
        config = json.load(f)

    datacenter_name = config['datacenter']
    datastore_name = config['datastore']
    vm_name_prefix = config['vm_name_prefix']
    iso_path = config['iso_path']
    vm_name = f"{vm_name_prefix}1"
    
    esxi_host = "10.144.208.248"
    esxi_user = "root"
    esxi_password = "toto32.."
    
    # Connexion à l'hôte ESXi
    si = connect_to_esxi(esxi_host, esxi_user, esxi_password)
    # création d'une VM vide
    create_dummy_vm(vm_name, si,datastore_name,datacenter_name)
    #fonction pour attacher l'ISO
    cdrom(si, vm_name, iso_path)
    #mise en marche de notre nouvelle vm
    power_on_vm(si,vm_name)
    
    

if __name__ == "__main__":
    main()