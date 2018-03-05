from storage.kv_store_rocksdb import KeyValueStorageRocksdb

try:
    import rocksdb
except ImportError:
    print('Cannot import rocksdb, please install')


class KeyValueStorageRocksdbIntKeys(KeyValueStorageRocksdb):
    def __init__(self, db_dir, db_name, open=True):
        super().__init__(db_dir, db_name, open)

    @staticmethod
    def compare(a, b):
        a = int(a)
        b = int(b)
        if (a < b):
            return -1
        if (a > b):
            return 1
        return 0

    def open(self):
        opts = rocksdb.Options()
        opts.create_if_missing = True
        opts.comparator = self.compare
        self._db = rocksdb.DB(self._db_path, opts)
