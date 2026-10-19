"""Export selected fields from existing local execution records; do not rerun n8n."""
import json
import re
from pathlib import Path

from run_validation import CASES, ROOT, SOURCE_ROOT, native_result


def main():
    observed = json.loads((ROOT / "observed-results.json").read_text(encoding="utf-8"))
    results = observed["results"]
    assert len(results) == len(CASES) and {r["scenario"] for r in results} == set(CASES)
    assert all(r["passed"] and all(r["checks"].values()) for r in results)
    public_results = []
    traces = []
    for result in results:
        path = (ROOT / result["stdout_file"]).resolve()
        assert path.parent == ROOT
        actual = native_result(path.read_text(encoding="utf-8"))
        nodes = {}
        for name, entries in actual["runData"].items():
            nodes[name] = [{"executionStatus": e.get("executionStatus"), "executionTime": e.get("executionTime"),
                            "data": e.get("data"), "errorMessage": (e.get("error") or {}).get("message")} for e in entries]
        traces.append({"scenario": result["scenario"], "errorMessage": (actual.get("error") or {}).get("message"), "runData": nodes})
        public_results.append({key: value for key, value in result.items() if key not in {"stdout_file", "stderr_file"}})
    payload = {"scope": "Selected native n8n CLI execution fields from our synthetic fixture. Stacks, local paths and instance metadata excluded.", "traces": traces}
    encoded = json.dumps(payload, indent=2)
    assert not re.search(r"[A-Za-z]:[\\/]|/Users/|/home/|BEGIN PRIVATE KEY|bb_ag_", encoded)
    (SOURCE_ROOT / "native-execution-summary.json").write_text(encoded + "\n", encoding="utf-8")
    (SOURCE_ROOT / "observed-results.json").write_text(json.dumps({"n8n_version": observed["n8n_version"], "scope": observed["scope"], "results": public_results}, indent=2) + "\n", encoding="utf-8")
    print("Exported seven actual scenarios and selected native trace fields. No test was rerun.")


if __name__ == "__main__":
    main()
