#!/usr/bin/python3

from pathlib import Path
import shutil
import sys

from brownie.network.contract import ContractContainer
from brownie.exceptions import ProjectAlreadyLoaded, ProjectNotFound
from .build import Build
from .sources import Sources
from . import compiler

from brownie._config import CONFIG, load_project_config

FOLDERS = ["contracts", "scripts", "reports", "tests"]


def check_for_project(path):
    '''Checks for a Brownie project.'''
    path = Path(path).resolve()
    for folder in [path]+list(path.parents):
        if folder.joinpath("brownie-config.json").exists():
            return folder
    return None


def new(path=".", ignore_subfolder=False):
    '''Initializes a new project.

    Args:
        path: Path to initialize the project at. If not exists, it will be created.
        ignore_subfolders: If True, will not raise if initializing in a project subfolder.

    Returns the path to the project as a string.
    '''
    if CONFIG['folders']['project']:
        raise ProjectAlreadyLoaded("Project has already been loaded")
    path = Path(path)
    path.mkdir(exist_ok=True)
    path = path.resolve()
    if not ignore_subfolder:
        check = check_for_project(path)
        if check and check != path:
            raise SystemError(
                "Cannot make a new project inside the subfolder of an existing project."
            )
    for folder in [i for i in FOLDERS]:
        path.joinpath(folder).mkdir(exist_ok=True)
    if not path.joinpath('brownie-config.json').exists():
        shutil.copy(
            str(Path(CONFIG['folders']['brownie']).joinpath("data/config.json")),
            str(path.joinpath('brownie-config.json'))
        )
    CONFIG['folders']['project'] = str(path)
    sys.path.insert(0, str(path))
    return str(path)


def load(path=None):
    '''Loads a project and instantiates various related objects.

    Args:
        path: Path of the project to load. If None, will attempt to locate
              a project using check_for_project()

    Returns a list of ContractContainer objects.
    '''
    if CONFIG['folders']['project']:
        raise ProjectAlreadyLoaded(
            "Project has already been loaded at {}".format(CONFIG['folders']['project'])
        )
    if path is None:
        path = check_for_project('.')
    if not path or not Path(path).joinpath("brownie-config.json").exists():
        raise ProjectNotFound("Could not find Brownie project")
    path = Path(path).resolve()
    CONFIG['folders']['project'] = str(path)
    for folder in [i for i in FOLDERS]:
        path.joinpath(folder).mkdir(exist_ok=True)
    sys.path.insert(0, str(path))
    load_project_config()
    compiler.set_solc_version()
    Sources()._load()
    Build()._load()  # compile happens here, updating tests / coverage happens here
    result = []
    for name, data in Build().items():
        if not data['bytecode']:
            continue
        container = ContractContainer(data)
        sys.modules['brownie.project'].__dict__[name] = container
        sys.modules['brownie.project'].__all__.append(name)
        result.append(container)
        # if running via interpreter, add to main namespace if package was imported via from
        if '__brownie_import_all__' in sys.modules['__main__'].__dict__:
            sys.modules['__main__'].__dict__[name] = container
    return result


def close(exc=True):
    if not CONFIG['folders']['project']:
        if not exc:
            return
        raise ProjectNotFound("No Brownie project currently open")
    Sources()._clear()
    Build()._clear()
    for name in sys.modules['brownie.project'].__all__.copy():
        if name == "__brownie_import_all__":
            continue
        del sys.modules['brownie.project'].__dict__[name]
        if '__brownie_import_all__' in sys.modules['__main__'].__dict__:
            del sys.modules['__main__'].__dict__[name]
    sys.path.remove(CONFIG['folders']['project'])
    sys.modules['brownie.project'].__all__ = ['__brownie_import_all__']
    CONFIG['folders']['project'] = None


def compile_source(source):
    '''Compiles the given source code string and returns a list of
    ContractContainer instances.'''
    result = []
    for name, build in compiler.compile_source(source).items():
        if build['type'] == "interface":
            continue
        result.append(ContractContainer(build))
    return result
