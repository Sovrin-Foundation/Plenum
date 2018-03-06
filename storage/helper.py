from ledger.hash_stores.file_hash_store import FileHashStore
from ledger.hash_stores.hash_store import HashStore
from ledger.hash_stores.memory_hash_store import MemoryHashStore

from plenum.common.config_util import getConfig
from plenum.common.constants import KeyValueStorageType, HS_FILE, HS_LEVELDB, HS_ROCKSDB
from plenum.common.exceptions import KeyValueStorageConfigNotFound

from plenum.persistence.leveldb_hash_store import LevelDbHashStore
from plenum.persistence.rocksdb_hash_store import RocksDbHashStore

from storage.kv_in_memory import KeyValueStorageInMemory
from storage.kv_store import KeyValueStorage
from storage.kv_store_leveldb import KeyValueStorageLeveldb
from storage.kv_store_rocksdb import KeyValueStorageRocksdb


def initKeyValueStorage(keyValueType, dataLocation,
                        keyValueStorageName) -> KeyValueStorage:
    if keyValueType == KeyValueStorageType.Leveldb:
        return KeyValueStorageLeveldb(dataLocation, keyValueStorageName)
    if keyValueType == KeyValueStorageType.Rocksdb:
        return KeyValueStorageRocksdb(dataLocation, keyValueStorageName)
    elif keyValueType == KeyValueStorageType.Memory:
        return KeyValueStorageInMemory()
    else:
        raise KeyValueStorageConfigNotFound


def initHashStore(data_dir, name, config=None) -> HashStore:
    """
    Create and return a hashStore implementation based on configuration
    """
    config = config or getConfig()
    hsConfig = config.hashStore['type'].lower()
    if hsConfig == HS_FILE:
        return FileHashStore(dataDir=data_dir,
                             fileNamePrefix=name)
    elif hsConfig == HS_LEVELDB:
        return LevelDbHashStore(dataDir=data_dir,
                                fileNamePrefix=name)
    elif hsConfig == HS_ROCKSDB:
        return RocksDbHashStore(dataDir=data_dir,
                                fileNamePrefix=name)
    else:
        return MemoryHashStore()
