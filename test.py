import paramiko
from pyVmomi import vim
import json
from question7 import connect_to_esxi
import time

def connction_ssh(host, port, username, password):
    ssh = paramiko.SSHClient()
    # Charger les clés d'hôtes connus et définir la politique pour accepter les nouveaux hôtes
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # Connexion au serveur
    ssh.connect(host, port=port, username=username, password=password)
    
    return ssh
       

def create_directory_over_ssh(ssh, directory_path):
    try:
        # Commande pour créer le répertoire (mkdir -p crée tous les sous-répertoires nécessaires)
        command = f"mkdir -p {directory_path}"
        
        # Exécuter la commande sur le serveur
        stdin, stdout, stderr = ssh.exec_command(command)
        
        # Vérifier si des erreurs ont été renvoyées
        errors = stderr.read().decode()
        if errors:
            print(f"Erreur : {errors}")
        else:
            print(f"Dossier '{directory_path}' créé avec succès sur le serveur.")
        
    except Exception as e:
        print(f"Une erreur est survenue : {e}")
        
def get_vm_by_name(content, vm_name):
    for vm in content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True).view:
        if vm.name == vm_name:
            return vm
    return None

def copy_directory_with_ssh(ssh, source_directory, target_directory):
    try:
        # Commande pour créer le répertoire (mkdir -p crée tous les sous-répertoires nécessaires)
        command = f"cp -r {source_directory}/* {target_directory}"
        
        # Exécuter la commande sur le serveur
        stdin, stdout, stderr = ssh.exec_command(command)
        
        # Vérifier si des erreurs ont été renvoyées
        errors = stderr.read().decode()
        if errors:
            print(f"Erreur : {errors}")
        else:
            print(f"Dossier '{source_directory}' copié vers {target_directory}.")
        
    except Exception as e:
        print(f"Une erreur est survenue : {e}")
    
def rename_file(ssh, target_directory,lastname,newname):
    try:
        # Commande pour créer le répertoire (mkdir -p crée tous les sous-répertoires nécessaires)
        command = f"mv {target_directory}/{lastname}*** {target_directory}/{newname}***"
        
        # Exécuter la commande sur le serveur
        stdin, stdout, stderr = ssh.exec_command(command)
        
        # Vérifier si des erreurs ont été renvoyées
        errors = stderr.read().decode()
        if errors:
            print(f"Erreur : {errors}")
        else:
            print(f"Fichier modifié dans {target_directory}.")
        
    except Exception as e:
        print(f"Une erreur est survenue : {e}")    

def main():
    # Utilisation de la fonction
    host = "10.144.208.248"
    port = 22
    username = "root"
    password = "toto32.."
    source_vm = "tinyVM"
    target_vm = "tinyVM_Clone"
    # Charger le fichier de configuration JSON
    with open('config_question8.json') as f:
        config = json.load(f)
        
    # Récupérer les paramètres de configuration
    datastore = config['datastore']
    datacenter_name = config['datacenter']
    
    vm_name_prefix = config['vm_name_prefix']
    num_clones = config["num_clones"]
    
    #source_vmdk = f"{source_vm}.vmdk"
    #source_vmx = f"{target_vm}.vmx"
    
    #source_vmdk_path = f"[{datastore}] {source_vm}/{source_vm}.vmdk"
    #source_vmx_path = f"[{datastore}] {source_vm}/{source_vm}.vmx"
    clone_directory = f"[{datastore}] {target_vm}/"
    
    
    source_directory = f"/vmfs/volumes/{datastore}/{source_vm}"
    target_directory = f"/vmfs/volumes/{datastore}/{target_vm}"
    
    ssh = connction_ssh(host, port, username, password)
    create_directory_over_ssh(ssh, target_directory)
    copy_directory_with_ssh(ssh, source_directory, target_directory)
    
    # Chemins des fichiers VM
    clone_directory = f"[{datastore}] {target_vm}/"
 
    si = connect_to_esxi(host,username,password)
    content = si.RetrieveServiceContent()
    # Créer le dossier pour le clone si nécessaire
    
    # Enregistrer la VM clone
    datacenter = next(dc for dc in content.rootFolder.childEntity if dc.name == datacenter_name)
    #clone_spec = vim.VirtualMachineConfigSpec(name=target_vm, memoryMB=source_vm.config.hardware.memoryMB, numCPUs=source_vm.config.hardware.numCPU)
    
    original_vm = get_vm_by_name(content,source_vm)
    clone_spec = vim.VirtualMachineConfigSpec(
        name=source_vm,
        memoryMB=original_vm.config.hardware.memoryMB,
        numCPUs=original_vm.config.hardware.numCPU,
        files=vim.VirtualMachineFileInfo(vmPathName=f"{clone_directory}{source_vm}.vmx"),
        deviceChange=[
            vim.vm.device.VirtualDeviceConfigSpec(
                operation=vim.vm.device.VirtualDeviceConfigSpec.Operation.add,
                device=vim.vm.device.VirtualDisk(
                    capacityInKB=original_vm.config.hardware.device[0].capacityInKB,
                    backing=vim.vm.device.VirtualDiskFlatVer2BackingInfo(
                        fileName=f"{clone_directory}{source_vm}.vmdk",
                        diskMode='persistent'
                    )
                )
            )
        ]
    )
    
    
    resource_pool = content.rootFolder.childEntity[0].resourcePool  # Utiliser le resource pool par défaut
    task = datacenter.vmFolder.CreateVM(clone_spec, resource_pool)


    # Attendre la fin de la tâche
    while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
        time.sleep(1)

    if task.info.state == vim.TaskInfo.State.success:
        print(f"VM clone '{target_vm}' créé avec succès.")
    else:
        print(f"Erreur lors de la création de la VM clone: {task.info.error.msg}")

    ssh.close()
    
if __name__ == "__main__":
    main()