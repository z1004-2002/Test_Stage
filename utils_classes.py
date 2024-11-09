import ssl
import sys
import os
import os.path

import tarfile
from threading import Timer
from six.moves.urllib.request import Request, urlopen

from pyVmomi import vim, vmodl

def get_tarfile_size(tarfile):
    """
    Déterminer la taille d'un fichier à l'intérieur de l'archive tar.
    """
    if hasattr(tarfile, 'size'):
        return tarfile.size
    size = tarfile.seek(0, 2)
    tarfile.seek(0, 0)
    return size

class OvfHandler(object):
    """
    OvfHandler gère la plupart des opérations OVA.
    """
    def __init__(self, ovafile):
        """
            Effectue l'initialisation nécessaire, ouvre le fichier OVA,
            traite les fichiers et lit le fichier ovf intégré.
        """
        self.handle = self._create_file_handle(ovafile)
        self.tarfile = tarfile.open(fileobj=self.handle)
        ovffilename = list(filter(lambda x: x.endswith(".ovf"),
                                  self.tarfile.getnames()))[0]
        ovffile = self.tarfile.extractfile(ovffilename)
        self.descriptor = ovffile.read().decode()

    def _create_file_handle(self, entry):
        """
            Un mécanisme simple pour déterminer si le fichier est local ou non.
            Ce n'est pas très robuste.
        """
        if os.path.exists(entry):
            return FileHandle(entry)
        return WebHandle(entry)

    def get_descriptor(self):
        return self.descriptor

    def set_spec(self, spec):
        """
        La spécification d'importation est nécessaire pour faire correspondre ultérieurement les clés de disque avec
            les noms de fichiers.
        """
        self.spec = spec

    def get_disk(self, file_item):
        """
        Effectue la traduction de la clé de disque en nom de fichier, renvoyant un handle de fichier.
        """
        ovffilename = list(filter(lambda x: x == file_item.path,
                                  self.tarfile.getnames()))[0]
        return self.tarfile.extractfile(ovffilename)

    def get_device_url(self, file_item, lease):
        for device_url in lease.info.deviceUrl:
            if device_url.importKey == file_item.deviceId:
                return device_url
        raise Exception("Impossible de trouver l'URL de l'appareil pour le fichier %s" % file_item.path)

    def upload_disks(self, lease, host):
        """
        Télécharge tous les disques, avec un suivi de la progression.
        """
        self.lease = lease
        try:
            self.start_timer()
            for fileItem in self.spec.fileItem:
                self.upload_disk(fileItem, lease, host)
            lease.Complete()
            print("Déploiement terminé avec succès.")
            return 0
        except vmodl.MethodFault as ex:
            print("Une erreur s'est produite lors du téléchargement : %s" % ex)
            lease.Abort(ex)
        except Exception as ex:
            print("Lease: %s" % lease.info)
            print("Une erreur s'est produite lors du téléchargement : %s" % ex)
            lease.Abort(vmodl.fault.SystemError(reason=str(ex)))
        return 1

    def upload_disk(self, file_item, lease, host):
        """
        Télécharger un disque individuel. Transmet le handle de fichier du
        disque directement à la requête urlopen.
        """
        ovffile = self.get_disk(file_item)
        if ovffile is None:
            return
        device_url = self.get_device_url(file_item, lease)
        url = device_url.url.replace('*', host)
        headers = {'Content-length': get_tarfile_size(ovffile)}
        if hasattr(ssl, '_create_unverified_context'):
            ssl_context = ssl._create_unverified_context()
        else:
            ssl_context = None
        req = Request(url, ovffile, headers)
        urlopen(req, context=ssl_context)

    def start_timer(self):
        """
        Un moyen simple de maintenir la mise à jour de la progression pendant que les disques sont transférés.
        """
        Timer(5, self.timer).start()

    def timer(self):
        """
        Mettez à jour la progression et reprogrammez le minuteur s'il n'est pas terminé.
        """
        try:
            prog = self.handle.progress()
            self.lease.Progress(prog)
            if self.lease.state not in [vim.HttpNfcLease.State.done,
                                        vim.HttpNfcLease.State.error]:
                self.start_timer()
            sys.stderr.write("Progression: %d%%\r" % prog)
        except Exception:  # Any exception means we should stop updating progress.
            pass

class FileHandle(object):
    def __init__(self, filename):
        self.filename = filename
        self.fh = open(filename, 'rb')

        self.st_size = os.stat(filename).st_size
        self.offset = 0

    def __del__(self):
        self.fh.close()

    def tell(self):
        return self.fh.tell()

    def seek(self, offset, whence=0):
        if whence == 0:
            self.offset = offset
        elif whence == 1:
            self.offset += offset
        elif whence == 2:
            self.offset = self.st_size - offset

        return self.fh.seek(offset, whence)

    def seekable(self):
        return True

    def read(self, amount):
        self.offset += amount
        result = self.fh.read(amount)
        return result

    # A slightly more accurate percentage
    def progress(self):
        return int(100.0 * self.offset / self.st_size)




class WebHandle(object):
    def __init__(self, url):
        self.url = url
        r = urlopen(url)
        if r.code != 200:
            raise FileNotFoundError(url)
        self.headers = self._headers_to_dict(r)
        if 'accept-ranges' not in self.headers:
            raise Exception("Le site n'accepte pas les plages")
        self.st_size = int(self.headers['content-length'])
        self.offset = 0

    def _headers_to_dict(self, r):
        result = {}
        if hasattr(r, 'getheaders'):
            for n, v in r.getheaders():
                result[n.lower()] = v.strip()
        else:
            for line in r.info().headers:
                if line.find(':') != -1:
                    n, v = line.split(': ', 1)
                    result[n.lower()] = v.strip()
        return result

    def tell(self):
        return self.offset

    def seek(self, offset, whence=0):
        if whence == 0:
            self.offset = offset
        elif whence == 1:
            self.offset += offset
        elif whence == 2:
            self.offset = self.st_size - offset
        return self.offset

    def seekable(self):
        return True

    def read(self, amount):
        start = self.offset
        end = self.offset + amount - 1
        req = Request(self.url,
                      headers={'Range': 'bytes=%d-%d' % (start, end)})
        r = urlopen(req)
        self.offset += amount
        result = r.read(amount)
        r.close()
        return result

    # A slightly more accurate percentage
    def progress(self):
        return int(100.0 * self.offset / self.st_size)

