from azure.storage.blob import BlockBlobService
import utils
import os
import hashlib
import time


def get_storage_service(app):
    if app.config['STORAGE_LOCATION'] == 'azure':
        return AzureStorageService(app.config)
    else:
        return LocalStorageService()


# Base class for storage service
class StorageService(object):
    def __init__(self, config={}):
        self.__config = config

    # put a (new version of) file. If file with provided key already exists,
    # a new version will be created
    def put(key, data):
        raise 'Not implemented yet'

    # return a list of versions of file wity provided key
    # sorted by creation date from newest to oldest
    def show_versions(key):
        raise 'Not implemented yet'

    # get a file with key and specific version
    # if version is not specified, it is the latest version
    def get(key, version=None):
        raise 'Not implemented yet'

    # revert the content of a file so that its latest version is the same as
    # the last version prior to the provided version. File will not be
    # modified if the provided version does not exist.
    def revert(key, version):
        raise 'Not implemented yet'

    # delete the full history of file with the provided key, cannot be reverted
    def delete(key):
        raise 'Not implemented yet'


class LocalStorageService(StorageService):
    def __init__(self):
        self.__root = '/code/storage/'
        utils.mkdir_p(self.__root)

    def put(self, key, data):
        timestamp = "%.10f" % (time.time())
        subdir = os.path.join(self.__root, utils.generate_id(key))
        utils.mkdir_p(subdir)
        self._save(subdir + "/original_key", key)
        version = self._compute_version(timestamp, data)
        self._save(os.path.join(subdir, version), data)
        self._update_meta(subdir + "/meta", timestamp, version)

    def _save(self, full_path, content):
        with open(full_path, 'w+') as fp:
            fp.write(content)

    def _read(self, full_path):
        with open(full_path, 'r') as fp:
            return fp.read()

    def _compute_version(self, timestamp, data):
        m = hashlib.md5()
        m.update(timestamp)
        m.update(data)
        return m.hexdigest()

    def _update_meta(self, meta_file, timestamp, version):
        with open(meta_file, 'a+') as fp:
            fp.write("%s --- %s\n" % (timestamp, version))

    def show_versions(self, key):
        meta = os.path.join(self.__root, utils.generate_id(key), 'meta')
        if not os.path.isfile(meta):
            return []
        versions = []
        for rec in self._read(meta).split("\n"):
            if not '---' in rec:
                continue
            ts, ver = rec.split("---")
            versions.append({
                'timestamp': float(ts.strip()),
                'version': ver.strip()
                })
        return versions[::-1]

    def delete(self, key):
        subdir = os.path.join(self.__root, utils.generate_id(key))
        utils.rm_rf(subdir)


    def get(self, key, version=None):
        if version is None:
            versions = self.show_versions(key)
            if len(versions) == 0:
                return None
            version = versions[0]['version']
        full_path = os.path.join(self.__root, utils.generate_id(key), version)
        if os.path.isfile(full_path):
            return self._read(full_path)
        return None

    def revert(self, key, version):
        versions = self.show_versions(key)
        find = False
        revert_to = None
        for ver in versions:
            # if previous version is the provided one, revert to this version
            if find == True:
                revert_to = ver['version']
                break
            if ver['version'] == version:
                find = True

        # if we find the provided version, do revert
        if find == True:
            # if provided version is the oldest
            if revert_to is None:
                data = ''
            else:
                data = self.get(key, revert_to)
            self.put(key, data)

        return find
