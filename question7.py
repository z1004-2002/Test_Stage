import os
import os.path

import tarfile
import time
import json
import atexit
from utils_classes import OvfHandler
from pyVim.connect import SmartConnect, Disconnect

from pyVmomi import vim
import requests



#fonction de connection à l'ESXi
def connect_to_esxi(host, user, password):
    service_instance = SmartConnect(host=host, user=user, pwd=password, disableSslCertValidation=True)
    atexit.register(Disconnect, service_instance)
    return service_instance

# Fonction pour obtenir le ResourcePool
def get_resource_pool(datacenter):
    #Ici nous utilisont la première ressource pool
    return datacenter.hostFolder.childEntity[0].resourcePool

def handle_lease(lease, ova_file):
    with tarfile.open(ova_file, 'r:') as tar:
        for member in tar.getmembers():
            # Transférer uniquement les disques
            if member.name.endswith(".vmdk"):  
                disk_file = tar.extractfile(member)
                for device_url in lease.info.deviceUrl:
                    if device_url.importKey == member.name:
                        print(f"Transfert de {member.name} vers {device_url.url}...")
                        # Initialiser la progression
                        lease.HttpNfcLeaseProgress(0)  
                        
                        # Écrire le contenu du fichier sur l'URL HTTP NFS
                        with requests.put(device_url.url, data=disk_file, verify=False) as response:
                            if response.status_code == 200:
                                print(f"{member.name} transféré avec succès.")
                            else:
                                print(f"Erreur lors du transfert de {member.name}: {response.status_code}")
                                lease.HttpNfcLeaseAbort(Exception("Erreur de transfert"))
                                return

                        # Marquer la fin de la progression
                        lease.HttpNfcLeaseProgress(100)

    # Terminer le bail
    lease.HttpNfcLeaseComplete()
    print("Transfert terminé et bail libéré.")

def deploy(si,datastore_name,ova_file,datacenter_name,esxi_host):
    content = si.RetrieveContent()
    
    # Récupérer le datacenter
    datacenter = next(dc for dc in content.rootFolder.childEntity if dc.name == datacenter_name)
    # Utiliser le dossier de VM dans le datacenter
    datastore = next(ds for ds in datacenter.datastore if ds.name == datastore_name)
    
    # Récupération du pool de ressources
    resource_pool = get_resource_pool(datacenter)

    #! gestionnaire de l'OVF
    ovf_handle = OvfHandler(ova_file)

    ovf_manager = si.content.ovfManager
    
    cisp = vim.OvfManager.CreateImportSpecParams()
    cisr = ovf_manager.CreateImportSpec(
        ovf_handle.get_descriptor(), resource_pool, datastore, cisp)

    if cisr.error:
        print("Les erreurs suivantes empêcheront l'importation de cet OVA:")
        for error in cisr.error:
            print("%s" % error)
        return 1

    # cisr.importSpec.configSpec.name = vm_name
    ovf_handle.set_spec(cisr)

    lease = resource_pool.ImportVApp(cisr.importSpec, datacenter.vmFolder)
    
    while lease.state == vim.HttpNfcLease.State.initializing:
        print("En attente que le bail soit prêt...")
        time.sleep(1)

    if lease.state == vim.HttpNfcLease.State.error:
        print("Erreur de bail: %s" % lease.error)
        return 1
    if lease.state == vim.HttpNfcLease.State.done:
        return 0
    
    print("Démarrage du déploiement...")
    ovf_handle.upload_disks(lease, esxi_host)

def main():
    #! connection à l'ESXi
    # Configuration des paramètres de connexion à l'ESXi
    esxi_host = "10.144.208.248"
    esxi_user = "root"
    esxi_password = "toto32.." 
    
    si = connect_to_esxi(esxi_host, esxi_user, esxi_password)
    # Charger le fichier de configuration JSON
    with open('config_question7.json') as f:
        config = json.load(f)
        
    # Récupérer les paramètres de configuration
    number_of_instances = config["num_instances"]
    ova_file = config["ovf_path"]
    datacenter_name = config['datacenter']
    datastore_name = config['datastore']
    
    for i in range(number_of_instances):
        print(f"deploiement de la VM {i}")
        deploy(si,datastore_name,ova_file,datacenter_name,esxi_host)

    


if __name__ == "__main__":
    main()