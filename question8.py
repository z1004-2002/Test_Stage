from pyVmomi import vim
import json
from question7 import connect_to_esxi


def get_vm_by_name(content, vm_name):
    for vm in content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True).view:
        if vm.name == vm_name:
            return vm
    return None

def clone_vm(service_instance, source_vm, clone_name, datastore_clone):
    # Get the content
    content = service_instance.RetrieveContent()
    
    # Create a clone spec
    clone_spec = vim.vm.CloneSpec()
    clone_spec.location = vim.vm.RelocateSpec()
    clone_spec.location.datastore = get_datastore(content, datastore_clone)
    clone_spec.powerOn = False
    clone_spec.template = False

    # Perform the clone operation
    task = source_vm.Clone(name=clone_name, folder=source_vm.parent, spec=clone_spec)

    return task

#datastore
def get_datastore(content, datastore_name):
    for ds in content.viewManager.CreateContainerView(content.rootFolder, [vim.Datastore], True).view:
        if ds.name == datastore_name:
            return ds
    return None

#transfrom de la vm en template
def vm_to_template(vm):
    vm.MarkAsTemplate()

def main():
    # Configuration
    esxi_host = "10.144.208.248"
    esxi_user = "root"
    esxi_password = "toto32.."
    
    # Charger le fichier de configuration JSON
    with open('config_question8.json') as f:
        config = json.load(f)
        
    # Récupérer les paramètres de configuration
    datastore_clone = config['datastore']
    vm_name_prefix = config['vm_name_prefix']
    num_clones = config["num_clones"]
    source_vm_name = f"{vm_name_prefix}"
    # Connect to ESXi
    si = connect_to_esxi(esxi_host, esxi_user, esxi_password)

    # Get content
    content = si.RetrieveServiceContent()

    # Find the source VM
    source_vm = get_vm_by_name(content, source_vm_name)
    if not source_vm:
        print(f"VM {source_vm_name} not found.")
        return
    
    #vm_to_template(source_vm)
    
    # Clone the VM
    print(f"Cloning VM {source_vm_name} to {clone_vm_name}...")
    for i in range(num_clones):
        clone_vm_name = f"{source_vm_name}_clone{i+1}"
        task = clone_vm(si, source_vm, clone_vm_name, datastore_clone)

        # Wait for the task to finish
        while task.info.state == vim.TaskInfo.State.running:
            print("Cloning in progress...")
        
        if task.info.state == vim.TaskInfo.State.success:
            print("VM cloned successfully.")
        else:
            print(f"Failed to clone VM: {task.info.error}")

if __name__ == "__main__":
    main()