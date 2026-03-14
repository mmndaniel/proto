#!/usr/bin/env python3
"""Extract metrics and behavioral checks from a Claude Code session transcript.

Usage: measure-session.py <session-dir-or-jsonl>

Reads the main session JSONL and any subagent transcripts.
Reports: timing, tokens, agent spawns, tool calls, and behavioral checks.
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def parse_transcript(path):
    """Parse a JSONL transcript and return metrics."""
    messages = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                messages.append(json.loads(line))

    timed_events = []
    input_tokens = 0
    output_tokens = 0
    cache_read = 0
    cache_create = 0
    assistant_turns = 0
    tool_calls = {}
    tool_details = []  # (tool_name, input_dict) for behavioral analysis
    agent_spawns = []
    text_outputs = []  # assistant text blocks

    for msg in messages:
        ts = msg.get("timestamp")
        msg_type = msg.get("type", "")
        if ts and msg_type in ("assistant", "user", "tool_result", "system"):
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                timed_events.append((dt, msg_type))
            except Exception:
                pass

        if msg.get("type") == "assistant":
            assistant_turns += 1
            usage = msg.get("message", {}).get("usage", {})
            if usage:
                input_tokens += usage.get("input_tokens", 0)
                output_tokens += usage.get("output_tokens", 0)
                cache_read += usage.get("cache_read_input_tokens", 0)
                cache_create += usage.get("cache_creation_input_tokens", 0)

            content = msg.get("message", {}).get("content", [])
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict):
                        if block.get("type") == "tool_use":
                            name = block.get("name", "unknown")
                            inp = block.get("input", {})
                            tool_calls[name] = tool_calls.get(name, 0) + 1
                            tool_details.append((name, inp))
                            if name == "Agent":
                                agent_spawns.append({
                                    "description": inp.get("description", ""),
                                    "subagent_type": inp.get("subagent_type", ""),
                                    "background": inp.get("run_in_background", False),
                                    "prompt": inp.get("prompt", ""),
                                })
                        elif block.get("type") == "text":
                            text_outputs.append(block.get("text", ""))

    wall_seconds = 0
    active_seconds = 0
    idle_seconds = 0
    if len(timed_events) >= 2:
        wall_seconds = (timed_events[-1][0] - timed_events[0][0]).total_seconds()
        for i in range(1, len(timed_events)):
            gap = (timed_events[i][0] - timed_events[i - 1][0]).total_seconds()
            if gap > 15:
                idle_seconds += gap
            else:
                active_seconds += gap

    return {
        "file": str(path),
        "wall_seconds": wall_seconds,
        "active_seconds": active_seconds,
        "idle_seconds": idle_seconds,
        "assistant_turns": assistant_turns,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cache_read_tokens": cache_read,
        "cache_create_tokens": cache_create,
        "total_tokens": input_tokens + output_tokens + cache_read + cache_create,
        "tool_calls": tool_calls,
        "tool_details": tool_details,
        "agent_spawns": agent_spawns,
        "text_outputs": text_outputs,
    }


def check_behaviors(main, subagents, subagent_metas):
    """Run behavioral checks and return list of (status, description)."""
    checks = []

    # 1. Skill invoked
    skill_used = main["tool_calls"].get("Skill", 0) > 0
    checks.append(("PASS" if skill_used else "FAIL", "Skill invoked"))

    # 2. Orchestrator never wrote implementation files
    source_writes = []
    for name, inp in main["tool_details"]:
        if name in ("Write", "Edit"):
            path = inp.get("file_path", "")
            base = Path(path).name
            if base.upper() not in ("PROGRESS.MD", "PLAN.MD", "CLAUDE.MD", "SPEC.MD", "PRD.MD", "ARCHITECTURE.MD"):
                source_writes.append(path)
    checks.append(("PASS" if not source_writes else "FAIL",
                    f"Orchestrator didn't write source files" +
                    (f" (wrote: {', '.join(source_writes)})" if source_writes else "")))

    # 3. Orchestrator didn't read implementation files
    source_reads = []
    for name, inp in main["tool_details"]:
        if name == "Read":
            path = inp.get("file_path", "")
            base = Path(path).name
            project_files = {"PROGRESS.MD", "PLAN.MD", "CLAUDE.MD", "SPEC.MD", "PRD.MD", "ARCHITECTURE.MD"}
            if base.upper() not in project_files and not path.endswith("SKILL.md") and "references/" not in path and "subagent-prompt-template" not in path:
                source_reads.append(path)
    checks.append(("PASS" if not source_reads else "WARN",
                    f"Orchestrator didn't read source files" +
                    (f" (read: {', '.join(source_reads[:3])})" if source_reads else "")))

    # 4. All implementers are background
    impl_spawns = [s for s in main["agent_spawns"] if s["subagent_type"] == "implementer"]
    all_bg = all(s["background"] for s in impl_spawns) if impl_spawns else False
    checks.append(("PASS" if all_bg else "FAIL",
                    f"All implementers background ({len(impl_spawns)} spawned)"))

    # 5. Integrator used
    integ_spawns = [s for s in main["agent_spawns"] if s["subagent_type"] == "integrator"]
    checks.append(("PASS" if integ_spawns else "FAIL",
                    f"Integrator used ({len(integ_spawns)} spawned)"))

    # 6. Check subagent git commands (implementers should NOT run git)
    impl_git_cmds = 0
    integ_merge_cmds = 0
    for sa, meta in zip(subagents, subagent_metas):
        agent_type = meta.get("agentType", "unknown")
        for name, inp in sa["tool_details"]:
            if name == "Bash":
                cmd = inp.get("command", "")
                if agent_type == "implementer" and ("git add" in cmd or "git commit" in cmd):
                    impl_git_cmds += 1
                if agent_type == "integrator" and "git merge" in cmd:
                    integ_merge_cmds += 1
    checks.append(("PASS" if impl_git_cmds == 0 else "WARN",
                    f"Implementers avoided git commands ({impl_git_cmds} git add/commit calls)"))
    checks.append(("PASS" if integ_merge_cmds > 0 else "FAIL",
                    f"Integrator used git merge ({integ_merge_cmds} merge calls)"))

    # 7. No TaskCreate/TaskUpdate (should use PROGRESS.md)
    task_calls = main["tool_calls"].get("TaskCreate", 0) + main["tool_calls"].get("TaskUpdate", 0)
    checks.append(("PASS" if task_calls == 0 else "WARN",
                    f"No TaskCreate/TaskUpdate ({task_calls} calls)"))

    # 8. Check if orchestrator asked user (for underspecified tasks)
    asked_user = False
    all_text = " ".join(main["text_outputs"]).lower()
    ask_indicators = ["which do you", "what would you", "could you clarify",
                      "not yet decided", "not specified", "need your input",
                      "which approach", "what should"]
    for indicator in ask_indicators:
        if indicator in all_text:
            asked_user = True
            break
    ask_tool = main["tool_calls"].get("AskUserQuestion", 0) > 0
    if ask_tool:
        asked_user = True
    checks.append(("INFO", f"Orchestrator asked user for input: {'yes' if asked_user else 'no'}"))

    # 9. Check if PROGRESS.md was updated incrementally (not just at end)
    progress_edits = sum(1 for name, inp in main["tool_details"]
                         if name == "Edit" and "PROGRESS" in inp.get("file_path", "").upper())
    checks.append(("PASS" if progress_edits >= 2 else "WARN",
                    f"Progress updated incrementally ({progress_edits} edits)"))

    return checks


def fmt_time(seconds):
    if seconds < 60:
        return f"{seconds:.0f}s"
    m, s = divmod(int(seconds), 60)
    return f"{m}m {s}s"


def fmt_tokens(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def main():
    if len(sys.argv) < 2:
        print("Usage: measure-session.py <session-jsonl-or-dir>")
        sys.exit(1)

    target = Path(sys.argv[1])

    # Find main transcript
    if target.is_file() and target.suffix == ".jsonl":
        main_jsonl = target
        session_dir = target.parent / target.stem
    elif target.is_dir():
        jsonls = list(target.glob("*.jsonl"))
        if not jsonls:
            print(f"No .jsonl files in {target}")
            sys.exit(1)
        main_jsonl = max(jsonls, key=lambda p: p.stat().st_mtime)
        session_dir = target / main_jsonl.stem
    else:
        print(f"Not found: {target}")
        sys.exit(1)

    # Parse main transcript
    main_data = parse_transcript(main_jsonl)

    # Parse subagent transcripts and metadata
    subagent_dir = session_dir / "subagents"
    subagents = []
    subagent_metas = []
    if subagent_dir.exists():
        for sa_jsonl in sorted(subagent_dir.glob("*.jsonl")):
            subagents.append(parse_transcript(sa_jsonl))
            meta_path = sa_jsonl.with_suffix(".meta.json")
            meta = {}
            if meta_path.exists():
                with open(meta_path) as f:
                    meta = json.load(f)
            subagent_metas.append(meta)

    # Print report
    print("=" * 60)
    print("SESSION METRICS")
    print("=" * 60)
    print(f"  Wall time:       {fmt_time(main_data['wall_seconds'])}")
    print(f"  Active time:     {fmt_time(main_data['active_seconds'])}")
    print(f"  Idle time:       {fmt_time(main_data['idle_seconds'])}")
    print(f"  Assistant turns:  {main_data['assistant_turns']}")
    print(f"  Agent spawns:     {len(main_data['agent_spawns'])}")
    print()

    print("TOKENS (main agent)")
    print(f"  Input:           {fmt_tokens(main_data['input_tokens'])}")
    print(f"  Output:          {fmt_tokens(main_data['output_tokens'])}")
    print(f"  Cache read:      {fmt_tokens(main_data['cache_read_tokens'])}")
    print(f"  Cache create:    {fmt_tokens(main_data['cache_create_tokens'])}")
    print(f"  Total:           {fmt_tokens(main_data['total_tokens'])}")
    print()

    print("TOOL CALLS (main agent)")
    for tool, count in sorted(main_data["tool_calls"].items(), key=lambda x: -x[1]):
        print(f"  {tool:20s} {count}")
    print()

    if main_data["agent_spawns"]:
        print("AGENT SPAWNS")
        for i, spawn in enumerate(main_data["agent_spawns"], 1):
            bg = "background" if spawn["background"] else "foreground"
            print(f"  {i}. [{spawn['subagent_type'] or 'general'}] {spawn['description']} ({bg})")
        print()

    if subagents:
        print("SUBAGENT METRICS")
        total_sub_input = 0
        total_sub_output = 0
        for sa, meta in zip(subagents, subagent_metas):
            name = Path(sa["file"]).stem
            agent_type = meta.get("agentType", "unknown")
            total_sub_input += sa["input_tokens"]
            total_sub_output += sa["output_tokens"]
            print(f"  {name} ({agent_type})")
            print(f"    Turns: {sa['assistant_turns']}  Time: {fmt_time(sa['wall_seconds'])}  Out: {fmt_tokens(sa['output_tokens'])}")
            tools = ", ".join(f"{t}:{c}" for t, c in sorted(sa["tool_calls"].items(), key=lambda x: -x[1]))
            if tools:
                print(f"    Tools: {tools}")
        print()
        print(f"  Subagent totals:  in={fmt_tokens(total_sub_input)}  out={fmt_tokens(total_sub_output)}")
        print()

    # Grand total
    grand_input = main_data["input_tokens"] + sum(s["input_tokens"] for s in subagents)
    grand_output = main_data["output_tokens"] + sum(s["output_tokens"] for s in subagents)
    grand_total = grand_input + grand_output
    print("GRAND TOTAL")
    print(f"  Input:           {fmt_tokens(grand_input)}")
    print(f"  Output:          {fmt_tokens(grand_output)}")
    print(f"  Combined:        {fmt_tokens(grand_total)}")
    print()

    # Behavioral checks
    checks = check_behaviors(main_data, subagents, subagent_metas)
    print("BEHAVIORAL CHECKS")
    for status, desc in checks:
        icon = {"PASS": "+", "FAIL": "X", "WARN": "!", "INFO": "~"}[status]
        print(f"  [{icon}] {status:4s}  {desc}")
    print("=" * 60)


if __name__ == "__main__":
    main()
