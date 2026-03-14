# Subagent Prompt Template

Use this structure when prompting each subagent.

## Template

```
You are implementing a single task for the {{PROJECT_NAME}} project.

## Your task
{{TASK_ID}}: {{TASK_DESCRIPTION}}

## Project context
{{RELEVANT_CONTEXT_FROM_PRD_AND_ARCHITECTURE}}

## Definition of done
{{WHAT_SUCCESS_LOOKS_LIKE_FOR_THIS_TASK}}

## Constraints
- Follow existing code conventions in the repo
- No placeholder or TODO code. Complete implementations only.
- No hardcoded secrets. Use environment variables.

## Before finishing
Verify your work runs without errors and matches the task requirements.

Complete the implementation in your worktree.
```

## Guidelines

- Include only context the subagent needs. Don't dump entire files.
- Define the goal, not the approach. Let the subagent decide how to implement.
- Keep it concise. A shorter prompt means the subagent spends tokens on code, not reading.
