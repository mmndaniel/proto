# Proto

Idea to working prototype, fast.

Proto is a Claude Code plugin that takes a rough idea and turns it into a working prototype using parallel subagents. You describe what you want to build, Proto helps you plan it, then implements everything autonomously using isolated worktrees.

## How it works

**Phase 1: Planning (collaborative)**
You and Claude work together to define the project: what you're building (PRD), how it's built (architecture), and what to do (plan). Each step is a conversation. Once you approve the plan, Proto takes over.

**Phase 2: Implementation (autonomous)**
Proto spawns parallel subagents, each implementing one task in an isolated git worktree. When they finish, a dedicated integrator subagent merges the branches, resolves conflicts, and runs integration tests. Proto updates progress and repeats until everything is done.

## Architecture

Three roles, each with a focused context window:

| Role | Runs in | Purpose |
|---|---|---|
| **Orchestrator** (skill) | Main context | Reads state, delegates tasks, updates progress. Never writes code. |
| **Implementer** (subagent) | Isolated worktree | Implements one task. Auto-commits via hook on completion. |
| **Integrator** (subagent) | Main worktree | Merges branches, resolves conflicts, runs integration tests. |

## Install

### From the marketplace (once approved)

```
/plugin install proto@claude-plugins-official
```

### From source

```bash
git clone https://github.com/mmndaniel/proto.git
claude --plugin-dir ./proto
```

### Manual install

Copy the components to your Claude Code config:

```bash
cp -r proto/skills/proto ~/.claude/skills/proto
cp proto/agents/implementer.md ~/.claude/agents/
cp proto/agents/integrator.md ~/.claude/agents/
```

## Usage

### Start a new project

```
/proto let's build a CLI bookmark tool in Python
```

Proto will walk you through the PRD, architecture, and plan, then implement everything.

### Resume an existing project

Open Claude Code in the project directory and say:

```
continue the project
```

Proto detects the existing project files and picks up where it left off.

## Project files

Proto creates these files in your project:

| File | Purpose |
|---|---|
| `prd.md` | What you're building, for whom, why |
| `architecture.md` | Stack, infrastructure, components |
| `plan.md` | Tasks with IDs, descriptions, dependencies |
| `progress.md` | Current state of each task |
| `CLAUDE.md` | Agent instructions and run commands |

## Why Proto

Proto isn't about being faster than plain Claude Code for small projects. Plain Claude Code will implement 5 simple tasks quicker than Proto can coordinate subagents to do the same.

Proto's value is the **scaffolding**: it forces you through PRD, architecture, and planning before writing code. That structure gives you:

- **Resumability**: progress.md tracks what's done. Session dies? Next session picks up where you left off.
- **Failure handling**: missing a decision in architecture.md? Proto asks instead of guessing. Bad task decomposition? It restructures the plan and re-delegates.
- **Context management**: implementation happens in disposable subagent contexts. The main conversation stays lean for long sessions.
- **Parallel execution**: independent tasks run simultaneously in isolated worktrees, with automatic merging.

For small projects (under 5 tasks), plain Claude Code is faster. Proto is for when you want the structure, the tracking, and the ability to walk away and come back.

## Evaluation

The `eval/` directory contains tooling and test fixtures:

```bash
# Run a single fixture
./eval/run-suite.sh happy-path

# Run all fixtures
./eval/run-suite.sh

# Test Phase 1 (new project from scratch)
./eval/run-new-project.sh

# Measure any session
python3 eval/measure-session.py <session-jsonl>
```

See `eval/README.md` for fixture descriptions and behavioral checks.

## License

MIT
