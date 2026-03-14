# Subagent Prompt Template

Structure for prompting each subagent.

## Template

```
Implementing a single task for {{PROJECT_NAME}}.

## Task
{{TASK_ID}}: {{TASK_DESCRIPTION}}

## Context
{{RELEVANT_CONTEXT_FROM_SPEC_AND_ARCHITECTURE}}

## Done when
{{WHAT_SUCCESS_LOOKS_LIKE}}

## Constraints
- Follow existing code conventions
- No placeholder or TODO code
- No hardcoded secrets; use environment variables

Verify your work runs without errors. Complete the implementation in your worktree.
```

## Guidelines

- Include only what the subagent needs. Don't dump entire files.
- Define the goal, not the approach.
- Shorter prompts mean more tokens spent on code.
