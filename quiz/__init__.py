import pkgutil

import quiz

for importer, modname, ispkg in pkgutil.walk_packages(
    path=quiz.__path__,prefix=quiz.__name__ + ".", onerror=lambda x: None
    ):
    __import__(modname)