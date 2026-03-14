# Proto - Development Guide

## What this is

A Claude Code plugin with three components:
- `skills/proto/SKILL.md` - orchestration skill (the main workflow)
- `agents/implementer.md` - subagent that implements tasks in isolated worktrees
- `agents/integrator.md` - subagent that merges worktree branches and runs integration tests

## Repository structure

```
proto/
├── .claude-plugin/plugin.json    # plugin manifest
├── skills/proto/                 # the skill
│   ├── SKILL.md                  # orchestration instructions
│   ├── scripts/init-project.sh   # project initialization
│   └── references/               # guides loaded on demand
├── agents/                       # subagent definitions
│   ├── implementer.md            # worktree + acceptEdits + stop hook
│   └── integrator.md             # merge + test
└── eval/                         # dev tooling, not part of the plugin
    └── measure-session.py        # session metrics extraction
```

## How to work on this

### Changing the skill
Edit `skills/proto/SKILL.md`. To test locally, copy to `~/.claude/skills/proto/SKILL.md` or use `claude --plugin-dir .` from this directory.

### Changing subagents
Edit files in `agents/`. Copy to `~/.claude/agents/` to test. The implementer has a Stop hook that auto-commits; this is defined in its frontmatter, not as a separate hook file.

### Testing changes
1. Reset the test project: delete implementation files, reset progress.md to all PENDING
2. Open a fresh Claude Code session in the test project directory
3. Say "continue the project"
4. Run `python3 eval/measure-session.py <session-jsonl>` to measure results

### What to measure
- **Active time**: wall time minus idle time (permission prompts, user away)
- **Main agent turns**: lower is better, means orchestrator stayed lean
- **Main agent output tokens**: lower means less context bloat
- **Subagent commits**: implementers should auto-commit via hook, never manually
- **Git merge usage**: integrator should use `git merge`, never manual file copying

### Key design decisions
- Orchestrator never writes code, merges branches, or reads implementation files
- Implementers never run git commands; the Stop hook commits automatically
- Integrator reads plan.md to understand task intent when resolving conflicts
- Progress updates happen after each batch, not just at the end (enables resumption)
- Project files (prd.md, architecture.md, plan.md) are the communication channel between orchestrator and subagents
