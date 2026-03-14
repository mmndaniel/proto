# Proto

Claude Code plugin. Skill (`/go`) + two subagents (implementer, integrator).

## Install

```bash
./install.sh
```

After install, `/go` or "let's start a project" triggers the skill.

## Files

- `skills/go/SKILL.md` - planning and implementation workflow
- `skills/go/scripts/init-project.sh` - scaffolds project files
- `skills/go/references/` - guides loaded during planning
- `agents/implementer.md` - implements tasks in isolated worktrees, auto-commits via hook
- `agents/integrator.md` - merges branches, resolves conflicts, runs integration tests
- `eval/` - test fixtures and measurement scripts (dev only)

## Developing

Edit `skills/go/SKILL.md` or `agents/*.md`, test with `claude --plugin-dir .`.

Evals: `./eval/run-suite.sh`

## Design decisions

- Claude decides subagents vs direct implementation (user can override)
- Implementers never run git commands; Stop hook auto-commits
- Integrator reads PLAN.md to resolve conflicts
- PROGRESS.md updated after each batch for cross-session resumption
- Project files are source of truth; ask the user when information is missing
