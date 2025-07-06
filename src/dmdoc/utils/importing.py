import inspect
import re
from importlib import import_module
from importlib.metadata import EntryPoint, entry_points
from typing import Optional, Type, TypeVar, Any

_T = TypeVar("_T")


def import_object(obj_path: str):
    _obj_path = obj_path.split(":")
    if len(_obj_path) != 2:
        raise ValueError(
            f"Invalid object definition, expected format [<module_path>:<object_name>] found [{obj_path}]"
        )
    module_path, obj_name = _obj_path
    module = import_module(module_path)
    return getattr(module, obj_name)


def import_entrypoint_object(entrypoint: EntryPoint):
    try:
        return import_object(entrypoint.value)
    except ImportError as ie:
        raise ValueError(
            f"Failed to import entrypoint object with name `{entrypoint.name}`: "
            "maybe an optional dependency is not installed"
        ) from ie
    except Exception as e:
        raise ValueError(f"Failed to import entrypoint object with key `{entrypoint.name}`") from e


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


def resolve_entrypoint_class(name: str, group: str, parent_class: type[_T]) -> type[_T]:
    entrypoints = entry_points(name=name, group=group)
    try:
        entrypoint = entrypoints[name]
    except Exception as e:
        raise ValueError(f"Cannot find entrypoint named `{name}` belonging to group `{group}`") from e
    _class = import_entrypoint_object(entrypoint)
    if not issubclass(_class, parent_class):
        raise ValueError(f"Invalid entrypoint class for key `{name}` {_class}: it must inherit from {parent_class}")
    return _class


def import_entrypoint_items(group: str) -> dict[str, Any]:
    entrypoints = entry_points(group=group)
    return {
        entrypoint.name: import_entrypoint_object(entrypoint)
        for entrypoint in entrypoints
    }
