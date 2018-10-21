import storage

def assertEqual(first, second):
    if first != second:
        raise AssertionError("%s is not equal to %s" % (str(first), str(second)))

def test_local_storage():
    lss = storage.LocalStorageService()
    # start with a clean state
    key = 'test'
    lss.delete(key)

    lss.put(key, 'test content version 1')
    lss.put(key, 'test content version 2')
    versions = lss.show_versions(key)
    assertEqual(len(versions), 2)
    print("It created 2 versions")
    assertEqual(versions[0]['timestamp'] > versions[1]['timestamp'], True)
    print("It return versions in order")
    assertEqual(lss.get(key), 'test content version 2')
    print("It gets latest version by default")

    lss.revert(key, 'nonexistsversion')
    assertEqual(len(lss.show_versions(key)), 2)
    assertEqual(lss.get(key), 'test content version 2')
    print("It does not do anything if revert a non-existent version")

    lss.revert(key, versions[0]['version'])
    versions = lss.show_versions(key)
    assertEqual(len(versions), 3)
    print("It creates a new version for revert")
    assertEqual(lss.get(key), 'test content version 1')
    print("The reverted content is as expected")

    lss.revert(key, versions[0]['version'])
    assertEqual(lss.get(key), 'test content version 2')
    assertEqual(lss.get(key, versions[1]['version']), 'test content version 2')
    print("It support revert revert")

    lss.revert(key, versions[-1]['version'])
    assertEqual(lss.get(key), '')
    print("Its content beomes empty if first version is reverted")

if __name__ == "__main__":
    test_local_storage()
