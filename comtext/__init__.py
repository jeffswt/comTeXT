
from . import loader


def parse(path, target, preload_libs=[], include_path=None):
    return loader.parse_file(path, target, preload_libs=preload_libs,
                             include_path=include_path)
