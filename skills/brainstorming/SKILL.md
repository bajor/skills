---
name: brainstorming
description: "Use when the user asks to brainstorm, ideate, refine a rough idea, compare approaches, design before coding, use Superpowers-style brainstorming, or choose a plan for a medium or larger task. Also use when a feature, workflow, architecture, product, document, or research plan has unclear requirements or meaningful tradeoffs. Do not use when the user explicitly asks for immediate execution, a tiny mechanical edit, a factual answer, or a command output."
---

# Brainstorming

## Overview

Turn a vague request into an agreed design before implementation. Keep the dialogue practical: understand the goal, surface constraints, compare options, recommend one path, and stop once the user has approved the next concrete step.

## Workflow

1. Check the local context that already exists: user instructions, repository files, current branch, docs, issue text, prior notes, or relevant examples.
2. Restate the goal in one or two sentences, including known constraints and unknowns.
3. If the request is too large for one deliverable, split it into smaller deliverables before discussing details.
4. Ask one clarifying question at a time. Prefer multiple-choice questions when the decision space is clear.
5. Propose two or three approaches with tradeoffs. Lead with the recommended approach and explain the reason.
6. Present the design or plan in sections sized to the task. For each section, state the concrete behavior, files or components involved, validation method, and out-of-scope items.
7. Ask for approval before implementation. Do not write code, scaffold files, or make durable repo changes until the user approves the design, unless the user explicitly asked for immediate execution.

## Question Discipline

Ask only questions that change the design or reduce implementation risk. Avoid generic discovery questions when local context already answers them.

Each question should include:

- the decision being made
- the available options, when known
- the effect of each option
- the default recommendation, when there is a clear one

## Design Output

For small tasks, the approved design can be a short message.

For medium or larger tasks, produce a written design before implementation when the user wants a durable artifact or the repository's instructions require planning. Use the repository's existing planning location if one exists. If there is no local convention, use `docs/brainstorming/YYYY-MM-DD-<topic>-design.md`.

Do not commit, push, open a pull request, or create extra planning files unless the user requested that workflow or local repository instructions require it.

## Quality Bar

Before asking for approval, verify that the design states:

- scope and non-scope
- assumptions and constraints
- selected approach and rejected alternatives
- data flow or control flow, if applicable
- user-visible behavior, if applicable
- error cases and edge cases
- validation steps
- acceptance criteria

If any item is missing because it does not apply, say that it does not apply.

## Completion

The brainstorming pass is complete only when one of these is true:

- the user approves a specific design and next step
- the user asks to stop brainstorming and execute a different instruction
- a blocker is identified that cannot be resolved without user input
