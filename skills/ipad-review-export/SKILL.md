---
name: ipad-review-export
description: Use when the user wants a change summary, plan, review, or architecture write-up delivered as a clean printable PDF to read and annotate with an Apple Pencil on an iPad. Triggers include "send this to my iPad", "make a review PDF", "export the plan for markup", "PDF I can write on", or any request to hand work off for tablet reading. Pairs with ipad-review-import, which reads the annotated PDF back.
---

# ipad-review-export

Turn the current work product (a diff, a plan, an architecture section) into a
typeset A4 PDF, then place it in the iCloud Drive folder that the iPad's Files
app shows. The user annotates it in place with the Pencil; the companion skill
`ipad-review-import` reads those annotations back and applies them.

Scope: macOS with Google Chrome (or any Chromium) installed and iCloud Drive
enabled. Output is one PDF per run. No network access is needed beyond iCloud's
own sync.

## Constants

```bash
INBOX="$HOME/Library/Mobile Documents/com~apple~CloudDocs/iPad Review"
ARCHIVE="$HOME/.cache/ipad-review/sent"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
# If Chrome is missing, use any Chromium binary: /Applications/Chromium.app/...
# or `command -v chromium chrome google-chrome` on PATH.
SCRATCH="$(mktemp -d)"                 # all temporary files go here
NAME="$(date +%Y-%m-%d-%H%M)-<slug>"   # <slug>: short kebab-case topic
```

## Workflow

1. **Gather content.** Actor: agent. Collect what the user wants reviewed:
   `git diff`/`git log` for changes, the plan file for plans, the named
   documents for architecture. Expected result: you can state in one sentence
   what decision set the reader is reviewing. Failure: the request names no
   reviewable artifact; ask which one.

2. **Write the document as HTML.** Actor: agent, Write tool. Copy
   `assets/template.html` (relative to this skill) to `$SCRATCH/review.html`
   and replace everything inside `<main>` except the header and the trailing
   legend. Keep the CSS untouched. The document is a review instrument, not a
   dump. Its shape:
   - Title names the decision set, not the branch name.
   - Meta line: date, repository and branch, short commit SHA, author.
   - "Summary" section: at most six sentences on what changed and why it
     matters.
   - Body: the decisions as numbered items with a bold lead sentence each,
     code excerpts only where a decision lives in the code, tables only for
     enumerable comparisons. Target 2 to 6 pages.
   - Final section "Questions for you": numbered, each one a single decidable
     question followed by the template's ruled answer space.
   Expected result: valid HTML file. Failure: none expected.

3. **Print to PDF with headless Chrome.** Actor: agent, Bash:

   ```bash
   "$CHROME" --headless --disable-gpu --no-first-run \
     --no-default-browser-check --user-data-dir="$SCRATCH/chrome-profile" \
     --no-pdf-header-footer --print-to-pdf="$SCRATCH/$NAME.pdf" \
     "file://$SCRATCH/review.html"
   ```

   `--user-data-dir` must point at a throwaway directory or Chrome refuses to
   start while the user's Chrome is open. Expected result: Chrome logs "bytes
   written".
   Failure: "Failed to create socket directory" or "Operation not permitted"
   means an OS sandbox is blocking Chrome's sockets; rerun this one command
   outside the sandbox through the harness permission gate.

4. **Check the layout on every page.** Actor: agent. If the harness reads
   PDFs natively, read `$SCRATCH/$NAME.pdf` itself, all pages. Otherwise:

   ```bash
   qlmanage -t -s 1400 -o "$SCRATCH" "$SCRATCH/$NAME.pdf"   # page 1 only
   ```

   then, when the `ipad-review-import` venv exists at
   `$HOME/.cache/ipad-review/venv`, render the remaining pages with that
   skill's `scripts/pdf_pages.py render` and read them too. Expected result:
   on every checked page, no clipped text, no orphan heading at a page bottom,
   code blocks intact. A page nothing could render goes unchecked; name it in
   the final message. Failure: fix the HTML and repeat steps 3 and 4 once.

5. **Archive the clean copy.** Actor: agent, Bash:
   `mkdir -p "$ARCHIVE" && cp "$SCRATCH/$NAME.pdf" "$ARCHIVE/"`.
   `ipad-review-import` diffs the annotated file against this copy to find the
   marked pages. Failure: none expected.

6. **Export to the iPad.** Actor: agent, Bash. Gate first:
   `[ -d "$HOME/Library/Mobile Documents/com~apple~CloudDocs" ]`; when that
   directory is missing, iCloud Drive is off on this Mac, stop and tell the
   user (a `mkdir -p` before this check would fabricate a local, non-syncing
   folder and mask the failure). Only then
   `mkdir -p "$INBOX" && cp "$SCRATCH/$NAME.pdf" "$INBOX/"`.
   iCloud uploads the file by itself; `ls -la "$INBOX"` confirming the copy is
   the only check needed. Do not run `brctl status`; it streams and hangs a
   non-interactive shell. Failure: "Operation not permitted" means an OS
   sandbox blocks writes under `~/Library/Mobile Documents`; rerun this one
   command outside the sandbox through the harness permission gate.

7. **Tell the user where it is.** Final message states: the file name, that it
   appears on the iPad under Files > iCloud Drive > iPad Review, and how to
   annotate so the round trip works: open the PDF, tap the Markup pencil, write
   directly on the page, tap Done. Markup saves into the same file and iCloud
   syncs it back; no export step is needed on the iPad.

## Annotation contract

The legend at the bottom of `assets/template.html` is the single authoritative
statement of the mark contract. Keep it in every export, unchanged:
`ipad-review-import` reads the contract off the document's own last page.

## Acceptance criteria

- A PDF of at most 6 pages exists in `$INBOX` and in `$ARCHIVE` with the same
  name.
- The layout check of step 4 ran; pages it could not render are named in the
  final message.
- The final message names the file and the iPad annotation steps.
