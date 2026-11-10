# bajor/skills

A portable collection of [Agent Skills](https://agentskills.io). The repository
combines maintained skills from `bajor/tools-configs`, the local agent harness
skill directories, and the MIT-licensed `backnotprop/pstack` collection.

## Install

Use the Skills CLI to choose skills and target harnesses:

```bash
npx skills add bajor/skills
```

## Layout

- `skills/<name>/SKILL.md`: an installable agent skill and its supporting files.
- `catalog.json`: source provenance and content hashes for every retained skill.
- `LICENSES/pstack-MIT.txt`: license for imported pstack material.

When two source directories have byte-identical content, the collection stores
one copy and records every source in `catalog.json`. When content differs, both
copies are retained. Later copies use a source-qualified directory name, such
as `claude-statechart`.

Catalog SHA-256 values are grouped in blocks of four hexadecimal characters for
readability and compatibility with the repository's PII scanner.

## Imported sources

- [`bajor/tools-configs`](https://github.com/bajor/tools-configs) at
  `b6f86623807c1d4e63a33f0f4d81f4a9a526ea93`
- [`backnotprop/pstack`](https://github.com/backnotprop/pstack) at
  `4161d4ef5051574e825ffe70e2f43a2e49e4b3db`, licensed under MIT
- Local managed skill directories: `$HOME/.agents/skills`, `$HOME/.claude/skills`, and
  `$HOME/.codex/skills`

Vendor caches and system-provided plugin directories are intentionally excluded.
They are not user-managed sources and may have separate distribution terms.
