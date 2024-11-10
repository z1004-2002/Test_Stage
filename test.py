import paramiko
from scp import SCPClient

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
    target_vm = "tinyVM_Copy"
    source_directory = f"/vmfs/volumes/datastore1/{source_vm}"
    target_directory = f"/vmfs/volumes/datastore1/{target_vm}"
    ssh = connction_ssh(host, port, username, password)
    #create_directory_over_ssh(ssh, target_directory)
    #copy_directory_with_ssh(ssh, source_directory, target_directory)
    rename_file(ssh, target_directory,source_vm,target_vm)
    ssh.close()
    
if __name__ == "__main__":
    main()