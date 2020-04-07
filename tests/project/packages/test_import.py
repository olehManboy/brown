import shutil

import pytest
import yaml

import brownie
from brownie.exceptions import CompilerError
from brownie.project import compile_source
from brownie.project.main import install_package


@pytest.fixture(autouse=True)
def setup():
    yield
    path = brownie._config._get_data_folder().joinpath("packages")
    shutil.rmtree(path)
    path.mkdir()


code = """
pragma solidity ^0.5.0;

import "brownie-mix/token-mix@1.0.0/contracts/Token.sol";

contract Foo is Token {}
    """


def test_import_from_package():
    install_package("brownie-mix/token-mix@1.0.0")
    compile_source(code)


def test_import_fails_without_package_installed():
    with pytest.raises(CompilerError):
        compile_source(code)


def test_dependency_with_remapping(newproject):
    with newproject._path.joinpath("brownie-config.yaml").open() as fp:
        config = yaml.safe_load(fp)
    config["dependencies"] = ["brownie-mix/token-mix@1.0.0"]
    config["compiler"]["solc"]["remappings"] = ["token=brownie-mix/token-mix@1.0.0/contracts"]
    with newproject._path.joinpath("brownie-config.yaml").open("w") as fp:
        yaml.dump(config, fp)

    remapped_code = """
pragma solidity ^0.5.0;

import "token/Token.sol";

contract Foo is Token {}
    """

    with newproject._path.joinpath("contracts/Test.sol").open("w") as fp:
        fp.write(remapped_code)

    newproject.load()
