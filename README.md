# Proto

Idea to working prototype, fast. No framework, no server, no dependencies. Just a convention the model follows.

## Philosophy

The model is the engine. You don't build machinery around it. You give it structure, goals, and good tools, then get out of the way.

Proto is 12 files: one skill, two agent definitions, and some reference docs. No MCP server. No database. No token overhead. Claude already knows how to read files, track state, and delegate work. Proto just gives it a convention to follow.

Think NanoClaw, not OpenClaw. If you want 36 tools and a dashboard, use [Task Master](https://github.com/eyaltoledano/claude-task-master). If you want the simplest thing that works, use this.

## What it does

**Phase 1: Planning (collaborative)**
You describe what you want to build. Claude interviews you, then creates structured project files: PRD, architecture, plan, and progress tracking. Each step is a conversation you approve before moving on.

**Phase 2: Implementation (autonomous)**
Claude works through the plan. For complex or parallel work, it delegates to implementer subagents running in isolated git worktrees, then merges results with a dedicated integrator. For simple tasks, it just implements directly. It decides what makes sense.

If something is missing (an architecture decision, an unclear requirement), it asks you instead of guessing. After getting your answer, it updates the project files and continues.

## Install

```bash
git clone https://github.com/mmndaniel/proto.git
claude --plugin-dir ./proto
```

Or copy the pieces manually:

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

Proto detects the project files and picks up where it left off.

## Project files

Proto creates these files in your project root. They're plain markdown. They work without Proto.

| File | Purpose |
|---|---|
| `prd.md` | What you're building, for whom, why |
| `architecture.md` | Stack, components, key decisions |
| `plan.md` | Tasks with IDs, descriptions, dependencies |
| `progress.md` | Current state of each task |
| `CLAUDE.md` | Agent instructions and run commands |

These files are the cross-session memory. When you start a fresh Claude Code session, Claude reads them and knows exactly where the project stands. No conversation history needed.

## Components

| Component | What it is | Lines |
|---|---|---|
| `skills/proto/SKILL.md` | The workflow: planning, delegation, failure handling | ~65 |
| `agents/implementer.md` | Subagent: implements one task in an isolated worktree. Auto-commits via hook. | ~15 |
| `agents/integrator.md` | Subagent: merges branches, resolves conflicts, runs integration tests. | ~15 |

That's it. The rest is reference docs the skill loads on demand.

## Evaluation

The `eval/` directory has test fixtures, a runner, and a metrics script:

```bash
./eval/run-suite.sh           # run all fixtures
./eval/run-new-project.sh     # test Phase 1 from scratch
python3 eval/measure-session.py <session.jsonl>  # measure any session
```

See `eval/README.md` for details.

## License

MIT
