---
name: ipad-review-export
description: Use when the user wants a change summary, plan, review, or architecture write-up delivered as a clean printable PDF to read and annotate with an Apple Pencil on an iPad. Triggers include "send this to my iPad", "make a review PDF", "export the plan for markup", "PDF I can write on", or any request to hand work off for tablet reading. Concepts with structure are drawn as inline SVG figures. Two registers: a 2 to 6 page change summary, and a deep dive that records each decision's constraints, trade-offs and cap headroom at the length that needs. Pairs with ipad-review-import, which reads the annotated PDF back.
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
     enumerable comparisons.
   - Depth: each decision records, in prose and in this order, (a) the
     constraint that forces it: a platform rule, a measured number or an
     owner requirement, named with its figure; (b) the trade-off: what the
     choice gives up, and the strongest rejected alternative with the
     reason it lost; (c) where a cap or budget exists: the cap, the measured
     value against it, the remaining headroom, and the behavior when the cap
     is hit. An item with none of these is context, not a decision; fold it
     into the summary or drop it.
   - Register and length: there is no page cap. A change summary stays as
     brief as its decisions allow; when the user asks for depth (a deep
     dive, "not deep enough", an architecture study), take every page the
     constraints and trade-offs need. Depth never comes from restating at
     more length; it comes from constraints, rejected alternatives, numbers
     and their consequences.
   - Diagrams: every concept with structure (a flow, a topology, a lifecycle,
     a layering) is drawn as an inline SVG figure under the Diagrams rules
     below. No ASCII-art diagram ships in the PDF. In a deep dive, a cap
     with measured pressure against it deserves a budget-bar figure showing
     used against remaining.
   - No closing questions section. A decision that waits on the reader is a
     body item where it belongs, opening with a bold "Open, yours:" lead;
     the reader answers it in the margin per the mark legend.
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
   code blocks intact, and every SVG figure whole: no label clipped at the
   viewBox edge, arrowheads present, the caption on the same page as its
   figure. A page nothing could render goes unchecked; name it in
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

## Diagrams

A concept with structure gets a drawn figure: data flows, process topologies,
trust boundaries, lifecycles, gate layers. Draw it as inline SVG; vector lines
stay crisp at any Pencil zoom, and the Markup ink lands on top cleanly. A
diagram must still earn its place: when two plain sentences say it, keep the
sentences.

- Inline `<svg>` inside `<figure class="diagram">`, followed by a
  `<figcaption>` that names what the reader should see. The template styles
  both; `assets/template.html` carries a minimal example figure.
- Give each `<svg>` a `viewBox` about 700 units wide and `width="100%"`.
  At that scale a 12-unit label prints near 8 pt, the floor for legibility;
  never draw text smaller. Keep every element inside the viewBox: Chrome
  clips at its edge without warning.
- Use only the template's SVG classes (`box`, `wash`, `edge`, `dashed`,
  `boxlabel`, `edgelabel`) so figures inherit the document's inks. Add no
  colors of your own, and never let color alone carry meaning: the page may
  be printed or read in grayscale.
- Arrowheads come from a `<marker>` defined in the figure's own `<defs>`,
  with an id unique across the whole document (`arrow-f1`, `arrow-f2`, ...).
  Duplicate marker ids across inline SVGs all resolve to the first one and
  corrupt later figures.
- When line styles differ in meaning (solid IPC against dashed consent-gated
  transfer, say), add a small legend row inside the SVG, in `edgelabel` text.
- Budget: a figure is at most half a page tall; the template's
  `break-inside: avoid-page` keeps it on one page, so an over-tall figure
  pushes a page break and wastes paper. Split an over-tall diagram into two
  figures instead.

## Annotation contract

The legend at the bottom of `assets/template.html` is the single authoritative
statement of the mark contract. Keep it in every export, unchanged:
`ipad-review-import` reads the contract off the document's own last page.

## Acceptance criteria

- A PDF exists in `$INBOX` and in `$ARCHIVE` with the same name, at the
  length its register needs: brief for a change summary, exhaustive for a
  requested deep dive, padded in neither.
- Every numbered decision names its forcing constraint and its trade-off,
  and every cap it touches appears with the measured value, the headroom and
  the at-cap behavior.
- Decisions that wait on the reader are marked "Open, yours:" in place; the
  document ends with the body, not a questions section.
- Every concept with structure is an inline SVG figure following the Diagrams
  rules; no ASCII-art diagram appears in the PDF.
- The layout check of step 4 ran, including the SVG checks; pages it could
  not render are named in the final message.
- The final message names the file and the iPad annotation steps.
