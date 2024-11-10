
Projet de déploiment des machines machines virtuelles de trois façons différentes sur un ESXi avec la bibliothèque pyVmomi de Python
=
notre projet est constitué de fichier  `question7.py`, `utils_classes.py`, et `config_question7.json` pour la question 7, `question8.py`, `test.py` et `config_question8.json` pour la question 8, `question9.py` et `config_question9.json` pour la question 9, `tinyVM.ova` qui est OVA des VM que nous déploiyons, un `README.md` et un `.gitignore`.

## Question 7: déploiement d'un image OVA (tinyVM)
> ### config_question7.json
Dans notre fichier `config_question7.json` nous mettons les configurations qui sont utilisées:
* **ovf_path**: qui est le chemin d'accès vers notre fichier OVA;
* **datacenter**: qui est le nom de notre datacenter;
* **datastore**: qui est le nom de notre datastore;
* **num_instances**: qui est le nombre d'instance des machine à déployer;
* **vm_name_prefix**: qui est le préfix des noms des machines à déployer;
* **host_name**: qui est le nom de l'hote sur lequel nous allons déployer nos machines virtuelles

> ### question7.py
Dans notre fichier `question7.py` implémentons notre code pour réponre à la question 7. Dans ce fichier, nous avons déclaré plusiers fonctions à savoir:
* **connect_to_esxi**: fonction permettant de ce connecter à l'ESXi;
* **get_resource_pool**: qui retourne la ressource_pool à partir du dataventer;
* **deploy_ova**: fonction de déploiement d'une machine virtuelle;
* **main**: fonction principale du fichier `question7.py`.

> ### utils_classes.py
Ce fichier `utils_classes.py` contient les classes utilitaires pour la question 7. ce fichier contient deux classes et une fonction
#### 1. la classe OvfHandler
OvfHandler gère la plupart des opérations OVA. Il traite le fichier tar, fait correspondre les clés de disque aux fichiers et télécharge les disques, tout en gardant à jour la progression du bail.

#### 2. la classe FileHandle
c'est la classe de gestion de fichier

#### 3. la fonction get_tarfile_size
Déterminez la taille d'un fichier à l'intérieur de l'archive tar. Si l'objet possède un attribut size, utilisez-le. Sinon, recherchez la fin et signalez-le.

## Question 8
> ### config_question8.json
Dans notre fichier `config_question7.json` nous mettons les configurations qui sont utilisées:
* **ovf_path**: qui est le chemin d'accès vers notre fichier OVA;
* **datacenter**: qui est le nom de notre datacenter;
* **datastore**: qui est le nom de notre datastore;
* **num_instances**: qui est le nombre d'instance des machine à déployer;
* **vm_name_prefix**: qui est le préfix des noms des machines à déployer;
* **num_clones**: qui est le nombre de fois que nous voulons cloner la notre VM déployé.

> ### question8.py
Dans notre fichier `question8.py` implémentons notre code pour réponre à la question 8. Dans ce fichier, nous avons déclaré plusiers fonctions à savoir:
* **connect_to_esxi**: fonction permettant de ce connecter à l'ESXi;
* **get_host_system**: fonction qui retourne l'hôte à partir de son nom;
* **get_ovf_descriptor**: cette fonction retourne le desscripteur de l'ova que nous voulons déployer;
* **get_resource_pool**: qui retourne la ressource_pool à partir du dataventer;
* **handle_lease**: fonction de gestion du retour de la fonction de création d'une machine virtuel;
* **deploy_ova**: fonction de déploiement d'une machine virtuelle;
* **main**: fonction principale du fichier `question8.py`.

> ### test.py
Dans ce fichier, j'ai essayé une autre approche en faisant un copié-collé en commande SSH. et créer une vm qui pointe sur les copies de l'original, mais en fait de compte, je n'ai pas pu finir d'exploiter cette voie. et l'erreur que j'ai eu est celle ci dessous
```
Traceback (most recent call last):
  File "/home/zogning-abel/Desktop/Test_Stage/test.py", line 159, in <module>
    main()
  File "/home/zogning-abel/Desktop/Test_Stage/test.py", line 129, in main
    vim.vm.device.VirtualDeviceConfigSpec(
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/zogning-abel/miniconda3/lib/python3.12/site-packages/pyVmomi/VmomiSupport.py", line 248, in __getattr__
    raise AttributeError(attr)
AttributeError: VirtualDeviceConfigSpec
```

### problèmes rencontrés
1. Les VM que nous avons déployé ne suportte pas la méthode `MarkAsTemplate` qui permet de transformer le la VM en template. et l'érreur de retour est que 
```
pyVmomi.VmomiSupport.vmodl.fault.NotSupported: (vmodl.fault.NotSupported) {
   dynamicType = <unset>,
   dynamicProperty = (vmodl.DynamicProperty) [],
   msg = 'The operation is not supported on the object.',
   faultCause = <unset>,
   faultMessage = (vmodl.LocalizableMessage) []
}
```
2. En ométant la fonction `MarkAsTemplate`, nous avons exécuté la méthosde `Clone` et cette méthode n'est pas aussi supporté par notre VM et nous avons l'erreur suivante :
```
pyVmomi.VmomiSupport.vmodl.fault.NotSupported: (vmodl.fault.NotSupported) {
   dynamicType = <unset>,
   dynamicProperty = (vmodl.DynamicProperty) [],
   msg = 'The operation is not supported on the object.',
   faultCause = <unset>,
   faultMessage = (vmodl.LocalizableMessage) []
}
```

## Question 9 

> ### config_question9.json
Dans notre fichier `config_question9.json` nous mettons les configurations qui sont utilisées:
* **datacenter**: qui est le nom de notre datacenter;
* **datastore**: qui est le nom de notre datastore;
* **vm_name_prefix**: qui est le préfix des noms des machines à déployer;
* **iso_path**: qui est le chemin vers le fichier `.iso` avec lequel nous allons créer notre machine virtuelle from scrach;

> ### question9.py
Dans notre fichier `question9.py` implémentons notre code pour réponre à la question 9. Dans ce fichier, nous avons déclaré plusiers fonctions à savoir:
* **get_resource_pool**: qui retourne la ressource_pool à partir du datacenter;
* **get_datastore**: qui retourne la ressource_pool à partir du datastore;
* **get_vm_by_name**: fonction qui retourne la vm à partir de son nom;
* **get_ovf_descriptor**: cette fonction retourne le desscripteur de l'ova que nous voulons déployer;
* **create_dummy_vm**: fonction qui crée une machine virtuelle vide
* **cdrom**: fonction pour créer le CDROM, attacher l’ISO et modifier la VM;
* **power_on_vm**: fonction qui allume une VM à partir de son nom;
* **main**: fonction principale du fichier `question9.py`;
* **get_physical_cdrom**: ;
* **find_free_ide_controller**: ;
* **get_physical_cdrom**: ;
* **new_cdrom_spec**: ;
* **find_device**: .