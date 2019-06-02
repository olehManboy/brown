#!/usr/bin/python3

import pytest
import solcx


from brownie.project import build, compiler, sources
from brownie.exceptions import CompilerError, ContractExists


@pytest.fixture(scope="function")
def version():
    yield
    compiler.set_solc_version("v0.5.7")


def _solc_5_source():
    source = sources.get('BrownieTester')
    source = source.replace('BrownieTester', 'TempTester')
    source = source.replace('UnlinkedLib', 'TestLib')
    return source


def _solc_4_source():
    source = _solc_5_source()
    source = source.replace('payable ', '')
    source = source.replace('^0.5.0', '^0.4.25')
    return source


def test_build_keys():
    build_json = sources.compile_paths(["contracts/BrownieTester.sol"])
    assert set(build.BUILD_KEYS) == set(build_json['BrownieTester'])


def test_contract_exists():
    with pytest.raises(ContractExists):
        sources.compile_source(sources.get('BrownieTester'))
    sources.compile_paths(["contracts/BrownieTester.sol"])


def test_set_solc_version(version):
    compiler.set_solc_version("v0.5.0")
    assert "0.5.0" in solcx.get_solc_version_string()


def test_unlinked_libraries(version):
    source = _solc_5_source()
    build_json = sources.compile_source(source)
    assert '__TestLib__' in build_json['TempTester']['bytecode']
    compiler.set_solc_version("v0.4.25")
    source = _solc_4_source()
    build_json = sources.compile_source(source)
    assert '__TestLib__' in build_json['TempTester']['bytecode']


def test_compiler_errors(version):
    with pytest.raises(CompilerError):
        sources.compile_paths(["contracts/Token.sol"])
    sources.compile_paths(["contracts/Token.sol", "contracts/SafeMath.sol"])
    source = _solc_4_source()
    with pytest.raises(CompilerError):
        sources.compile_source(source)
    compiler.set_solc_version("v0.4.25")
    sources.compile_source(source)
