"""Docs review agent — checks if PR code changes need doc updates.

Uses DeepSeek API when DEEPSEEK_API_KEY is set, otherwise falls back to a
rule-based heuristic comparing changed source files against doc files.
"""

import json
import os
import subprocess
import sys
from urllib.request import Request, urlopen


def get_pr_diff() -> str:
    """Get the diff for the current PR."""
    result = subprocess.run(
        ["git", "diff", "origin/main...HEAD", "--", "src/", "tests/"],
        capture_output=True,
        text=True,
    )
    return result.stdout


def get_changed_files() -> tuple[list[str], list[str], list[str]]:
    """Return (src_files, doc_files, other_files) changed in this PR."""
    result = subprocess.run(
        ["git", "diff", "--name-only", "origin/main...HEAD"],
        capture_output=True,
        text=True,
    )
    src_files = []
    doc_files = []
    other = []
    for line in result.stdout.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("src/model_eval_harness/") and line.endswith(".py"):
            src_files.append(line)
        elif line.startswith("docs/") or line == "mkdocs.yml":
            doc_files.append(line)
        else:
            other.append(line)
    return src_files, doc_files, other


def check_with_deepseek(diff: str, src_files: list[str], doc_files: list[str]) -> dict:
    """Ask DeepSeek to review doc coverage."""
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        return {"reviewed": False, "reason": "No DEEPSEEK_API_KEY set"}

    src_list = "\n".join(f"- {f}" for f in src_files) if src_files else "none"
    doc_list = "\n".join(f"- {f}" for f in doc_files) if doc_files else "none"

    prompt = (
        "You are a documentation review agent. A PR has been submitted with the following changes.\n\n"
        f"Changed source files:\n{src_list}\n\n"
        f"Changed documentation files:\n{doc_list}\n\n"
        "Code diff:\n```\n" + (diff[:6000] if len(diff) > 6000 else diff) + "\n```\n\n"
        "Does this PR include adequate documentation updates for the code changes?\n"
        "Consider:\n"
        "- New public APIs should have doc entries in docs/reference/\n"
        "- New features should have entries in docs/guides/\n"
        "- Bug fixes may not need doc changes\n"
        "- Internal refactors without API changes don't need docs\n\n"
        "Respond in JSON format:\n"
        "{\n"
        '  "needs_docs": true/false,\n'
        '  "severity": "none"|"low"|"medium"|"high",\n'
        '  "summary": "one sentence summary",\n'
        '  "suggestion": "specific suggestion for what docs to add (if needed)"\n'
        "}\n"
        "Only output valid JSON, no other text."
    )

    req = Request(
        "https://api.deepseek.com/v1/chat/completions",
        data=json.dumps(
            {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.0,
                "max_tokens": 500,
            }
        ).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )

    try:
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            content = data["choices"][0]["message"]["content"]
            # Strip markdown code fences if present
            content = content.strip().removeprefix("```json").removesuffix("```").strip()
            return json.loads(content) | {"reviewed": True}
    except Exception as e:
        return {"reviewed": False, "reason": str(e)}


def heuristic_check(src_files: list[str], doc_files: list[str]) -> dict:
    """Rule-based check for doc coverage."""
    needs_docs = bool(src_files) and not bool(doc_files)
    severity = "medium" if needs_docs else "none"

    return {
        "reviewed": False,
        "needs_docs": needs_docs,
        "severity": severity,
        "summary": f"{len(src_files)} source files changed, {len(doc_files)} doc files changed.",
        "suggestion": (
            "Consider adding documentation for the changed source files."
            if needs_docs
            else "Documentation appears up to date."
        ),
    }


def main() -> None:
    src_files, doc_files, _ = get_changed_files()

    if not src_files:
        print("No source files changed — skipping docs review.")
        return

    diff = get_pr_diff()

    result = check_with_deepseek(diff, src_files, doc_files)
    if not result.get("reviewed"):
        result = heuristic_check(src_files, doc_files)

    output = {
        "src_files": src_files,
        "doc_files": doc_files,
        "needs_docs": result.get("needs_docs", False),
        "severity": result.get("severity", "low"),
        "summary": result.get("summary", ""),
        "suggestion": result.get("suggestion", ""),
    }

    print(json.dumps(output, indent=2))

    # Write to file for the workflow to use as comment body
    with open("docs-review-result.json", "w") as f:
        json.dump(output, f, indent=2)

    with open("docs-review-comment.md", "w") as f:
        severity = output["severity"].upper()
        emoji = {"NONE": "✅", "LOW": "ℹ️", "MEDIUM": "⚠️", "HIGH": "🚨"}.get(severity, "ℹ️")
        f.write(f"## 📚 Docs Review {emoji}\n\n")
        f.write(f"**{output['summary']}**\n\n")
        if output.get("suggestion") and output["severity"] != "none":
            f.write(f"> {output['suggestion']}\n\n")
        f.write(f"Source files changed: {len(output['src_files'])}\n")
        f.write(f"Doc files changed: {len(output['doc_files'])}\n\n")
        f.write("<sub>🤖 model-eval-harness docs-review agent</sub>\n")


if __name__ == "__main__":
    main()
