# Proto

Idea to working prototype, fast. 12 files, no dependencies.

## Why this exists

Proto is one skill and two agent definitions. No MCP server, no database, no token overhead. Claude already knows how to read files, track state, and delegate work. Proto gives it a file convention and two specialized subagents.

If you want 36 tools and a dashboard, use [Task Master](https://github.com/eyaltoledano/claude-task-master). If you want the simplest thing that works, use this.

## What it does

**Phase 1: Planning (collaborative)**
You describe what you want to build. Claude interviews you, then creates structured project files: PRD, architecture, plan, and progress tracking. You approve each step before moving on.

**Phase 2: Implementation (autonomous)**
Claude works through the plan. For parallel or complex work, it delegates to implementer subagents in isolated git worktrees, then merges with a dedicated integrator. For simple tasks, it implements directly.

When information is missing, it asks you instead of guessing. After getting your answer, it updates the project files and continues.

## Install

```bash
git clone https://github.com/mmndaniel/proto.git
claude --plugin-dir ./proto
```

Or copy manually:

```bash
cp -r proto/skills/proto ~/.claude/skills/proto
cp proto/agents/implementer.md ~/.claude/agents/
cp proto/agents/integrator.md ~/.claude/agents/
```

## Usage

Start a new project:
```
/proto let's build a CLI bookmark tool in Python
```

Resume an existing project:
```
continue the project
```

## Project files

Proto creates these in your project root. Plain markdown. Work without Proto.

| File | Purpose |
|---|---|
| `SPEC.md` | What you're building, for whom, why |
| `ARCHITECTURE.md` | Stack, components, key decisions |
| `PLAN.md` | Tasks with IDs, descriptions, dependencies |
| `PROGRESS.md` | Current state of each task |
| `CLAUDE.md` | Agent instructions and run commands |

A fresh Claude Code session reads these files and knows where the project stands. No conversation history needed.

## Components

| Component | What it is | Lines |
|---|---|---|
| `skills/proto/SKILL.md` | Planning, delegation, failure handling | ~65 |
| `agents/implementer.md` | Implements one task in an isolated worktree. Auto-commits via hook. | ~15 |
| `agents/integrator.md` | Merges branches, resolves conflicts, runs integration tests. | ~15 |

## Evaluation

```bash
./eval/run-suite.sh           # run all fixtures
./eval/run-new-project.sh     # test full flow from scratch
python3 eval/measure-session.py <session.jsonl>
```

See `eval/README.md` for fixture descriptions.

## License

MIT
