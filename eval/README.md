# Eval Suite

Four test fixtures, each 2 tasks, each testing one behavior:

| Fixture | Tests | Expected behavior |
|---|---|---|
| `happy-path` | Baseline: 2 independent tasks, clean merge | Skill triggers, parallel implementers, integrator merges, all checks pass |
| `missing-decision` | Architecture gap (config format undecided) | Orchestrator asks user before delegating TASK-001 |
| `merge-conflict` | 2 tasks both write to cli.py | Integrator resolves conflict, keeps both subcommands |
| `blocked-task` | Task references unreachable internal API | Implementer returns blocked, orchestrator asks user for API details |

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

**Behavioral checks**:
- Skill invoked
- Orchestrator didn't write/read source files
- All implementers ran as background agents
- Integrator was used and ran git merge
- No TaskCreate/TaskUpdate (uses progress.md)
- Progress updated incrementally
- Orchestrator asked user when information was missing
