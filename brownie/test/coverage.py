#!/usr/bin/python3

import json
from pathlib import Path
import re

from brownie.project import Build, Sources

build = Build()
sources = Sources()

def analyze_coverage(history):
    build_json = {}
    coverage_eval = {}
    coverage_map = {}
    pcMap = {}
    for tx in history:
        if not tx.receiver:
            continue
        tx_eval = {}
        for i in range(len(tx.trace)):
            t = tx.trace[i]
            pc = t['pc']
            name = t['contractName']
            path = t['source']['filename']
            if not name or not path:
                continue
            
            # prevent repeated requests to build object
            if name not in pcMap:
                pcMap[name] = build[name]['pcMap']
                coverage_map[name] = build[name]['coverageMap']
                coverage_eval[name] = dict((i, {}) for i in coverage_map[name])
            if name not in tx_eval:
                tx_eval[name] = dict((i, {}) for i in coverage_map[name])
            
            fn = pcMap[name][pc]['fn']
            if not fn:
                continue
            
            coverage_eval[name][path].setdefault(fn, {'tx': set(), 'true': set(), 'false': set()})
            tx_eval[name][path].setdefault(fn, set())
            if t['op'] != "JUMPI":
                if 'coverageIndex' not in pcMap[name][pc]:
                    continue
                # if not a JUMPI, record at the coverage map index
                idx = pcMap[name][pc]['coverageIndex']
                if coverage_map[name][path][fn][idx]['jump']:
                    tx_eval[name][path][fn].add(pcMap[name][pc]['coverageIndex'])
                else:
                    coverage_eval[name][path][fn]['tx'].add(pcMap[name][pc]['coverageIndex'])
                continue
            # if a JUMPI, check that we hit the jump AND the related coverage map
            idx = coverage_map[name][path][fn].index(next(i for i in coverage_map[name][path][fn] if i['jump']==pc))
            if idx not in tx_eval[name][path][fn] or idx in coverage_eval[name][path][fn]['tx']:
                continue
            key = ('false', 'true') if tx.trace[i+1]['pc'] == pc+1 else ('true', 'false')
            # if the conditional evaluated both ways, record on the main eval dict
            if idx not in coverage_eval[name][path][fn][key[1]]:
                coverage_eval[name][path][fn][key[0]].add(idx)
                continue
            coverage_eval[name][path][fn][key[1]].discard(idx)
            coverage_eval[name][path][fn]['tx'].add(idx)

    # evaluate coverage %'s
    for contract, source, fn_name, maps in [(k,w,y,z) for k,v in coverage_map.items() for w,x in v.items() for y,z in x.items()]:
        if fn_name not in coverage_eval[contract][source]:
            coverage_eval[contract][source][fn_name] = {'pct': 0}
            continue
        total = len([i for i in maps if i['jump']])*2 + len([i for i in maps if not i['jump']])

        result = coverage_eval[contract][source][fn_name]
        count = 0
        for idx, item in enumerate(maps):
            if idx in result['tx']:
                count += 2 if item['jump'] else 1
                continue
            if not item['jump']:
                continue
            if idx in result['true'] or idx in result['false']:
                count += 1
        result['pct'] = round(count / total, 4)
        if result['pct'] == 1:
            coverage_eval[contract][source][fn_name] = {'pct': 1}
    return coverage_eval


def merge_coverage(coverage_files):
    merged_eval = {}
    for filename in coverage_files:
        path = Path(filename)
        if not path.exists():
            continue
        coverage = json.load(path.open())['coverage']
        for contract_name in list(coverage):
            if contract_name not in merged_eval:
                merged_eval[contract_name] = coverage.pop(contract_name)
                continue
            for source, fn_name in [(k, x) for k, v in coverage[contract_name].items() for x in v]:
                f = merged_eval[contract_name][source][fn_name]
                c = coverage[contract_name][source][fn_name]
                if not c['pct'] or f == c:
                    continue
                if f['pct'] == 1 or c['pct'] == 1:
                    merged_eval[contract_name][source][fn_name] = {'pct': 1}
                    continue
                f['true'] += c['true']
                f['false'] += c['false']
                f['tx'] = list(set(f['tx']+c['tx']+[i for i in f['true'] if i in f['false']]))
                f['true'] = list(set([i for i in f['true'] if i not in f['tx']]))
                f['false'] = list(set([i for i in f['false'] if i not in f['tx']]))
    return merged_eval


def _list_to_set(obj, key):
    if key in obj:
        obj[key] = set(obj[key])
    else:
        obj[key] = set()
    return obj[key]


def generate_report(coverage_eval):
    report = {
        'highlights':{},
        'sha1':{}
    }
    for name, coverage in coverage_eval.items():
        report['highlights'][name] = {}
        for path in coverage:
            coverage_map = build[name]['coverageMap'][path]
            report['highlights'][name][path] = []
            for key, fn, lines in [(k,v['fn'],v['line']) for k,v in coverage_map.items()]:
                if coverage[path][key]['pct'] in (0, 1):
                    color = "green" if coverage[path][key]['pct'] else "red"
                    report['highlights'][name][path].append(
                        (fn['start'], fn['stop'], color, "")
                    )
                    continue
                for i, ln in enumerate(lines):
                    if i in coverage[path][key]['line']:
                        color = "green"
                    elif i in coverage[path][key]['true']:
                        color = "yellow" if _evaluate_branch(path, ln) else "orange"
                    elif i in coverage[path][key]['false']:
                        color = "orange" if _evaluate_branch(path, ln) else "yellow"
                    else:
                        color = "red"
                    report['highlights'][name][path].append(
                        (ln['start'], ln['stop'], color, "")
                    )
    return report


def _evaluate_branch(path, ln):
    source = sources[path]
    start, stop = ln['start'], ln['stop']
    try:
        idx = _maxindex(source[:start])
    except:
        return False

    # remove comments, strip whitespace
    before = source[idx:start]
    for pattern in ('\/\*[\s\S]*?\*\/', '\/\/[^\n]*'):
        for i in re.findall(pattern, before):
            before = before.replace(i, "")
    before = before.strip("\n\t (")

    idx = source[stop:].index(';')+len(source[:stop])
    if idx <= stop:
        return False
    after = source[stop:idx].split()
    after = next((i for i in after if i!=")"),after[0])[0]
    if (
        (before[-2:] == "if" and after=="|") or
        (before[:7] == "require" and after in (")","|"))
    ):
        return True
    return False


def _maxindex(source):
    comp = [i for i in [";", "}", "{"] if i in source]
    return max([source.rindex(i) for i in comp])+1