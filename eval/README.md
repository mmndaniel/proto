# Eval Suite

Five fixtures, each with 2 tasks, each testing one behavior:

| Fixture | Tests | Expected behavior |
|---|---|---|
| `happy-path` | 2 independent tasks, clean merge | Parallel implementers, integrator merges, all checks pass |
| `missing-decision` | Architecture gap (config format undecided) | Orchestrator asks user before delegating |
| `merge-conflict` | 2 tasks both write to cli.py | Integrator resolves conflict, keeps both subcommands |
| `integration-fail` | Tasks that break when combined | Integrator reports failure, orchestrator creates fix task |
| `blocked-task` | Task references unreachable API | Implementer returns blocked, orchestrator asks user |

## Running a test

```bash
# Set up test project from fixture
./setup-test.sh happy-path

# Open Claude Code in the test project
cd /tmp/happy-path && claude

# Say: continue the project

# After completion, measure the session
python3 measure-session.py ~/.claude/projects/-tmp-happy-path/<session-id>.jsonl
```

## What the eval checks

**Metrics**: active time, token usage, turns, agent spawns.

**Behavioral checks**: skill invoked, orchestrator stayed out of source files, implementers ran as background agents, integrator merged branches, progress updated incrementally, orchestrator asked user when information was missing.
