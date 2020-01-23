#!/usr/bin/python3

from typing import Any, Dict, List, Optional, Tuple, Union

from eth_abi.grammar import TupleType, parse

from .convert import to_bool, to_decimal, to_int, to_string, to_uint
from .datatypes import EthAddress, HexString, ReturnValue


def format_input(abi: Dict, inputs: Union[List, Tuple]) -> List:
    # Format contract inputs based on ABI types
    if len(inputs) and not len(abi["inputs"]):
        raise TypeError(f"{abi['name']} requires no arguments")
    abi_types = _get_abi_types(abi["inputs"])
    try:
        return _format_tuple(abi_types, inputs)
    except Exception as e:
        raise type(e)(f"{abi['name']} {e}")


def format_output(abi: Dict, outputs: Tuple) -> ReturnValue:
    # Format contract outputs based on ABI types
    abi_types = _get_abi_types(abi["outputs"])
    result = _format_tuple(abi_types, outputs)
    return ReturnValue(result, abi["outputs"])


def format_event(event: Dict) -> Any:
    # Format event data based on ABI types
    for e in [i for i in event["data"] if not i["decoded"]]:
        e["type"] = "bytes32"
        e["name"] += " (indexed)"
    abi_types = _get_abi_types(event["data"])
    values = ReturnValue(
        _format_tuple(abi_types, [i["value"] for i in event["data"]]), event["data"]
    )
    for i in range(len(event["data"])):
        event["data"][i]["value"] = values[i]
    return event


def _format_tuple(abi_types, values: Any) -> List:
    result = []
    values = list(values)
    if len(values) != len(abi_types):
        raise TypeError(f"Expected {len(abi_types)} arguments, got {len(values)}")
    for type_, value in zip(abi_types, values):
        try:
            if type_.is_array:
                result.append(_format_array(type_, value))
            elif isinstance(type_, TupleType):
                result.append(_format_tuple(type_.components, value))
            else:
                result.append(_format_single(type_.to_type_str(), value))
        except Exception as e:
            raise type(e)(f"'{value}' - {e}")
    return result


def _format_array(abi_type, values):
    if not isinstance(values, (list, tuple)):
        raise TypeError(f"Expected sequence, got {type(values).__name__}")
    if not abi_type.is_dynamic and len(values) != abi_type.arrlist[-1][0]:
        raise ValueError(
            f"Expected {abi_type.to_type_str()} but sequence has length of {len(values)}"
        )
    item_type = abi_type.item_type
    if item_type.is_array:
        return [_format_array(item_type, i) for i in values]
    elif isinstance(item_type, TupleType):
        return [_format_tuple(item_type.components, i) for i in values]
    return [_format_single(item_type.to_type_str(), i) for i in values]


def _format_single(type_str: str, value: Any) -> Any:
    # Apply standard formatting to a single value
    if "uint" in type_str:
        return to_uint(value, type_str)
    elif "int" in type_str:
        return to_int(value, type_str)
    elif type_str == "fixed168x10":
        return to_decimal(value)
    elif type_str == "bool":
        return to_bool(value)
    elif type_str == "address":
        return EthAddress(value)
    elif "byte" in type_str:
        return HexString(value, type_str)
    elif "string" in type_str:
        return to_string(value)
    raise TypeError(f"Unknown type: {type_str}")


def _params(abi_params: List, substitutions: Optional[Dict] = None) -> List:
    types = []
    if substitutions is None:
        substitutions = {}
    for i in abi_params:
        if i["type"] != "tuple":
            type_str = i["type"]
            for orig, sub in substitutions.items():
                if type_str.startswith(orig):
                    type_str = type_str.replace(orig, sub)
            types.append((i["name"], type_str))
            continue
        params = [i[1] for i in _params(i["components"], substitutions)]
        types.append((i["name"], f"({','.join(params)})"))
    return types


def _get_abi_types(abi_params: List) -> Tuple:
    type_str = f"({','.join(i[1] for i in _params(abi_params))})"
    tuple_type = parse(type_str)
    return tuple_type.components
