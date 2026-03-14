# Proto

Idea to working prototype, fast. Iterate without losing context. Subagents build in parallel while you steer.

## Who this is for

Product builders who use AI coding agents to implement. You steer at the product level: what to build, why, whether the result is right. You don't review every patch.

## The problem

Every iteration pollutes your context. You try approach A, it doesn't work, you switch to approach B. Approach A's code is still in context. After enough iterations, Claude gets confused by stale code and abandoned approaches. You compact or start fresh, then re-explain everything.

## How Proto solves it

Proto captures decisions in project files outside the conversation. When context gets noisy, start fresh. Claude reads the files and picks up where you left off.

**Phase 1: Planning.** You describe what you want. Claude creates project files: SPEC.md (what and why), ARCHITECTURE.md (technical decisions), PLAN.md (tasks with dependencies), PROGRESS.md (status). You approve each step.

**Phase 2: Implementation.** Claude works through the plan, delegating tasks to subagents in isolated git worktrees. Implementation stays out of your conversation. Your main context stays clean for steering. When a task needs information not in the project files, Claude asks instead of guessing.

Claude decides when subagents make sense and when to implement directly. You can override either way.

## Install

```bash
git clone https://github.com/mmndaniel/proto.git
cd proto && ./install.sh
```

## Quick start

```bash
mkdir my-project && cd my-project
claude
```

Then:
```
/go I want to build a habit tracker CLI. Track daily habits, mark them done, see streaks. Python, SQLite.
```

Claude walks you through planning (SPEC, architecture, task breakdown), then implements using parallel subagents. Your main context stays clean.

To resume in a new session, open Claude Code in the same directory and say:
```
continue the project
```

## Install options

`./install.sh` installs everything. For more control:

**Skill only** (planning + progress tracking, no subagents):
```bash
cp -r skills/go ~/.claude/skills/go
```

**Full** (skill + subagents):
```bash
cp -r skills/go ~/.claude/skills/go
cp agents/*.md ~/.claude/agents/
```

**Plugin mode** (for `--plugin-dir` or marketplace):
```bash
claude --plugin-dir ./proto
```
Command becomes `/proto:go`. Don't combine with standalone install.

## Project files

Plain markdown. Any Claude Code session can read them and continue without Proto installed.

| File | Purpose |
|---|---|
| `SPEC.md` | What you're building, for whom, why |
| `ARCHITECTURE.md` | Stack, components, key decisions |
| `PLAN.md` | Tasks with IDs, descriptions, dependencies |
| `PROGRESS.md` | Current state of each task |
| `CLAUDE.md` | How to work on this project |

## Philosophy

Claude already knows how to read files, track state, delegate work, and write code. Proto gives it a file convention and two subagents. No MCP server, no database, no token overhead. 12 files.

If you want 36 tools and a task management server, use [Task Master](https://github.com/eyaltoledano/claude-task-master). Proto is the minimal alternative: a convention, not a framework.

## How it works

| Component | What it does | Lines |
|---|---|---|
| `skills/go/SKILL.md` | Planning workflow, failure handling, file conventions | ~45 |
| `agents/implementer.md` | One task in an isolated worktree, auto-commits on finish | ~15 |
| `agents/integrator.md` | Merges worktree branches, resolves conflicts, runs checks | ~15 |

The implementer runs with `permissionMode: acceptEdits` and `isolation: worktree`. It writes files without prompts, isolated from main until merged.

The integrator reads PLAN.md to understand task intent when resolving conflicts. If a conflict is ambiguous, it reports back instead of guessing.

## Demo

See subagents in action without going through planning:

```bash
./eval/setup-test.sh happy-path
cd /tmp/happy-path && claude
```

Then say `continue the project`. Claude reads the plan, spawns parallel implementers, merges their work, and updates progress.

## Evaluation

```bash
./eval/run-suite.sh           # run all test fixtures
./eval/run-new-project.sh     # test full Phase 1 + 2 flow
python3 eval/measure-session.py <session.jsonl>
```

Five fixtures: happy path, missing decisions, merge conflicts, integration failures, blocked tasks. Checks behavioral correctness and token/timing metrics. See `eval/README.md`.

## License

MIT
