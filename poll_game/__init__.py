import pkgutil

import poll_game

for importer, modname, ispkg in pkgutil.walk_packages(
    path=poll_game.__path__,prefix=poll_game.__name__ + ".", onerror=lambda x: None
    ):
    __import__(modname)