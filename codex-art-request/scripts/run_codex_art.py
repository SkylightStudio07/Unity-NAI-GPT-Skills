"""Run the local Codex CLI for an art job and report what it changed.

Run from the project root (or pass --root). Never touches Codex credentials and never disables the sandbox.
"""
import argparse
import glob
import os
import subprocess
import sys
from pathlib import Path

LOG_NAMES = ("_codex_last.txt", "_codex_log.txt")


def find_codex():
    """codex.exe lives inside the Codex app bundle, in a folder that changes with updates."""
    candidates = []
    local = os.environ.get("LOCALAPPDATA")
    if local:
        candidates += glob.glob(str(Path(local) / "OpenAI" / "Codex" / "bin" / "*" / "codex.exe"))
    if candidates:
        return max(candidates, key=os.path.getmtime)
    from shutil import which
    found = which("codex")
    if found:
        return found
    sys.exit("codex not found (looked in %LOCALAPPDATA%/OpenAI/Codex/bin/*/ and PATH). Is the Codex app installed?")


def scope_state(scope):
    """mtime/size of every file under the scope, git-ignored or not."""
    state = {}
    for p in scope.rglob("*"):
        if p.is_file() and p.name not in LOG_NAMES:
            st = p.stat()
            state[p.relative_to(scope).as_posix()] = (st.st_mtime_ns, st.st_size)
    return state


def git_state(root):
    """Changed files according to git, or None outside a repository."""
    r = subprocess.run(["git", "-c", "core.quotepath=false", "status", "--porcelain", "-uall"],
                       cwd=root, capture_output=True, text=True, encoding="utf-8")
    if r.returncode:
        return None
    state = {}
    for line in r.stdout.splitlines():
        path = line[3:].strip().strip('"')
        p = root / path
        state[path] = (line[:2], p.stat().st_mtime_ns if p.is_file() else None)
    return state


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="project root Codex runs in (default: current folder)")
    ap.add_argument("--scope", help="folder the job may write to, relative to --root")
    ap.add_argument("--request", help="request .md for Codex to follow")
    ap.add_argument("--prompt", help="free-form instruction instead of --request")
    ap.add_argument("--image", action="append", default=[], help="image to attach, repeatable")
    ap.add_argument("--model", help="override the Codex default model")
    ap.add_argument("--timeout", type=int, default=3600, help="seconds")
    ap.add_argument("--check", action="store_true", help="read-only login test, no image")
    args = ap.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    root = Path(args.root).resolve()
    codex = find_codex()

    if args.check:
        cmd = [codex, "exec", "-C", str(root), "-s", "read-only", "--ephemeral", "--color", "never", "-"]
        r = subprocess.run(cmd, input="Reply with exactly: OK. Do not run commands or edit files.",
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
        print(r.stdout[-1500:])
        if r.returncode:
            print(r.stderr[-1500:])
        print("exit", r.returncode)
        sys.exit(r.returncode)

    if not args.scope or not (args.request or args.prompt):
        sys.exit("Need --scope and either --request or --prompt.")
    scope = (root / args.scope).resolve()
    try:
        scope_rel = scope.relative_to(root).as_posix()
    except ValueError:
        sys.exit("--scope must be inside --root.")
    if scope_rel == ".":
        sys.exit("--scope must be a subfolder, not the project root.")
    scope.mkdir(parents=True, exist_ok=True)
    scope_prefix = scope_rel.rstrip("/") + "/"

    if args.request:
        prompt = (f"Follow the request file `{Path(args.request).as_posix()}` exactly. Read it and the files it names. "
                  f"Write only inside `{scope_prefix}`. Do not edit, move or delete anything outside that folder. "
                  "Do not use git. Use the imagegen tool for anything that must be drawn, and do not use SVG. "
                  "Finish with a short summary of the files you delivered and anything you could not do.")
    else:
        prompt = args.prompt

    last = scope / LOG_NAMES[0]
    log = scope / LOG_NAMES[1]
    cmd = [codex, "exec", "-C", str(root), "-s", "workspace-write", "--color", "never", "-o", str(last)]
    if args.model:
        cmd += ["-m", args.model]
    for image in args.image:
        cmd += ["-i", str(Path(image).resolve())]
    cmd.append("-")

    scope_before, git_before = scope_state(scope), git_state(root)
    with open(log, "w", encoding="utf-8") as f:
        try:
            r = subprocess.run(cmd, input=prompt, stdout=f, stderr=subprocess.STDOUT, cwd=root,
                               text=True, encoding="utf-8", errors="replace", timeout=args.timeout)
            code = r.returncode
        except subprocess.TimeoutExpired:
            code = 124
    scope_after, git_after = scope_state(scope), git_state(root)

    inside = sorted(p for p in set(scope_before) | set(scope_after) if scope_before.get(p) != scope_after.get(p))
    print(f"exit {code}")
    print(f"changed inside scope: {len(inside)}")
    for p in inside[:60]:
        print(f"  {scope_prefix}{p}" + ("  (deleted)" if p not in scope_after else ""))

    if git_before is None or git_after is None:
        print("NOTE not a git repository: changes outside the scope were not checked.")
    else:
        outside = sorted(p for p in set(git_before) | set(git_after)
                         if git_before.get(p) != git_after.get(p) and not p.startswith(scope_prefix))
        if outside:
            print(f"WARNING changed OUTSIDE scope: {len(outside)}")
            for p in outside[:60]:
                print("  " + p)

    if last.exists():
        print("--- final message ---")
        print(last.read_text(encoding="utf-8", errors="replace")[:3000])
    else:
        print(f"No final message. See {log}")
    sys.exit(code)


if __name__ == "__main__":
    main()
