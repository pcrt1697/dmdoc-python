import inspect
import re
from importlib import import_module
from typing import Optional, Type


def import_object(cls_path: str):
    _cls_path = cls_path.split(":")
    if len(_cls_path) != 2:
        raise ValueError(
            f"Invalid class definition, expected format [<module_path>:<class_name>] found [{cls_path}]"
        )
    module_path, cls_name = _cls_path
    module = import_module(module_path)
    return getattr(module, cls_name)


def scan_modules(
    parent_class: str,
    modules: list[str],
    include: Optional[str] = None,
    exclude: Optional[str] = None
):
    _parent_class = import_object(parent_class)
    classes = set()
    for module in modules:
        for cls_name, cls in scan_module_subclasses(module, _parent_class):
            if ((include is None or re.match(include, cls_name)) and
                    (exclude is None or not re.match(exclude, cls_name))):
                classes.add(cls)
    return classes


def scan_module_subclasses(module: str, parent_class: Type):
    module = import_module(module)
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, parent_class) and obj != parent_class:
            yield name, obj
