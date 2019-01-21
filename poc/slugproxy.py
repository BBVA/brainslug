from tinydb.middlewares import Middleware
from tinydb.storages import MemoryStorage
from tinydb import TinyDB

import weakref


class WeakRefMiddleware(Middleware):
    def __init__(self, storage_cls=TinyDB.DEFAULT_STORAGE):
        # Any middleware *has* to call the super constructor
        # with storage_cls
        super(WeakRefMiddleware, self).__init__(storage_cls)

    def _filter_data_by_lost_weakref(self, data):
        to_remove = list()
        for table_name in data:
            table = data[table_name]

            for doc_id in table:
                item = table[doc_id]

                if item.get('__session__', lambda: None)() is None:
                    to_remove.append(doc_id)
        for doc_id in to_remove:
            del table[doc_id]

    def read(self):
        data = self.storage.read()
        if data:
            self._filter_data_by_lost_weakref(data)
        return data

    def write(self, data):
        if data:
            self._filter_data_by_lost_weakref(data)
        self.storage.write(data)

    def close(self):
        self.storage.close()

class Niano:
    pass

namedobj = Niano()

db = TinyDB(storage=WeakRefMiddleware(MemoryStorage))
db.insert({'ojete': 'moreno1', '__session__': weakref.ref(namedobj)})
db.insert({'ojete': 'moreno2', '__session__': weakref.ref(Niano())})

del namedobj
