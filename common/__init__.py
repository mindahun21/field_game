import pkgutil

import common

for importer, modname, ispkg in pkgutil.walk_packages(
    path=common.__path__,prefix=common.__name__ + ".", onerror=lambda x: None
    ):
    __import__(modname)