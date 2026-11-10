---
name: zadania-mira-a4-current-task
description: Display-only skill for the current printable A4 task prompt for Mira. Use when the user asks for today's/current worksheet prompt, task graphic prompt, or what to print for Mira; the workflow reads the Linux system date, uses birth date 2024-02-12, selects the matching quarterly directory, and prints a copy-ready AI graphics prompt plus a short parent guide without creating or modifying files.
---

# Zadania Mira A4 Current Task

Use this skill when the user wants the current printable A4 task prompt for Mira.

## Rules

- Mira's birth date is `2024-02-12`.
- The current date must come from Linux `date +%F` inside the script.
- Use quarterly directories, not monthly directories.
- Return the script output directly in chat unless the user asks for a summary.
- The output must contain a copy-ready prompt for an AI graphics/worksheet tool and a short parent guide.

## Read-only / output-only constraint

- Do not create, edit, move, copy, delete, or rename files.
- Do not save the generated prompt anywhere.
- Do not redirect output to a file.
- Do not use `tee`, `>`, or `>>`.
- The only shell command this skill should run is the absolute script command below, optionally with `--list` or one prompt filename argument.
- The script is expected to read existing markdown files and print to stdout only.

## Command

Run this absolute command:

```bash
/home/ubuntu/obsidian/implementation_plans/zadania-mira/_skills/a4_current_task/scripts/current_prompt.sh
```

List available prompts for the current quarter:

```bash
/home/ubuntu/obsidian/implementation_plans/zadania-mira/_skills/a4_current_task/scripts/current_prompt.sh --list
```

Use a specific prompt file from the selected quarter:

```bash
/home/ubuntu/obsidian/implementation_plans/zadania-mira/_skills/a4_current_task/scripts/current_prompt.sh 02_ilosc_i_przestrzen_a4.md
```
