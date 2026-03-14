# Proto

Project structure for AI-assisted development. Describe what you want, delegate implementation, come back anytime and pick up where you left off.

## Who this is for

Product builders who use AI coding agents as their primary implementation tool. You work at the product level: what to build, why, whether the result is right. You don't review every patch. You want to describe, delegate, steer, and iterate.

## The problem

Every iteration pollutes your context. You try approach A, it doesn't work, you redirect to approach B. Now approach A's code is still in context. After enough iterations, Claude gets confused by stale code and abandoned approaches. You compact or start fresh, but then you have to re-explain everything.

## How Proto solves it

Proto creates project files that capture your decisions outside the conversation. When a session ends or context gets noisy, you start fresh. Claude reads the files and knows exactly where things stand.

**Phase 1: Planning.** You describe what you want to build. Claude interviews you and creates structured project files: SPEC.md (what and why), ARCHITECTURE.md (technical decisions), PLAN.md (tasks with dependencies), PROGRESS.md (what's done). You approve each step.

**Phase 2: Implementation.** Claude works through the plan. It can delegate tasks to subagents that run in isolated git worktrees, keeping implementation details out of your conversation. Your main context stays clean for steering: changing direction, asking questions, evaluating results. When a task needs information that isn't in the project files, Claude asks you instead of guessing.

Phase 2 is flexible. Claude decides when subagents make sense and when to implement directly. You can override either way.

## Install

**Standalone** (recommended for personal use):
```bash
git clone https://github.com/mmndaniel/proto.git
cp -r proto/skills/go ~/.claude/skills/go
cp proto/agents/*.md ~/.claude/agents/
```
Command: `/go`

**Plugin** (for `--plugin-dir` or marketplace):
```bash
git clone https://github.com/mmndaniel/proto.git
claude --plugin-dir ./proto
```
Command: `/proto:go`

Or just open Claude Code in this repo and say "install this for me." Claude reads CLAUDE.md and knows what to do.

Pick one method, not both. Having the skill installed standalone AND loaded as a plugin causes duplicate loading.

## Usage

Start a new project:
```
/go I want to build a URL shortener CLI. Takes a long URL, generates a short code, stores in SQLite. Python, stdlib only.
```

Or just say "let's start a project" and describe your idea. Claude picks up the skill automatically.

Claude creates the project files (SPEC.md, ARCHITECTURE.md, PLAN.md, PROGRESS.md), asking for your approval at each step. Once you approve the plan, it implements.

Resume an existing project (new session, same directory):
```
continue the project
```

Claude reads the project files, sees what's done in PROGRESS.md, and picks up where it left off.

## Project files

Plain markdown. Work without Proto. Any Claude Code session can read them and continue.

| File | Purpose |
|---|---|
| `SPEC.md` | What you're building, for whom, why |
| `ARCHITECTURE.md` | Stack, components, key decisions |
| `PLAN.md` | Tasks with IDs, descriptions, dependencies |
| `PROGRESS.md` | Current state of each task |
| `CLAUDE.md` | How to work on this project |

## Philosophy

The model is the engine. Claude already knows how to read files, track state, delegate work, and write code. Proto gives it a file convention and two specialized subagents. No MCP server, no database, no token overhead. 12 files total.

If you want 36 tools and a task management server, use [Task Master](https://github.com/eyaltoledano/claude-task-master). Proto is the minimal version: a convention the model follows, not a framework built around it.

## How it works

| Component | What it does | Lines |
|---|---|---|
| `skills/go/SKILL.md` | Planning workflow, failure handling, project file convention | ~45 |
| `agents/implementer.md` | Implements one task in an isolated git worktree. A Stop hook auto-commits when the subagent finishes. | ~15 |
| `agents/integrator.md` | Merges worktree branches into main, resolves conflicts, runs integration checks. | ~15 |

The implementer runs with `permissionMode: acceptEdits` and `isolation: worktree`, so it can write files without permission prompts and its work is isolated from the main repo until merged.

The integrator reads PLAN.md to understand task intent when resolving merge conflicts. If a conflict is ambiguous, it reports back instead of guessing.

## Evaluation

```bash
./eval/run-suite.sh           # run all test fixtures
./eval/run-new-project.sh     # test full Phase 1 + 2 flow
python3 eval/measure-session.py <session.jsonl>
```

Five test fixtures covering: happy path, missing architecture decisions, merge conflicts, integration failures, and blocked tasks. The eval script checks behavioral correctness alongside token and timing metrics.

See `eval/README.md` for details.

## License

MIT
