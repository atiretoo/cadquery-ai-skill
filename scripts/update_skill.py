#!/usr/bin/env python3
"""
Autonomous CadQuery SKILL.md updater.
Compares upstream CadQuery documentation changes and uses Google Gemini API
to synthesize changes into SKILL.md while strictly preserving coordinate system rules.
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request


def run_git(cmd: list[str], cwd: str) -> str:
    res = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    return res.stdout.strip()


def call_gemini(api_key: str, prompt: str, model: str = "gemini-2.5-flash") -> str:
    models_to_try = [model, "gemini-2.0-flash", "gemini-1.5-flash"]
    last_err = None

    for m in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 8192
            }
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                return text
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            print(f"Warning: Gemini model {m} failed with HTTP {e.code}: {err_body}", file=sys.stderr)
            last_err = e
            continue
        except Exception as e:
            print(f"Warning: Gemini model {m} failed with error: {e}", file=sys.stderr)
            last_err = e
            continue

    raise RuntimeError(f"All Gemini models failed. Last error: {last_err}")


def set_github_output(name: str, value: str):
    output_file = os.environ.get("GITHUB_OUTPUT")
    if output_file:
        with open(output_file, "a", encoding="utf-8") as f:
            if "\n" in value:
                delimiter = "EOF"
                f.write(f"{name}<<{delimiter}\n{value}\n{delimiter}\n")
            else:
                f.write(f"{name}={value}\n")


def main():
    parser = argparse.ArgumentParser(description="Update SKILL.md based on upstream CadQuery documentation changes.")
    parser.add_argument("--cadquery-dir", required=True, help="Path to upstream CadQuery repository")
    parser.add_argument("--skill-file", default="SKILL.md", help="Path to SKILL.md")
    parser.add_argument("--commit-file", default=".upstream_commit", help="Path to tracked upstream commit file")
    args = parser.parse_args()

    cadquery_dir = os.path.abspath(args.cadquery_dir)
    skill_file = os.path.abspath(args.skill_file)
    commit_file = os.path.abspath(args.commit_file)

    if not os.path.exists(commit_file):
        print(f"ERROR: Commit file {commit_file} not found.", file=sys.stderr)
        sys.exit(1)

    with open(commit_file, "r", encoding="utf-8") as f:
        old_commit = f.read().strip()

    new_commit = run_git(["git", "rev-parse", "HEAD"], cwd=cadquery_dir)
    print(f"Tracking CadQuery commits: {old_commit} -> {new_commit}")

    if old_commit == new_commit:
        print("Upstream commit has not changed. Everything is up to date.")
        set_github_output("docs_changed", "false")
        return

    # Check if doc/ files changed
    diff_stat = run_git(["git", "diff", "--stat", old_commit, new_commit, "--", "doc/"], cwd=cadquery_dir)
    if not diff_stat:
        print("Upstream updated, but NO files under doc/ were modified.")
        # Advance the commit file
        with open(commit_file, "w", encoding="utf-8") as f:
            f.write(new_commit + "\n")
        set_github_output("docs_changed", "false")
        set_github_output("commit_advanced", "true")
        set_github_output("new_commit", new_commit)
        return

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable is missing but doc changes were detected.", file=sys.stderr)
        sys.exit(1)

    print("Documentation changes detected in upstream CadQuery:")
    print(diff_stat)

    commit_log = run_git(["git", "log", "--oneline", f"{old_commit}..{new_commit}", "--", "doc/"], cwd=cadquery_dir)
    diff_content = run_git(["git", "diff", old_commit, new_commit, "--", "doc/"], cwd=cadquery_dir)

    # Truncate diff if extremely large to prevent context overflow
    if len(diff_content) > 50000:
        diff_content = diff_content[:50000] + "\n\n... [diff truncated due to size] ...\n"

    with open(skill_file, "r", encoding="utf-8") as f:
        current_skill = f.read()

    prompt = f"""You are an autonomous maintainer of the CadQuery AI Skill repository.
The official CadQuery documentation (under `doc/`) has been updated in upstream commits:
{commit_log}

Here is the git diff of the documentation changes:
```diff
{diff_content}
```

Here is the current `SKILL.md` file:
```markdown
{current_skill}
```

TASK:
Update `SKILL.md` to reflect any new methods, API changes, syntax updates, or features introduced in the upstream documentation.

CRITICAL INSTRUCTIONS & CONSTRAINTS:
1. STRICT PRESERVATION: You MUST preserve Section 2 ("Coordinate Spaces & Orientation (CRITICAL)") and all its subsection rules verbatim. Do NOT modify or remove:
   - The CAD standard: +X = right, +Y = rear, +Z = up in all three spaces (Build, User, Print).
   - Build Space and User Space are identical.
   - The rotation to Print Space is always the LAST operation in a script.
   - The workplane orientation rules: always use cyclic "XY", "YZ", "ZX" (NEVER "XZ").
   - The specific note on "ZX" swapping local sketch axes to local x = +Z, local y = +X, with coordinates written (z, x).
   - The print orientation table and rules.
2. DENSE AND OPTIMIZED: Maintain dense, concise, and accurate documentation structured specifically for LLMs.
3. OUTPUT FORMAT:
   Return ONLY the complete updated text of `SKILL.md`.
   Start immediately with the YAML frontmatter (`---`).
   Do NOT enclose the entire output in extra Markdown backtick code blocks (e.g. no leading ```markdown and no trailing ```).
"""

    print("Sending prompt to Gemini API...")
    updated_skill = call_gemini(api_key, prompt)

    # Clean up output if wrapped in backticks
    updated_skill = updated_skill.strip()
    if updated_skill.startswith("```markdown"):
        updated_skill = updated_skill[len("```markdown"):].strip()
    elif updated_skill.startswith("```"):
        updated_skill = updated_skill[len("```"):].strip()
    if updated_skill.endswith("```"):
        updated_skill = updated_skill[:-3].strip()

    # Safety validation
    required_phrases = [
        "name:",
        "description:",
        "# CadQuery AI Skill",
        "## 2. Coordinate Spaces & Orientation"
    ]
    for phrase in required_phrases:
        if phrase not in updated_skill:
            print(f"ERROR: Generated SKILL.md failed safety validation (missing '{phrase}'). Aborting update.", file=sys.stderr)
            sys.exit(1)

    # Write updated SKILL.md
    with open(skill_file, "w", encoding="utf-8") as f:
        f.write(updated_skill + "\n")

    # Update .upstream_commit
    with open(commit_file, "w", encoding="utf-8") as f:
        f.write(new_commit + "\n")

    print("Successfully updated SKILL.md and advanced .upstream_commit.")

    # Write outputs for GitHub Actions
    set_github_output("docs_changed", "true")
    set_github_output("old_commit", old_commit[:7])
    set_github_output("new_commit", new_commit[:7])
    set_github_output("pr_title", f"Autonomous Update: CadQuery doc changes ({new_commit[:7]})")

    summary_file = os.path.join(os.path.dirname(skill_file), "update_summary.md")
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(f"### Upstream CadQuery Documentation Changes\n\n")
        f.write(f"Updated from `{old_commit[:7]}` to `{new_commit[:7]}`.\n\n")
        f.write(f"**Commits:**\n```\n{commit_log}\n```\n\n")
        f.write(f"**Files changed:**\n```\n{diff_stat}\n```\n")


if __name__ == "__main__":
    main()
