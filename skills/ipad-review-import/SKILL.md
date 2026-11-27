---
name: ipad-review-import
description: Use when the user has annotated a review PDF on their iPad with an Apple Pencil and wants those handwritten corrections read and acted on. Triggers include "get my notes from the iPad", "apply the PDF corrections", "import the marked-up PDF", "I reviewed it on the iPad", or any request to pick up tablet annotations. Counterpart of ipad-review-export, which sent the PDF.
---

# ipad-review-import

Fetch the Pencil-annotated PDF from the iCloud Drive handoff folder, read the
handwriting from page images, turn every mark into an explicit instruction,
then carry those instructions out. The agent's own vision does the handwriting
reading; the bundled script only locates and rasterizes the marks.

Scope: macOS with iCloud Drive enabled and `python3` available. First run
creates a virtualenv and downloads PyMuPDF from PyPI, which needs network
access once.

## Constants

```bash
INBOX="$HOME/Library/Mobile Documents/com~apple~CloudDocs/iPad Review"
ARCHIVE="$HOME/.cache/ipad-review/sent"     # clean copies ipad-review-export kept
VENV="$HOME/.cache/ipad-review/venv"
PY="$VENV/bin/python"
SKILL_DIR="<the directory holding this SKILL.md>"   # bundled script lives here
SCRATCH="$(mktemp -d)"                              # all temporary files go here
```

## Workflow

1. **Import the PDF from the iPad.** Actor: agent, Bash. List candidates with
   `ls -t "$INBOX"/*.pdf`; take the file the user named, otherwise the newest.
   Markup annotates in place, so the newest PDF is normally the very file the
   export delivered, under its original name.
   Copy it into `$SCRATCH`; the copy forces iCloud to materialize the
   latest synced bytes. If the copy stalls or reads zero bytes, run
   `brctl download "$INBOX/<file>"`, wait a few seconds, and copy again.
   Expected result: a local PDF larger than zero bytes. Failure: no PDFs in
   `$INBOX`, tell the user nothing has arrived from the iPad yet and stop.

2. **Bootstrap the renderer once.** Actor: agent, Bash. Only if `$PY` is
   missing:

   ```bash
   python3 -m venv "$VENV" && "$VENV/bin/pip" -q install pymupdf
   ```

   Failure: pip cannot reach PyPI; name the missing network access and stop.

3. **Locate the marks.** Actor: agent, Bash, script bundled with this skill:

   ```bash
   "$PY" "$SKILL_DIR/scripts/pdf_pages.py" info "$SCRATCH/<file>.pdf"
   "$PY" "$SKILL_DIR/scripts/pdf_pages.py" diff "$ARCHIVE/<file>.pdf" "$SCRATCH/<file>.pdf"
   ```

   `info` prints page count and per-page annotation objects (Apple Markup
   stores Pencil strokes as ink annotations). `diff` pixel-compares against the
   clean archived copy. The matching archive file is the one with the annotated
   file's exact name; failing that, the archived name that is the longest
   prefix of it (iCloud appends suffixes like " 2" to conflict copies). Skip
   the diff when neither exists. Expected result: a set of marked pages.
   Failure: the script exits nonzero; read its stderr, it names the cause.

4. **Rasterize and read.** Actor: agent, Bash then image reading:

   ```bash
   "$PY" "$SKILL_DIR/scripts/pdf_pages.py" render "$SCRATCH/<file>.pdf" "$SCRATCH/pages" --dpi 150
   ```

   Read every rendered page image when the document has 12 pages or fewer;
   otherwise read the marked pages from step 3 plus the first page. Some iPad
   apps flatten ink into the page image, so an empty annotation list never
   proves an unmarked document; the diff and your own eyes decide. For a mark
   too small to read, re-render that page alone with `--dpi 300` and read it
   again.

5. **Transcribe into findings.** Actor: agent. Produce a numbered list, one
   entry per visible mark; a single annotation object may hold several separate
   strokes, split them. Each entry: page number, the printed text the mark
   anchors to (quoted), the handwriting transcribed verbatim, and the
   interpretation under this contract (the same legend printed on the PDF's
   last page):
   - Cross-out or ✗ over an item: reject or delete it.
   - ✓ next to an item: approved as is.
   - Underline or circle plus a margin note: change it as the note says.
   - ? in the margin: explain, do not change.
   - Writing inside a question's ruled space: the decision for that question.
   A bare underline, circle, or squiggle with no words near it is emphasis:
   record it in the report, change nothing, and raise no question about it
   unless it strikes text through. Transcribe uncertain words with best effort
   and mark them `[unclear]`. Never invent a correction you cannot see.

6. **Act on the findings.** Actor: agent. Treat each actionable finding as an
   instruction from the user and carry it out in the relevant repository, plan,
   or document now, in finding order. A `?` finding produces an explanation in
   the final message, not an edit. A finding that is `[unclear]` or contradicts
   another becomes a question to the user instead of a guess.

7. **Archive the processed PDF.** Actor: agent, Bash:
   `mkdir -p "$INBOX/processed" && mv "$INBOX/<file>.pdf" "$INBOX/processed/"`.
   This keeps the inbox to unprocessed documents only. Do not delete anything.
   Failure: "Operation not permitted" means an OS sandbox blocks writes under
   `~/Library/Mobile Documents`; rerun this one command outside the sandbox
   through the harness permission gate.

8. **Report.** The final message leads with what was changed, then the full
   findings list with each finding's disposition: applied, explained, or
   question for the user.

## Acceptance criteria

- Every rendered marked page was actually read; no finding was fabricated.
- Each finding has page, anchor quote, verbatim transcription, interpretation,
  and disposition.
- Actionable findings are applied; unclear ones are questions, not guesses.
- The processed PDF sits in `$INBOX/processed/`, not deleted.
