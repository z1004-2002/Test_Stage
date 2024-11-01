import json
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl


# Configuration de la connexion
host = "192.168.235.129"
username = "root"
password = "mr@bel2.0"

# Ignorer les erreurs SSL
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
context.verify_mode = ssl.CERT_NONE

# Connexion à l'ESXi
si = SmartConnect(host=host, user=username, pwd=password, disableSslCertValidation=True)

# Charger le fichier de configuration JSON
with open('config.json') as f:
    config = json.load(f)

number_of_instances = config["number_of_instances"]
ova_file = config["ova_file"]

# Fonction pour déployer l'OVA
def deploy_ova(ova_file, number_of_instances):
        # Récupérer le gestionnaire de contenu
    content = si.RetrieveContent()
    
    # Spécifier le chemin du datastore et le nom du dossier
    datastore_name = "datastore1"
    vm_folder = content.rootFolder.childEntity[0].vmFolder
    
    # Charger le fichier OVA
    with open(ova_file, 'rb') as ova:
        ova_data = ova.read()

    # Déployer les instances
    for i in range(number_of_instances):
        vm_name = f"tinyVM-{i+1}"
        print(f"Déploiement de {vm_name}...")

        # Créer une configuration pour la VM
        ovf_manager = content.ovfManager
        ovf_descriptor = ovf_manager.CreateDescriptor(ova_data)

        # Importer l'OVA
        task = ovf_manager.ImportVApp(ovf_descriptor, vm_folder)

        # Attendre la fin de la tâche
        while task.info.state == vim.TaskInfo.State.running:
            pass
        
        if task.info.state == vim.TaskInfo.State.success:
            print(f"{vm_name} déployé avec succès.")
        else:
            print(f"Échec du déploiement de {vm_name}: {task.info.error}")

# Appel de la fonction pour déployer les instances
deploy_ova(ova_file, number_of_instances)

# Déconnexion
Disconnect(si)