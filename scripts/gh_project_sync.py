#!/usr/bin/env python3
"""
gh_project_sync.py: Number Pii GitHub Project Orchestration Bridge

Deterministic wrapper around the GitHub CLI (`gh`) that connects a project's
planned backlog to a live GitHub Project board. It is the execution-layer half
of the GitHub Project Orchestration Layer; the rules it follows live in
GITHUB_ORCHESTRATION.md at the toolkit root.

The board is the single source of truth for what is claimed and what is free.
This script reads a structured backlog from doc/task-board.md, pushes it to
GitHub as issues, assigns owners, applies the standard labels, and queries the
board so any contributor (human or AI) can see current state before claiming.

Subcommands:
    push     Create issues from doc/task-board.md and add them to the project.
    assign   Set or clear an issue's owner and move its workflow state; the
             board Status field updates automatically. Refuses to take over a
             claimed item (assigned + In Progress) without --force.
    status   Set the project board Status field for one issue directly.
    sync     Write live board Status values back into doc/task-board.md.
    query    List open board items with owner, state, labels, and blockers.
    link     Record a blocked-by / blocks dependency between two issues.

Every subcommand accepts --dry-run, which prints the `gh` calls it would make
without running them. Run a dry run first.

Usage:
    python3 organisation/scripts/gh_project_sync.py query
    python3 organisation/scripts/gh_project_sync.py push --dry-run
    python3 organisation/scripts/gh_project_sync.py push
    python3 organisation/scripts/gh_project_sync.py assign --issue 42 \\
        --assignee octocat --state "In Progress"
    python3 organisation/scripts/gh_project_sync.py status --issue 42 --state Review
    python3 organisation/scripts/gh_project_sync.py sync
    python3 organisation/scripts/gh_project_sync.py link --issue 42 --blocked-by 40

Prerequisites:
    - GitHub CLI installed and authenticated: `gh auth login`
    - doc/task-board.md present with a Board Configuration table that names the
      GitHub Project number, project owner, and repository.

Requirements: Python 3.9+, no external dependencies.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

# ── Standard board vocabulary ─────────────────────────────────────────────────
# These mirror GITHUB_ORCHESTRATION.md. Keep the two in step: the spec is the
# human-facing contract, this list is what the script will create on the board.

WORKFLOW_STATES = ["Backlog", "Ready", "In Progress", "Review", "Blocked", "Completed"]

AREA_LABELS = ["backend", "frontend", "devops", "security", "docs", "design"]
PRIORITY_LABELS = ["p0", "p1", "p2", "urgent"]
MARKER_LABELS = ["blocked", "human", "agent"]

# Colours are cosmetic; gh accepts a 6-char hex without the leading hash.
LABEL_COLOURS = {
    "backend": "1d76db", "frontend": "5319e7", "devops": "0e8a16",
    "security": "b60205", "docs": "0052cc", "design": "d93f0b",
    "p0": "b60205", "p1": "d93f0b", "p2": "fbca04", "urgent": "e11d21",
    "blocked": "000000", "human": "0e8a16", "agent": "5319e7",
}

DEFAULT_BOARD = Path("doc/task-board.md")


# ── Errors and process helpers ────────────────────────────────────────────────

class BoardError(Exception):
    """A precondition or configuration problem the user must fix."""


def escalate(message: str) -> None:
    """Print a clear, actionable message and exit non-zero.

    The toolkit's posture is to stop and surface a missing precondition rather
    than guess around it.
    """
    print(f"\nERROR: {message}\n", file=sys.stderr)
    raise SystemExit(1)


def run_gh(args: list[str], dry_run: bool, capture: bool = False) -> str | None:
    """Run a `gh` command, or print it under --dry-run.

    Returns captured stdout when capture is True and the command ran for real;
    returns None under --dry-run or when not capturing.
    """
    printable = "gh " + " ".join(_quote(a) for a in args)
    if dry_run:
        print(f"  [dry-run] {printable}")
        return None
    try:
        result = subprocess.run(
            ["gh", *args],
            check=True,
            text=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        escalate(f"`{printable}` failed:\n  {stderr}")
        return None  # unreachable; escalate raises
    return result.stdout if capture else None


def _quote(arg: str) -> str:
    """Quote an argument for the printed preview when it contains spaces."""
    return f'"{arg}"' if (" " in arg or not arg) else arg


def check_gh_available() -> None:
    if shutil.which("gh") is None:
        escalate(
            "GitHub CLI (`gh`) is not installed or not on PATH.\n"
            "  Install it from https://cli.github.com/ then run `gh auth login`."
        )


def check_gh_auth() -> None:
    try:
        subprocess.run(["gh", "auth", "status"], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError:
        escalate(
            "GitHub CLI is not authenticated.\n"
            "  Run `gh auth login`, then `gh auth status` to confirm."
        )


def require_live_preconditions(dry_run: bool) -> None:
    """Checks needed before touching GitHub for real. Skipped under --dry-run so
    a preview works offline."""
    check_gh_available()
    if not dry_run:
        check_gh_auth()


# ── Board file parsing ────────────────────────────────────────────────────────

def _parse_markdown_table(lines: list[str]) -> list[dict]:
    """Parse one GitHub-flavoured markdown table into a list of row dicts keyed
    by lower-cased header. Stops at the first blank line after the table starts.
    """
    rows: list[dict] = []
    header: list[str] | None = None
    for raw in lines:
        line = raw.strip()
        if not line.startswith("|"):
            if header is not None:
                break  # table ended
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if set("".join(cells)) <= {"-", ":", " "}:
            continue  # the |---|---| separator row
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if len(cells) < len(header):
            cells += [""] * (len(header) - len(cells))
        rows.append(dict(zip(header, cells)))
    return rows


def _section_lines(text: str, heading: str) -> list[str]:
    """Return the lines under a `## heading` up to the next `## ` heading."""
    out: list[str] = []
    collecting = False
    for line in text.splitlines():
        if line.strip().startswith("## "):
            if collecting:
                break
            collecting = line.strip()[3:].strip().lower() == heading.lower()
            continue
        if collecting:
            out.append(line)
    return out


def parse_board(path: Path) -> tuple[dict, list[dict]]:
    """Return (config, tasks) parsed from doc/task-board.md.

    config keys: project_number, project_owner, repository.
    Each task is a dict from the Backlog table (lower-cased column names).
    """
    if not path.exists():
        escalate(
            f"Board file not found: {path}\n"
            "  Scaffold it with scripts/init_project.py, or pass --board <path>."
        )
    text = path.read_text(encoding="utf-8")
    # Strip HTML comments first; they carry template guidance and example table rows
    # that must never be parsed as real configuration or backlog items.
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)

    config_rows = _parse_markdown_table(_section_lines(text, "Board Configuration"))
    config: dict[str, str] = {}
    for row in config_rows:
        setting = row.get("setting", "").lower()
        value = row.get("value", "").strip()
        if value.upper().startswith("TODO") or value in ("", "<number>", "<owner/repo>"):
            value = ""
        if "project number" in setting:
            config["project_number"] = value
        elif "project owner" in setting:
            config["project_owner"] = value
        elif "repository" in setting:
            config["repository"] = value

    tasks = _parse_markdown_table(_section_lines(text, "Backlog"))
    return config, tasks


def require_config(config: dict, *keys: str) -> None:
    missing = [k for k in keys if not config.get(k)]
    if missing:
        names = ", ".join(k.replace("_", " ") for k in missing)
        escalate(
            f"doc/task-board.md is missing required Board Configuration: {names}.\n"
            "  Fill the Board Configuration table before syncing."
        )


# ── Label management ──────────────────────────────────────────────────────────

def ensure_labels(repo: str, dry_run: bool) -> None:
    """Create or update the standard label set. `--force` makes this idempotent:
    it updates an existing label rather than failing."""
    for label in AREA_LABELS + PRIORITY_LABELS + MARKER_LABELS:
        colour = LABEL_COLOURS.get(label, "ededed")
        run_gh(
            ["label", "create", label, "--repo", repo, "--color", colour, "--force"],
            dry_run,
        )


def labels_for_task(task: dict) -> list[str]:
    """Derive the label set for a backlog row from its area, priority, owner type,
    and state."""
    labels: list[str] = []
    area = task.get("area", "").strip().lower()
    if area in AREA_LABELS:
        labels.append(area)
    priority = task.get("priority", "").strip().lower()
    if priority in PRIORITY_LABELS:
        labels.append(priority)
    owner_type = task.get("owner type", task.get("owner_type", "")).strip().lower()
    if owner_type in ("human", "agent"):
        labels.append(owner_type)
    if task.get("state", "").strip().lower() == "blocked":
        labels.append("blocked")
    return labels


# ── Issue body ────────────────────────────────────────────────────────────────

def issue_body(task: dict) -> str:
    """Build an issue body that records the owner, state, and dependencies so the
    board carries the full task context, including the agent owner that GitHub
    cannot hold as an assignee."""
    owner = task.get("owner", "").strip() or "unassigned"
    owner_type = task.get("owner type", task.get("owner_type", "")).strip() or "unspecified"
    state = task.get("state", "").strip() or "Backlog"
    depends = task.get("depends on", task.get("depends_on", "")).strip() or "none"
    lines = [
        "## Owner",
        f"{owner} ({owner_type})",
        "",
        "## Workflow State",
        state,
        "",
        "## Dependencies",
        depends,
        "",
        "---",
        "_Synced from doc/task-board.md by the Number Pii orchestration layer._",
    ]
    return "\n".join(lines)


# ── Project lookups ───────────────────────────────────────────────────────────

def existing_issue_titles(repo: str, dry_run: bool) -> set[str]:
    """Titles of issues already in the repo, so push stays idempotent."""
    out = run_gh(
        ["issue", "list", "--repo", repo, "--state", "all",
         "--limit", "1000", "--json", "title"],
        dry_run, capture=True,
    )
    if not out:
        return set()
    try:
        return {item["title"] for item in json.loads(out)}
    except (json.JSONDecodeError, KeyError):
        return set()


# ── Project board Status control (GraphQL via gh project) ────────────────────

def find_status_field(fields: list[dict]) -> tuple[str, dict[str, str]]:
    """From `gh project field-list` JSON, return (field_id, {option name lower: option_id})
    for the single-select Status field; ("", {}) when the project has none."""
    for field in fields:
        if field.get("name", "").strip().lower() == "status":
            options = {
                o.get("name", "").strip().lower(): o.get("id", "")
                for o in field.get("options", [])
            }
            return field.get("id", ""), options
    return "", {}


def find_project_item(items: list[dict], repo: str, issue_number: int) -> dict:
    """From `gh project item-list` JSON, the item whose content is repo#issue_number."""
    for item in items:
        content = item.get("content") or {}
        if (content.get("number") == issue_number
                and content.get("repository", "").lower() == repo.lower()):
            return item
    return {}


def _project_json(args: list[str], dry_run: bool) -> dict:
    out = run_gh(args, dry_run, capture=True)
    if out is None:
        return {}
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        escalate(f"`gh {args[0]} {args[1]}` returned unparseable JSON.")
        return {}  # unreachable


def get_board_status(config: dict, issue_number: int, dry_run: bool) -> str:
    """The project board Status value for an issue, or '' when unknown."""
    data = _project_json(
        ["project", "item-list", config["project_number"], "--owner",
         config["project_owner"], "--format", "json", "--limit", "1000"],
        dry_run,
    )
    item = find_project_item(data.get("items", []), config["repository"], issue_number)
    return (item.get("status") or "").strip()


def set_board_status(config: dict, issue_number: int, state: str, dry_run: bool) -> None:
    """Set the project board Status field for an issue via the Projects v2 API."""
    number, owner, repo = (config["project_number"], config["project_owner"],
                           config["repository"])
    if dry_run:
        print(f"  [dry-run] would set project {number} Status of {repo}#{issue_number} "
              f"to '{state}' via gh project item-edit")
        return

    fields = _project_json(
        ["project", "field-list", number, "--owner", owner,
         "--format", "json", "--limit", "100"], dry_run).get("fields", [])
    field_id, options = find_status_field(fields)
    if not field_id:
        escalate(f"Project {number} has no Status field; add one on GitHub first.")
    option_id = options.get(state.strip().lower())
    if not option_id:
        escalate(
            f"Project {number} Status has no option named '{state}'.\n"
            f"  Available options: {', '.join(sorted(options)) or 'none'}.\n"
            "  Add the standard workflow states to the board (GITHUB_ORCHESTRATION.md)."
        )

    items = _project_json(
        ["project", "item-list", number, "--owner", owner,
         "--format", "json", "--limit", "1000"], dry_run).get("items", [])
    item = find_project_item(items, repo, issue_number)
    if not item:
        escalate(f"Issue {repo}#{issue_number} is not on project {number}; run `push` first.")

    project_id = _project_json(
        ["project", "view", number, "--owner", owner, "--format", "json"],
        dry_run).get("id", "")
    if not project_id:
        escalate(f"Could not resolve the node ID for project {number}.")

    run_gh(
        ["project", "item-edit", "--id", item["id"], "--project-id", project_id,
         "--field-id", field_id, "--single-select-option-id", option_id],
        dry_run,
    )
    print(f"  [ok] board Status of {repo}#{issue_number} set to '{state}'")


def reassignment_needs_force(current_assignees: list[str], new_assignee: str,
                             status: str) -> bool:
    """The ownership lock: an In Progress item held by someone else is claimed;
    taking it over requires an explicit --force."""
    if not new_assignee or not current_assignees:
        return False
    if new_assignee in current_assignees:
        return False
    return status.strip().lower() == "in progress"


# ── Board write-back ──────────────────────────────────────────────────────────

def rewrite_board_states(text: str, statuses: dict[str, str]) -> tuple[str, list[str], list[str]]:
    """Update the State column of Backlog table rows from live board statuses.

    Returns (new_text, updated titles, titles with no live match). Rows inside
    HTML comments (template examples) are never touched.
    """
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    updated: list[str] = []
    unmatched: list[str] = []

    in_backlog = False
    in_comment = False
    header: list[str] | None = None

    for raw in lines:
        line = raw.strip()
        if "<!--" in line and "-->" not in line:
            in_comment = True
        elif in_comment and "-->" in line:
            in_comment = False
            out.append(raw)
            continue

        if line.startswith("## "):
            in_backlog = line[3:].strip().lower() == "backlog"
            header = None

        if in_comment or not in_backlog or not line.startswith("|"):
            out.append(raw)
            continue

        cells = [c.strip() for c in line.strip("|").split("|")]
        if set("".join(cells)) <= {"-", ":", " "}:
            out.append(raw)
            continue
        if header is None:
            header = [c.lower() for c in cells]
            out.append(raw)
            continue

        try:
            title_i = header.index("title")
            state_i = header.index("state")
        except ValueError:
            out.append(raw)
            continue
        if len(cells) <= max(title_i, state_i):
            out.append(raw)
            continue

        title = cells[title_i]
        live = statuses.get(title)
        if live is None:
            unmatched.append(title)
            out.append(raw)
            continue
        if cells[state_i] != live:
            cells[state_i] = live
            updated.append(title)
            newline = "\n" if raw.endswith("\n") else ""
            out.append("| " + " | ".join(cells) + " |" + newline)
        else:
            out.append(raw)

    return "".join(out), updated, unmatched


# ── Subcommands ───────────────────────────────────────────────────────────────

def cmd_push(args: argparse.Namespace) -> int:
    require_live_preconditions(args.dry_run)
    config, tasks = parse_board(Path(args.board))
    require_config(config, "project_number", "project_owner", "repository")
    repo = config["repository"]
    number = config["project_number"]
    owner = config["project_owner"]

    if not tasks:
        print("No backlog rows found under '## Backlog' in the board file. Nothing to push.")
        return 0

    ensure_labels(repo, args.dry_run)
    already = existing_issue_titles(repo, args.dry_run)

    created = 0
    skipped = 0
    for task in tasks:
        title = task.get("title", "").strip()
        if not title:
            continue
        if title in already:
            print(f"  [skip] issue already exists: {title}")
            skipped += 1
            continue

        create_args = ["issue", "create", "--repo", repo, "--title", title,
                       "--body", issue_body(task)]
        for label in labels_for_task(task):
            create_args += ["--label", label]
        url = run_gh(create_args, args.dry_run, capture=True)
        created += 1

        # Add the new issue to the project board. Under --dry-run there is no URL
        # to chain, so show the intended call with a placeholder.
        item_url = (url or "").strip() or "<issue-url>"
        run_gh(
            ["project", "item-add", number, "--owner", owner, "--url", item_url],
            args.dry_run,
        )
        print(f"  [ok]   {title}")

    print(f"\nPush complete: {created} created, {skipped} skipped (already on board).")
    if args.dry_run:
        print("This was a dry run. Re-run without --dry-run to apply.")
    return 0


def cmd_assign(args: argparse.Namespace) -> int:
    require_live_preconditions(args.dry_run)
    config, _ = parse_board(Path(args.board))
    require_config(config, "repository")
    repo = config["repository"]

    # Ownership lock: an In Progress item with a different assignee is claimed.
    if args.assignee and not args.force and not args.dry_run:
        view = run_gh(
            ["issue", "view", str(args.issue), "--repo", repo, "--json", "assignees"],
            args.dry_run, capture=True,
        )
        try:
            current = [a["login"] for a in json.loads(view or "{}").get("assignees", [])]
        except (json.JSONDecodeError, KeyError, TypeError):
            current = []
        if current and args.assignee not in current:
            require_config(config, "project_number", "project_owner")
            status = get_board_status(config, args.issue, args.dry_run)
            if reassignment_needs_force(current, args.assignee, status):
                escalate(
                    f"Issue #{args.issue} is claimed: assigned to "
                    f"{', '.join(current)} and In Progress.\n"
                    "  Taking over a claimed task needs agreement with the owner or the "
                    "project lead;\n  re-run with --force to record the reassignment."
                )

    edit_args = ["issue", "edit", str(args.issue), "--repo", repo]
    if args.assignee:
        edit_args += ["--add-assignee", args.assignee]
    if args.unassign:
        edit_args += ["--remove-assignee", args.unassign]
    if args.state:
        if args.state not in WORKFLOW_STATES:
            escalate(f"Unknown state '{args.state}'. Use one of: {', '.join(WORKFLOW_STATES)}.")
        # Mirror the Blocked state with the matching label for label-based filters.
        if args.state == "Blocked":
            edit_args += ["--add-label", "blocked"]
        else:
            edit_args += ["--remove-label", "blocked"]

    if len(edit_args) <= 4:
        escalate("Nothing to change. Pass --assignee, --unassign, and/or --state.")

    run_gh(edit_args, args.dry_run)

    if args.state:
        require_config(config, "project_number", "project_owner")
        set_board_status(config, args.issue, args.state, args.dry_run)
    print("Done." if not args.dry_run else "Dry run complete.")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    require_live_preconditions(args.dry_run)
    config, _ = parse_board(Path(args.board))
    require_config(config, "project_number", "project_owner", "repository")

    if args.state not in WORKFLOW_STATES:
        escalate(f"Unknown state '{args.state}'. Use one of: {', '.join(WORKFLOW_STATES)}.")

    set_board_status(config, args.issue, args.state, args.dry_run)

    # Keep the blocked label mirror in step, matching assign --state.
    label_args = ["issue", "edit", str(args.issue), "--repo", config["repository"]]
    if args.state == "Blocked":
        label_args += ["--add-label", "blocked"]
    else:
        label_args += ["--remove-label", "blocked"]
    run_gh(label_args, args.dry_run)
    print("Done." if not args.dry_run else "Dry run complete.")
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    require_live_preconditions(args.dry_run)
    board_path = Path(args.board)
    config, _ = parse_board(board_path)
    require_config(config, "project_number", "project_owner", "repository")

    if args.dry_run:
        print("  [dry-run] would read project item statuses and rewrite the State "
              f"column of {board_path}")
        return 0

    data = _project_json(
        ["project", "item-list", config["project_number"], "--owner",
         config["project_owner"], "--format", "json", "--limit", "1000"],
        args.dry_run,
    )
    statuses = {}
    for item in data.get("items", []):
        content = item.get("content") or {}
        title = (content.get("title") or item.get("title") or "").strip()
        status = (item.get("status") or "").strip()
        if title and status:
            statuses[title] = status

    text = board_path.read_text(encoding="utf-8")
    new_text, updated, unmatched = rewrite_board_states(text, statuses)

    if updated:
        board_path.write_text(new_text, encoding="utf-8")
    print(f"\nSync complete: {len(updated)} row(s) updated from the live board.")
    for title in updated:
        print(f"  [ok]   {title} -> {statuses[title]}")
    for title in unmatched:
        print(f"  [warn] no live board item matches: {title}")
    if unmatched:
        print("  (Unmatched rows keep their file state; check titles or run `push`.)")
    return 0


def cmd_query(args: argparse.Namespace) -> int:
    require_live_preconditions(args.dry_run)
    config, _ = parse_board(Path(args.board))
    require_config(config, "repository")
    repo = config["repository"]

    out = run_gh(
        ["issue", "list", "--repo", repo, "--state", "open", "--limit", "1000",
         "--json", "number,title,assignees,labels"],
        args.dry_run, capture=True,
    )
    if args.dry_run:
        print("Dry run: the command above lists open board items for awareness.")
        return 0
    if args.json:
        print(out or "[]")
        return 0

    items = json.loads(out) if out else []
    if not items:
        print("No open issues on the board.")
        return 0

    print(f"\nOpen board items in {repo} (read this before claiming work):\n")
    print(f"  {'#':>5}  {'Owner':<20} {'Labels':<28} Title")
    print("  " + "-" * 78)
    for it in items:
        assignees = ", ".join(a["login"] for a in it.get("assignees", [])) or "unassigned"
        labels = ", ".join(l["name"] for l in it.get("labels", [])) or "-"
        print(f"  {it['number']:>5}  {assignees[:20]:<20} {labels[:28]:<28} {it['title']}")
    print()
    return 0


def cmd_link(args: argparse.Namespace) -> int:
    require_live_preconditions(args.dry_run)
    config, _ = parse_board(Path(args.board))
    require_config(config, "repository")
    repo = config["repository"]

    # v1 records the dependency as a comment and a blocked label. A full
    # dependency graph is deferred to a later version.
    note = f"Depends on #{args.blocked_by} (blocked-by). Recorded by the orchestration layer."
    run_gh(["issue", "comment", str(args.issue), "--repo", repo, "--body", note],
           args.dry_run)
    run_gh(["issue", "edit", str(args.issue), "--repo", repo, "--add-label", "blocked"],
           args.dry_run)
    run_gh(
        ["issue", "comment", str(args.blocked_by), "--repo", repo,
         "--body", f"Blocks #{args.issue}. Recorded by the orchestration layer."],
        args.dry_run,
    )
    print(f"Linked #{args.issue} as blocked-by #{args.blocked_by}.")
    return 0


# ── Entry point ───────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sync a Number Pii project backlog to a GitHub Project board.",
    )
    parser.add_argument("--board", default=str(DEFAULT_BOARD),
                        help=f"Path to the board file (default: {DEFAULT_BOARD})")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the gh commands without running them")
    sub = parser.add_subparsers(dest="command", required=True)

    p_push = sub.add_parser("push", help="Create issues from the board file and add them to the project")

    p_assign = sub.add_parser("assign", help="Set/clear an owner and move workflow state")
    p_assign.add_argument("--issue", required=True, type=int, help="Issue number")
    p_assign.add_argument("--assignee", help="GitHub username to assign (the claim)")
    p_assign.add_argument("--unassign", help="GitHub username to remove (release the claim)")
    p_assign.add_argument("--state", help=f"Workflow state: {', '.join(WORKFLOW_STATES)}")
    p_assign.add_argument("--force", action="store_true",
                          help="Take over a claimed (assigned + In Progress) item")

    p_status = sub.add_parser("status", help="Set the project board Status field for an issue")
    p_status.add_argument("--issue", required=True, type=int, help="Issue number")
    p_status.add_argument("--state", required=True,
                          help=f"Workflow state: {', '.join(WORKFLOW_STATES)}")

    p_sync = sub.add_parser("sync", help="Write live board Status values back into doc/task-board.md")

    p_query = sub.add_parser("query", help="List open board items for awareness before claiming")
    p_query.add_argument("--json", action="store_true", help="Emit raw JSON instead of a table")

    p_link = sub.add_parser("link", help="Record a blocked-by dependency between two issues")
    p_link.add_argument("--issue", required=True, type=int, help="The dependent issue")
    p_link.add_argument("--blocked-by", required=True, type=int, dest="blocked_by",
                        help="The issue that must finish first")

    # Accept --dry-run after the subcommand too, not only before it. SUPPRESS keeps an
    # absent post-subcommand flag from overwriting a value already set before it.
    for sp in (p_push, p_assign, p_status, p_sync, p_query, p_link):
        sp.add_argument("--dry-run", action="store_true", default=argparse.SUPPRESS,
                        help="Print the gh commands without running them")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "json"):
        args.json = False

    dispatch = {
        "push": cmd_push,
        "assign": cmd_assign,
        "status": cmd_status,
        "sync": cmd_sync,
        "query": cmd_query,
        "link": cmd_link,
    }
    try:
        return dispatch[args.command](args)
    except BoardError as exc:
        escalate(str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())
