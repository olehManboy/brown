#!/usr/bin/python3

import importlib
import json
import re
import time
from os import environ
from pathlib import Path
from typing import Dict

from pythx import Client, ValidationError
from pythx.middleware.toolname import ClientToolNameMiddleware
from mythx_models.request import AnalysisSubmissionRequest
from mythx_models.response import AnalysisSubmissionResponse, DetectedIssuesResponse
from brownie import project
from brownie._cli.__main__ import __version__
from brownie._config import ARGV, _update_argv_from_docopt
from brownie.exceptions import ProjectNotFound
from brownie.utils import color, notify
from brownie.utils.docopt import docopt

__doc__ = """Usage: brownie analyze [options] [--async | --interval=<sec>]

Options:
  --gui                     Launch the Brownie GUI after analysis
  --mode=<string>           The analysis mode (quick, standard, deep) [default: quick]
  --interval=<sec>          Result polling interval in seconds [default: 3]
  --async                   Do not poll for results, print job IDs and exit
  --api-key=<string>        The JWT access token from the MythX dashboard
  --help -h                 Display this message

Submits your project to the MythX API for smart contract security analysis.

In order to perform an analysis you must register for a MythX account and
generate a JWT access token. This access token may be passed through an
environment variable "MYTHX_API_KEY", or given via a command line option.

Visit https://mythx.io/ to learn more about MythX and sign up for an account.
"""


ANALYSIS_MODES = ("quick", "standard", "deep")
SEVERITY_COLOURS = {"LOW": "yellow", "MEDIUM": "orange", "HIGH": "red"}
DASHBOARD_BASE_URL = "https://dashboard.mythx.io/#/console/analyses/"


class SubmissionPipeline:
    BYTECODE_ADDRESS_PATCH = re.compile(r"__\w{38}")
    DEPLOYED_ADDRESS_PATCH = re.compile(r"__\$\w{34}\$__")

    def __init__(self, build, client: Client = None):
        self.requests: Dict[str, AnalysisSubmissionRequest] = {}
        self.responses: Dict[str, AnalysisSubmissionResponse] = {}
        self.reports: Dict[str, DetectedIssuesResponse] = {}
        self.build = build
        self.client = client or self.get_mythx_client()
        self.highlight_report = {"highlights": {"MythX": {}}}
        self.stdout_report = {}

    @staticmethod
    def get_mythx_client():
        """Generate a MythX client instance."""

        if ARGV["api-key"]:
            auth_args = {"api_key": ARGV["api-key"]}
        elif environ.get("MYTHX_API_KEY"):
            auth_args = {"api_key": environ.get("MYTHX_API_KEY")}
        else:
            raise ValidationError(
                "You must provide a MythX API key via environment variable or the command line"
            )

        return Client(
            **auth_args, middlewares=[ClientToolNameMiddleware(name=f"brownie-{__version__}")]
        )

    def prepare_requests(self):
        """Transform an artifact into a MythX payload."""

        contracts = {n: d for n, d in self.build.items() if d["type"] == "contract"}
        libraries = {n: d for n, d in self.build.items() if d["type"] == "library"}

        requests = {}
        for contract, artifact in contracts.items():
            requests[contract] = self.construct_request_from_artifact(artifact)

        # update requests with library dependencies
        for library, artifact in libraries.items():
            library_dependents = set(self.build.get_dependents(library))
            contract_dependencies = set(contracts.keys()).intersection(library_dependents)
            for contract in contract_dependencies:
                requests[contract].sources.update({
                    artifact.get("sourcePath"): {
                        "source": artifact.get("source"),
                        "ast": artifact.get("ast"),
                    }
                })

        self.requests = requests

    @classmethod
    def construct_request_from_artifact(cls, artifact) -> AnalysisSubmissionRequest:
        """Construct a raw submission request from an artifact JSON file."""

        bytecode = artifact.get("bytecode")
        deployed_bytecode = artifact.get("deployedBytecode")
        source_map = artifact.get("sourceMap")
        deployed_source_map = artifact.get("deployedSourceMap")

        bytecode = re.sub(cls.BYTECODE_ADDRESS_PATCH, "0" * 40, bytecode)
        deployed_bytecode = re.sub(cls.DEPLOYED_ADDRESS_PATCH, "0" * 40, deployed_bytecode)

        source_list = artifact.get("allSourcePaths")
        return AnalysisSubmissionRequest(
            contract_name=artifact.get("contractName"),
            bytecode=bytecode if bytecode else None,
            deployed_bytecode=deployed_bytecode if deployed_bytecode else None,
            source_map=source_map if source_map else None,
            deployed_source_map=deployed_source_map if deployed_source_map else None,
            sources={
                artifact.get("sourcePath"): {
                    "source": artifact.get("source"),
                    "ast": artifact.get("ast"),
                }
            },
            source_list=source_list if source_list else None,
            main_source=artifact.get("sourcePath"),
            solc_version=artifact["compiler"]["version"],
            analysis_mode=ARGV["mode"] or ANALYSIS_MODES[0],
        )

    def send_requests(self):
        """Send the prepared requests to MythX."""

        for contract_name, request in self.requests.items():
            response = self.client.analyze(payload=request)
            self.responses[contract_name] = response
            print(
                f"Submitted analysis {color('bright blue')}{response.uuid}{color} for "
                f"contract {color('bright magenta')}{request.contract_name}{color})"
            )
            print(f"You can also check the results at {DASHBOARD_BASE_URL}{response.uuid}\n")

    def wait_for_jobs(self):
        """Poll the MythX API and returns once all requests have been processed."""

        if not self.responses:
            raise ValidationError("No requests given")
        for contract_name, response in self.responses.items():
            while not self.client.analysis_ready(response.uuid):
                time.sleep(int(ARGV["interval"]))
            self.reports[contract_name] = self.client.report(response.uuid)
            # TODO: log message

    def generate_highlighting_report(self):
        """Generate a Brownie highlighting report from a MythX issue report."""

        source_to_name = {d["sourcePath"]: d["contractName"] for _, d in self.build.items()}
        for idx, (contract_name, issue_report) in enumerate(self.reports.items()):
            print(
                f"Generating report for {color('bright blue')}{contract_name}{color} ({idx}/{len(self.reports)})"
            )
            for report in issue_report.issue_reports:
                for issue in report:
                    # convert issue locations to report locations
                    # severities are highlighted according to SEVERITY_COLOURS
                    for loc in issue.locations:
                        comp = loc.source_map.components[0]
                        source_list = loc.source_list or report.source_list

                        if source_list and 0 <= comp.file_id < len(source_list):
                            filename = source_list[comp.file_id]
                            if filename not in source_to_name:
                                continue
                            contract_name = source_to_name[filename]
                            severity = issue.severity.name
                            self.highlight_report["highlights"]["MythX"].setdefault(
                                contract_name, {filename: []}
                            )
                            self.highlight_report["highlights"]["MythX"][contract_name][filename].append(
                                [
                                    comp.offset,
                                    comp.offset + comp.length,
                                    SEVERITY_COLOURS[severity],
                                    f"{issue.swc_id}: {issue.description_short}\n{issue.description_long}",
                                ]
                            )

    def generate_stdout_report(self):
        """Generated a stdout report overview from a MythX issue report."""

        for contract_name, issue_report in self.reports.items():
            for issue in issue_report:
                severity = issue.severity.name
                self.stdout_report.setdefault(contract_name, {}).setdefault(severity, 0)
                self.stdout_report[contract_name][severity] += 1


def print_console_report(stdout_report):
    """Highlight and print a given stdout report to the console."""

    total_issues = sum(x for i in stdout_report.values() for x in i.values())
    if not total_issues:
        notify("SUCCESS", "No issues found!")
        return

    # display console report
    total_high_severity = sum(i.get("HIGH", 0) for i in stdout_report.values())
    if total_high_severity:
        notify(
            "WARNING", f"Found {total_issues} issues including {total_high_severity} high severity!"
        )
    else:
        print(f"Found {total_issues} issues:")
    for name in sorted(stdout_report):
        print(f"\n  contract: {color('bright magenta')}{name}{color}")
        for key in [i for i in ("HIGH", "MEDIUM", "LOW") if i in stdout_report[name]]:
            c = color("bright red" if key == "HIGH" else "bright yellow")
            print(f"    {key.title()}: {c}{stdout_report[name][key]}{color}")


def main():
    args = docopt(__doc__)
    _update_argv_from_docopt(args)

    if ARGV["mode"] not in ANALYSIS_MODES:
        raise ValidationError(
            "Invalid analysis mode: Must be one of [{}]".format(
                ", ".join(ANALYSIS_MODES)
            )
        )

    project_path = project.check_for_project(".")
    if project_path is None:
        raise ProjectNotFound

    build = project.load()._build
    submission = SubmissionPipeline(build)

    print("Preparing project data for submission to MythX...")
    submission.prepare_requests()

    print("Sending analysis requests to MythX...")
    submission.send_requests()

    # exit if user wants an async analysis run
    if ARGV["async"]:
        print(
            "\nAll contracts were submitted successfully. Check the dashboard at "
            "https://dashboard.mythx.io/ for the progress and results of your analyses"
        )
        return

    print("\nWaiting for results...")

    submission.wait_for_jobs()
    submission.generate_stdout_report()
    submission.generate_highlighting_report()

    # erase previous report
    report_path = Path("reports/security.json")
    if report_path.exists():
        report_path.unlink()

    print_console_report(submission.stdout_report)

    # Write report to Brownie directory
    with report_path.open("w+") as fp:
        json.dump(submission.highlight_report, fp, indent=2, sort_keys=True)

    # Launch GUI if user requested it
    if ARGV["gui"]:
        print("Launching the Brownie GUI")
        gui = importlib.import_module("brownie._gui").Gui
        gui().mainloop()
