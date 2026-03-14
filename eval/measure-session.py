#!/usr/bin/env python3
"""Extract metrics from a Claude Code session transcript.

Usage: measure-session.py <session-dir-or-jsonl>

Reads the main session JSONL and any subagent transcripts.
Reports: wall time, turns, token usage, agent spawns, tool calls.
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

    timed_events = []  # (datetime, type) for active/idle calculation
    input_tokens = 0
    output_tokens = 0
    cache_read = 0
    cache_create = 0
    assistant_turns = 0
    tool_calls = {}
    agent_spawns = []

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
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        name = block.get("name", "unknown")
                        tool_calls[name] = tool_calls.get(name, 0) + 1
                        if name == "Agent":
                            inp = block.get("input", {})
                            agent_spawns.append({
                                "description": inp.get("description", ""),
                                "subagent_type": inp.get("subagent_type", ""),
                                "background": inp.get("run_in_background", False),
                            })

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
        "agent_spawns": agent_spawns,
    }


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
    main = parse_transcript(main_jsonl)

    # Parse subagent transcripts
    subagent_dir = session_dir / "subagents"
    subagents = []
    if subagent_dir.exists():
        for sa_jsonl in sorted(subagent_dir.glob("*.jsonl")):
            subagents.append(parse_transcript(sa_jsonl))

    # Print report
    print("=" * 60)
    print("SESSION METRICS")
    print("=" * 60)
    print(f"  Wall time:       {fmt_time(main['wall_seconds'])}")
    print(f"  Active time:     {fmt_time(main['active_seconds'])}")
    print(f"  Idle time:       {fmt_time(main['idle_seconds'])}")
    print(f"  Assistant turns:  {main['assistant_turns']}")
    print(f"  Agent spawns:     {len(main['agent_spawns'])}")
    print()

    print("TOKENS (main agent)")
    print(f"  Input:           {fmt_tokens(main['input_tokens'])}")
    print(f"  Output:          {fmt_tokens(main['output_tokens'])}")
    print(f"  Cache read:      {fmt_tokens(main['cache_read_tokens'])}")
    print(f"  Cache create:    {fmt_tokens(main['cache_create_tokens'])}")
    print(f"  Total:           {fmt_tokens(main['total_tokens'])}")
    print()

    print("TOOL CALLS (main agent)")
    for tool, count in sorted(main["tool_calls"].items(), key=lambda x: -x[1]):
        print(f"  {tool:20s} {count}")
    print()

    if main["agent_spawns"]:
        print("AGENT SPAWNS")
        for i, spawn in enumerate(main["agent_spawns"], 1):
            bg = "background" if spawn["background"] else "foreground"
            print(f"  {i}. [{spawn['subagent_type'] or 'general'}] {spawn['description']} ({bg})")
        print()

    if subagents:
        print("SUBAGENT METRICS")
        total_sub_input = 0
        total_sub_output = 0
        for sa in subagents:
            name = Path(sa["file"]).stem
            total_sub_input += sa["input_tokens"]
            total_sub_output += sa["output_tokens"]
            print(f"  {name}")
            print(f"    Turns: {sa['assistant_turns']}  Time: {fmt_time(sa['wall_seconds'])}  Out: {fmt_tokens(sa['output_tokens'])}")
            tools = ", ".join(f"{t}:{c}" for t, c in sorted(sa["tool_calls"].items(), key=lambda x: -x[1]))
            if tools:
                print(f"    Tools: {tools}")
        print()
        print(f"  Subagent totals:  in={fmt_tokens(total_sub_input)}  out={fmt_tokens(total_sub_output)}")
        print()

    # Grand total
    grand_input = main["input_tokens"] + sum(s["input_tokens"] for s in subagents)
    grand_output = main["output_tokens"] + sum(s["output_tokens"] for s in subagents)
    grand_total = grand_input + grand_output
    print("GRAND TOTAL")
    print(f"  Input:           {fmt_tokens(grand_input)}")
    print(f"  Output:          {fmt_tokens(grand_output)}")
    print(f"  Combined:        {fmt_tokens(grand_total)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
