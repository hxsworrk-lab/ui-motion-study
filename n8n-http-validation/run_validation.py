"""Bounded native-n8n check against our own loopback fixture, not Google Sheets."""
import argparse
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import threading
from uuid import uuid4

import fixture_server as fixture

SOURCE_ROOT = Path(__file__).resolve().parent
ROOT = Path(os.environ.get("HX_N8N_CHECK_ROOT", str(SOURCE_ROOT / ".local"))).resolve()
ROOT.mkdir(parents=True, exist_ok=True)
(ROOT / "tmp").mkdir(exist_ok=True)
NODE = os.environ.get("HX_NODE_EXECUTABLE", "node")
CLI = Path(os.environ.get("HX_N8N_CLI", str(SOURCE_ROOT / "node_modules/n8n/bin/n8n")))
CASES = ["normal", "rate-limit-once", "unavailable-once", "permanent400", "always503", "duplicate", "missing-id"]


def condition(expression):
    return {"conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
                           "conditions": [{"id": str(uuid4()), "leftValue": "={{ " + expression + " }}", "rightValue": True,
                                           "operator": {"type": "boolean", "operation": "true", "singleValue": True}}],
                           "combinator": "and"}, "options": {}}


def make_workflow(scenario, port):
    nodes = []

    def node(name, kind, parameters, version=1):
        nodes.append({"id": str(uuid4()), "name": name, "type": "n8n-nodes-base." + kind,
                      "typeVersion": version, "parameters": parameters, "position": [len(nodes) * 200, 0]})

    node("Start", "manualTrigger", {})
    node("Read synthetic API", "httpRequest", {"method": "GET", "url": f"http://127.0.0.1:{port}/source?scenario={scenario}",
          "options": {"timeout": 5000, "response": {"response": {"fullResponse": True, "neverError": True, "responseFormat": "json"}}}}, 4.2)
    node("Retry transient status", "if", condition("[429,500,502,503,504].includes($json.statusCode) && $runIndex < 2"), 2.2)
    node("Wait one second", "wait", {"resume": "timeInterval", "amount": 1, "unit": "seconds"}, 1.1)
    node("Require success", "if", condition("$json.statusCode === 200"), 2.2)
    node("Require valid batch", "if", condition("Array.isArray($json.body.records) && $json.body.records.every(r => typeof r.id === 'string' && r.id.length > 0 && Number.isInteger(r.quantity) && r.quantity >= 0)"), 2.2)
    node("Split records", "splitOut", {"fieldToSplitOut": "body.records", "include": "noOtherFields", "options": {}}, 1)
    node("First record per ID", "removeDuplicates", {"operation": "removeDuplicateInputItems", "compare": "selectedFields", "fieldsToCompare": "id", "options": {}}, 2)
    node("Write synthetic row", "httpRequest", {"method": "POST", "url": f"http://127.0.0.1:{port}/row", "sendBody": True,
          "contentType": "json", "specifyBody": "json", "jsonBody": "={{ $json }}", "options": {"timeout": 5000}}, 4.2)
    node("Stop HTTP failure", "stopAndError", {"errorType": "errorMessage", "errorMessage": "={{ 'Synthetic source HTTP ' + $json.statusCode }}"})
    node("Stop invalid batch", "stopAndError", {"errorType": "errorMessage", "errorMessage": "Synthetic source contains invalid records"})
    edges = {"Start": [["Read synthetic API"]], "Read synthetic API": [["Retry transient status"]],
             "Retry transient status": [["Wait one second"], ["Require success"]], "Wait one second": [["Read synthetic API"]],
             "Require success": [["Require valid batch"], ["Stop HTTP failure"]],
             "Require valid batch": [["Split records"], ["Stop invalid batch"]], "Split records": [["First record per ID"]],
             "First record per ID": [["Write synthetic row"]]}
    connections = {name: {"main": [[{"node": target, "type": "main", "index": 0} for target in output] for output in outputs]}
                   for name, outputs in edges.items()}
    return {"id": "HxHttpCheck" + str(CASES.index(scenario) + 1).zfill(5), "name": "Hx self-study " + scenario,
            "nodes": nodes, "connections": connections, "settings": {"executionOrder": "v1"}, "active": False}


def environment():
    allowed = {"SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT", "PATH", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "LANG", "LC_ALL"}
    env = {key: value for key, value in os.environ.items() if key.upper() in allowed}
    for key in ("N8N_LICENSE_ACTIVATION_KEY", "N8N_ENCRYPTION_KEY", "N8N_LICENSE_CERT", "N8N_CONFIG_FILES"):
        env.pop(key, None)
    env.update(N8N_USER_FOLDER=str(ROOT / "state"), DB_TYPE="sqlite", DB_SQLITE_DATABASE=str(ROOT / "state/.n8n/database.sqlite"),
               N8N_DIAGNOSTICS_ENABLED="false", N8N_VERSION_NOTIFICATIONS_ENABLED="false",
               N8N_TEMPLATES_ENABLED="false", N8N_LICENSE_AUTO_RENEW_ENABLED="false", N8N_LISTEN_ADDRESS="127.0.0.1",
               N8N_RUNNERS_BROKER_LISTEN_ADDRESS="127.0.0.1", TEMP=str(ROOT / "tmp"), TMP=str(ROOT / "tmp"))
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        env["N8N_RUNNERS_BROKER_PORT"] = str(sock.getsockname()[1])
    return env


def invoke(args, name):
    original_name = name
    attempt = 1
    while (ROOT / (name + ".stdout.txt")).exists():
        attempt += 1
        name = original_name + "-attempt" + str(attempt)
    stdout_file = ROOT / (name + ".stdout.txt")
    stderr_file = ROOT / (name + ".stderr.txt")
    with stdout_file.open("w", encoding="utf-8") as out, stderr_file.open("w", encoding="utf-8") as err:
        process = subprocess.run([NODE, "--use-system-ca", str(CLI), *args], cwd=ROOT, env=environment(),
                                 stdout=out, stderr=err, timeout=150)
    result = subprocess.CompletedProcess(process.args, process.returncode, stdout_file.read_text(encoding="utf-8", errors="replace"),
                                         stderr_file.read_text(encoding="utf-8", errors="replace"))
    result.stdout_path = stdout_file.name
    result.stderr_path = stderr_file.name
    return result


def native_result(stdout):
    decoder = json.JSONDecoder()
    for match in re.finditer(r"(?m)^\{", stdout):
        try:
            data, _ = decoder.raw_decode(stdout[match.start():])
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and isinstance(data.get("data", {}).get("resultData"), dict):
            return data["data"]["resultData"]
    raise AssertionError("No native n8n execution result JSON; inspect saved CLI logs")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=CASES + ["all", "remaining"], default="normal")
    args = parser.parse_args()
    cases = CASES if args.scenario == "all" else CASES[1:] if args.scenario == "remaining" else [args.scenario]
    version = invoke(["--version"], "runtime-version")
    if version.returncode or version.stdout.strip() != "2.43.7":
        raise AssertionError("This recorded study requires n8n 2.43.7; do not label another runtime as that version")
    server = fixture.ThreadingHTTPServer(("127.0.0.1", 0), fixture.Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    previous_results = ROOT / "observed-results.json"
    results = json.loads(previous_results.read_text(encoding="utf-8"))["results"] if previous_results.exists() else []
    try:
        workflows = [make_workflow(case, server.server_port) for case in cases]
        file = ROOT / "synthetic-workflows.json"
        normal_original = ROOT / "normal-workflow-original.json"
        if file.exists() and not normal_original.exists():
            normal_original.write_bytes(file.read_bytes())
        file.write_text(json.dumps(workflows, indent=2), encoding="utf-8")
        imported = invoke(["import:workflow", "--input=" + str(file)], "import")
        if imported.returncode or "successfully imported" not in imported.stdout.lower():
            raise AssertionError("Native workflow import not proved; inspect import logs")
        for workflow, case in zip(workflows, cases):
            fixture.calls.clear()
            fixture.rows.clear()
            fixture.events.clear()
            executed = invoke(["execute", "--id=" + workflow["id"], "--rawOutput"], "execute-" + case)
            result = native_result(executed.stdout)
            has_error = bool(result.get("error"))
            expected_error = case in {"permanent400", "always503", "missing-id"}
            expected_calls = 3 if case == "always503" else 2 if case in {"rate-limit-once", "unavailable-once"} else 1
            expected_rows = {} if expected_error else {"item-a": {"id": "item-a", "quantity": 10}, "item-b": {"id": "item-b", "quantity": 5}}
            checks = {"native_run_data": "Read synthetic API" in result.get("runData", {}), "error_matches": has_error == expected_error,
                      "source_calls_match": fixture.calls[case] == expected_calls, "rows_match": fixture.rows == expected_rows,
                      "row_write_count_matches": len(fixture.events) == len(expected_rows)}
            observed = {"scenario": case, "checks": checks, "passed": all(checks.values()), "cli_returncode": executed.returncode,
                        "source_calls": fixture.calls[case], "rows": dict(fixture.rows), "write_events": list(fixture.events),
                        "native_error": result.get("error", {}).get("message"), "executed_nodes": list(result.get("runData", {})),
                        "stdout_file": executed.stdout_path, "stderr_file": executed.stderr_path}
            results.append(observed)
            (ROOT / "observed-results.json").write_text(json.dumps({"n8n_version": "2.43.7", "scope": "own-loopback-fixture-not-google-sheets", "results": results}, indent=2), encoding="utf-8")
            print(json.dumps(observed), flush=True)
            if not observed["passed"]:
                raise AssertionError("Actual native result differs from expected checks")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        print(json.dumps({"fixture_closed": not thread.is_alive(), "port": server.server_port}), flush=True)


if __name__ == "__main__":
    main()
