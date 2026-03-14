# Proto

This repo is a Claude Code plugin. It has a skill (`/go`) and two subagent definitions.

## Install for a user

Copy three things:
```bash
cp -r skills/go ~/.claude/skills/go
cp agents/implementer.md ~/.claude/agents/
cp agents/integrator.md ~/.claude/agents/
```

After install, the user can invoke `/go` or say "let's start a project" and it triggers automatically.

## What's in the box

- `skills/go/SKILL.md` - planning and implementation workflow
- `skills/go/scripts/init-project.sh` - scaffolds project files (SPEC.md, PLAN.md, etc.)
- `skills/go/references/` - guides loaded on demand during planning
- `agents/implementer.md` - implements tasks in isolated git worktrees, auto-commits via hook
- `agents/integrator.md` - merges worktree branches, resolves conflicts, runs integration tests
- `eval/` - test fixtures and measurement scripts (not installed, dev tooling only)

## Developing

Edit `skills/go/SKILL.md` or `agents/*.md`, then test with `claude --plugin-dir .` from this directory.

To run evals: `./eval/run-suite.sh`

Key design decisions:
- Phase 2 is flexible: Claude decides when to use subagents vs direct implementation
- Implementers never run git commands; the Stop hook commits automatically
- Integrator reads PLAN.md to understand task intent when resolving conflicts
- PROGRESS.md is updated after each batch (enables cross-session resumption)
- Project files are the source of truth; when information is missing, ask the user
