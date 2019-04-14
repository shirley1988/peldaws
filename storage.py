from azure.storage.blob import BlockBlobService
import utils
import os
import hashlib
import time
import json
import base64


def get_storage_service(config):
    if config.get('STORAGE_LOCATION') == 'azure':
        return AzureStorageService(config)
    else:
        return LocalStorageService()


# Base class for storage service
class StorageService(object):
    def __init__(self, config={}):
        self.__config = config

    # put a (new version of) file. If file with provided key already exists,
    # a new version will be created
    def put(self, key, data, attrs=None):
        raise 'Not implemented yet'

    # return a list of versions of file wity provided key
    # sorted by creation date from newest to oldest
    def show_versions(self, key):
        raise 'Not implemented yet'

    # get a file with key and specific version
    # if version is not specified, it is the latest version
    def get(self, key, version=None):
        raise 'Not implemented yet'

    # revert the content of a file so that its latest version is the same as
    # the last version prior to the provided version. File will not be
    # modified if the provided version does not exist.
    def revert(self, key, version):
        raise 'Not implemented yet'

    # delete the full history of file with the provided key, cannot be reverted
    def delete(self, key):
        raise 'Not implemented yet'

    def _serialize_attrs(self, attrs=None):
        if attrs is None:
            return ''
        if not isinstance(attrs, dict):
            raise ValueError("Obejct attributes must be a dictionary with string key and values")
        return base64.b64encode(json.dumps(attrs))


    def _deserialize_attrs(self, attrs_string):
        if not isinstance(attrs_string, basestring):
            raise ValueError("Not a string data to deserialize")
        if len(attrs_string) == 0:
            return None
        try:
            return json.loads(base64.b64decode(attrs_string))
        except:
            raise ValueError("Unable to deserialize data: " + attrs_string)


class LocalStorageService(StorageService):
    def __init__(self):
        self.__root = '/code/storage/'
        utils.mkdir_p(self.__root)

    def put(self, key, data, attrs=None):
        timestamp = "%.10f" % (time.time())
        subdir = os.path.join(self.__root, utils.generate_id(key))
        utils.mkdir_p(subdir)
        self._save(subdir + "/original_key", key)
        version = self._compute_version(timestamp, data)
        self._save(os.path.join(subdir, version), data)
        self._update_meta(subdir + "/meta", timestamp, version, self._serialize_attrs(attrs))

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
        return utils.generate_id(m.hexdigest())

    def _update_meta(self, meta_file, timestamp, version, attrs=''):
        with open(meta_file, 'a+') as fp:
            fp.write("%s --- %s --- %s\n" % (timestamp, version, attrs))

    def show_versions(self, key):
        meta = os.path.join(self.__root, utils.generate_id(key), 'meta')
        if not os.path.isfile(meta):
            return []
        versions = []
        for rec in self._read(meta).split("\n"):
            if not '---' in rec:
                continue
            parts = rec.split("---")
            ts = parts[0]
            ver = parts[1]
            if len(parts) > 2:
                attrs = parts[2]
            else:
                attrs = ''
            v_info = {
                'timestamp': ts.strip(),
                'timestamp_utc': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(float(ts))),
                'version': ver.strip(),
                'attributes': self._deserialize_attrs(attrs),
            }
            versions.append(v_info)
        return versions[::-1]

    def delete(self, key):
        subdir = os.path.join(self.__root, utils.generate_id(key))
        utils.rm_rf(subdir)


    def get(self, key, version=None):
        versions = self.show_versions(key)
        if version is None:
            if len(versions) == 0:
                return None
            version_info = versions[0]
            version = version_info['version']
        else:
            version_exists = False
            for v in versions:
                if v['version'] == version:
                    version_exists = True
                    version_info = v
                    break
            if not version_exists:
                return None
        full_path = os.path.join(self.__root, utils.generate_id(key), version)
        if os.path.isfile(full_path):
            return {'data': self._read(full_path), 'version': version_info}
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
        if find:
            # if provided version is the oldest
            if revert_to is None:
                data = ''
            else:
                data = self.get(key, revert_to)
            self.put(key, data)

        return find
