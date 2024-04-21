import pkgutil

import field_game

for importer, modname, ispkg in pkgutil.walk_packages(
    path=field_game.__path__,prefix=field_game.__name__ + ".", onerror=lambda x: None
    ):
    __import__(modname)