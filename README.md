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

## When to use Proto vs plain Claude Code

Proto adds coordination overhead (spawning subagents, merging branches). For small projects that fit in one context window, plain Claude Code is faster. Proto's value is architectural:

- **Context ceiling**: plain Claude Code puts all code in one context window. At 10+ tasks with complex code, that window fills up and quality degrades. Proto's orchestrator stays lean regardless of project size.
- **Resumability**: Proto tracks state in progress.md. If the session dies mid-project, the next session picks up where it left off. Plain Claude Code has no tracking.
- **Failure handling**: Proto asks the user when information is missing instead of guessing. It updates project files before re-delegating so subagents get correct context.

**Benchmark: 5-task bookmark CLI**

| Metric | Plain Claude Code | Proto |
|---|---|---|
| Active time | 50s | 2m 16s |
| Main agent turns | 22 | 38 |
| Main agent output | 3.5K tokens | 5.0K tokens |
| Main agent context | 392K | 876K |
| Code in main context | all of it | none |
| Resumable | no | yes |
| Failure escalation | no | yes |

Plain Claude Code is 2.7x faster for 5 small tasks. It writes all code directly in one pass. This works until the project outgrows one context window.

Proto's orchestrator wrote zero lines of code. Implementation happened in disposable subagent contexts that don't bloat the main conversation. The orchestrator's output (5.0K) stays roughly constant whether you have 5 tasks or 50.

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
