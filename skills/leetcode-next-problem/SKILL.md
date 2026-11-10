---
name: leetcode-next-problem
description: Inspect the hardcoded public LeetCode profile for maciekbajor, select one suitable unsolved text-only LeetCode problem, create a Python starter file in the current directory, and return exactly one direct problem URL and no other text.
---

# LeetCode Next Problem

Use the public internet to inspect the configured LeetCode profile, select one next training problem, and create a Python starter file in the current directory.

## Output contract

The complete response must be one raw URL and nothing else:

```text
https://leetcode.com/problems/<title-slug>/
```

Do not include a title, explanation, Markdown, difficulty, hints, created filename, or punctuation.

Before responding, create a Python file in the current working directory named:

```text
<title-slug>.py
```

The Python file must contain, in this order:

1. The problem URL at the very top, commented out with `# `.
2. The LeetCode problem description converted to plain text, with every line commented out with `# `.
3. One blank line.
4. The Python or Python3 starter code exactly as LeetCode provides it for the selected problem.

Do not solve the problem in the generated file. Do not add hints, explanations, imports, tests, or helper code unless LeetCode's starter code already includes them.

## Fixed profile

This skill is personal. Always use this profile; do not ask which account to inspect.

```python
PROFILE_URL = "https://leetcode.com/u/maciekbajor/"
USERNAME = "maciekbajor"
PREFERRED_LANGUAGE = "Python3"
```

`PREFERRED_LANGUAGE` is only a preference for the LeetCode editor. Do not add a made-up language parameter to the problem URL. A normal LeetCode problem URL should open using the language remembered by the user's browser/account.

## Editable training scope

Change only this block to extend, shrink, or reorder the curriculum.

```python
# Each group contains current LeetCode topic-tag slugs.
# Add/remove groups or tag slugs here. Selection code uses their union.
TOPIC_GROUPS = {
    "arrays_strings": {
        "array",
        "string",
    },
    "two_pointers": {
        "two-pointers",
    },
    "sliding_window": {
        "sliding-window",
    },
    "prefix_sum": {
        "prefix-sum",
    },
    "hashing_sets_dictionaries": {
        "hash-table",
    },
    "anagrams_frequency_maps_counting": {
        "string",
        "hash-table",
        "counting",
    },
}

ALLOWED_TOPIC_SLUGS = set().union(*TOPIC_GROUPS.values())

# Prefer easier problems first. Reorder or extend freely.
DIFFICULTY_ORDER = ["Easy", "Medium"]
EXCLUDE_PREMIUM = True

# Public LeetCode recent accepted submissions are unauthenticated and limited.
PUBLIC_RECENT_ACCEPTED_LIMIT = 20

# Only choose problems whose statement is text-only. Reject problems that depend
# on images, diagrams, tables-as-layout, animations, or other visual media.
REJECT_DESCRIPTION_HTML_PATTERNS = {
    "<img",
    "<svg",
    "<picture",
    "<figure",
    "<video",
    "<iframe",
    "<canvas",
    "<table",
}

# First valid problem wins. Reorder, add, or remove slugs freely.
# Dynamic tag-based selection is used after this list is exhausted.
PRIORITY_PROBLEM_SLUGS = [
    "contains-duplicate",
    "valid-anagram",
    "two-sum",
    "ransom-note",
    "isomorphic-strings",
    "word-pattern",
    "intersection-of-two-arrays",
    "intersection-of-two-arrays-ii",
    "unique-number-of-occurrences",
    "majority-element",
    "first-unique-character-in-a-string",
    "find-common-characters",
    "group-anagrams",
    "top-k-frequent-elements",
    "product-of-array-except-self",
    "longest-consecutive-sequence",
    "valid-palindrome",
    "merge-sorted-array",
    "remove-duplicates-from-sorted-array",
    "move-zeroes",
    "two-sum-ii-input-array-is-sorted",
    "3sum",
    "container-with-most-water",
    "best-time-to-buy-and-sell-stock",
    "maximum-average-subarray-i",
    "longest-substring-without-repeating-characters",
    "minimum-size-subarray-sum",
    "permutation-in-string",
    "find-all-anagrams-in-a-string",
    "longest-repeating-character-replacement",
    "find-pivot-index",
    "range-sum-query-immutable",
    "subarray-sum-equals-k",
    "contiguous-array",
]

# Reject problems whose main technique is clearly outside this curriculum.
BLOCKED_MAJOR_TOPIC_SLUGS = {
    "backtracking",
    "binary-tree",
    "database",
    "depth-first-search",
    "design",
    "dynamic-programming",
    "graph",
    "heap-priority-queue",
    "linked-list",
    "monotonic-queue",
    "monotonic-stack",
    "queue",
    "segment-tree",
    "shortest-path",
    "stack",
    "topological-sort",
    "tree",
    "trie",
    "union-find",
}
```

## No-authentication rule

- Use only public internet pages and unauthenticated public LeetCode data.
- Never request or use `LEETCODE_SESSION`, CSRF values, cookies, API keys, passwords, or any other token.
- Never ask the user to log in or copy credentials.
- The browser may already be logged in, but the skill must not depend on that state.

## Workflow

1. Open `PROFILE_URL` on every run. Verify that the displayed username is `USERNAME`.
2. Read the current public profile before selecting anything, including:
   - total problems solved;
   - language counts;
   - visible skill/topic counts;
   - publicly visible recent accepted activity.
3. Build a public solved-slug set from LeetCode's unauthenticated `recentAcSubmissionList` for `USERNAME`, requesting up to `PUBLIC_RECENT_ACCEPTED_LIMIT`, and from any additional solved problem slugs visibly exposed by the public profile.
4. Do not use a stale solved count or a hardcoded solved list. The profile must be checked live each time.
5. Fetch current LeetCode problem metadata, tags, HTML description content, and code snippets. Do not trust hardcoded difficulty, premium, topic metadata, descriptions, or starter code.
6. A candidate is valid only when all of these are true:
    - its slug is not in the public solved-slug set;
    - its difficulty is in `DIFFICULTY_ORDER`;
    - it is not premium-only when `EXCLUDE_PREMIUM` is true;
    - it has at least one tag in `ALLOWED_TOPIC_SLUGS`;
    - it is not primarily a technique in `BLOCKED_MAJOR_TOPIC_SLUGS`;
    - its HTML description content does not contain any value in `REJECT_DESCRIPTION_HTML_PATTERNS`;
    - its description still makes sense after conversion to plain text;
    - LeetCode provides a Python or Python3 starter code snippet for it.
7. Check `PRIORITY_PROBLEM_SLUGS` in order and choose the first valid candidate.
8. If the priority list is exhausted, rank all valid candidates with this tuple and choose the minimum:

```python
(
    DIFFICULTY_ORDER.index(question["difficulty"]),
    -len(question_tags & ALLOWED_TOPIC_SLUGS),
    len(question_tags - ALLOWED_TOPIC_SLUGS),
    -float(question.get("acRate") or 0),
    int(question["frontendQuestionId"]),
)
```

9. If public recent submissions contain fewer unique solved slugs than the profile's total solved count, public history is incomplete. Do not ask for credentials. Use all visible public profile/activity evidence, exclude every known solved slug, and make the best public-data-only selection.
10. Build the final URL exactly as:

```python
url = f"https://leetcode.com/problems/{title_slug}/"
```

11. Convert the selected problem's LeetCode HTML description to readable plain text:
    - preserve paragraphs and example blocks as separate lines;
    - decode HTML entities;
    - remove all remaining HTML tags;
    - normalize repeated blank lines;
    - do not include image alt text as a substitute for a visual explanation.
12. Select the starter code snippet whose language name is `Python3` or `Python`, preferring `Python3` when both are available.
13. Create `<title-slug>.py` in the current working directory. Overwrite an existing file with the same name only when it is empty or clearly an unsolved LeetCode starter file for the same URL. If a non-empty existing file appears to contain user work, stop and ask before overwriting.
14. Write the generated file in this exact shape:

```python
# https://leetcode.com/problems/<title-slug>/
# <plain-text problem description line 1>
# <plain-text problem description line 2>

<leetcode-provided Python starter code>
```

15. Output only `url`.

## Public GraphQL query

This query is public and must be sent without authentication headers or cookies:

```graphql
query recentAcSubmissions($username: String!, $limit: Int!) {
  recentAcSubmissionList(username: $username, limit: $limit) {
    titleSlug
  }
}
```

Variables:

```json
{
  "username": "maciekbajor",
  "limit": 20
}
```

Endpoint:

```text
https://leetcode.com/graphql/
```

## Public problem-detail GraphQL query

Use this query for candidate validation and starter-file generation. Send it without authentication headers or cookies:

```graphql
query questionData($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    title
    titleSlug
    content
    difficulty
    isPaidOnly
    topicTags {
      slug
    }
    codeSnippets {
      lang
      langSlug
      code
    }
  }
}
```

Variables:

```json
{
  "titleSlug": "<title-slug>"
}
```

Endpoint:

```text
https://leetcode.com/graphql/
```

## Rules

- Always inspect the live public profile first.
- Never solve the selected problem or provide hints unless asked in a separate request.
- Verify current LeetCode tags; never infer topics from the title alone.
- Never select problems that need images, diagrams, tables, animations, or other visual explanation elements to understand the statement.
- Always create the Python starter file in the current working directory before returning the URL.
- Put the commented problem URL as the first line of the generated Python file.
- Never return more than one URL.
- Never return anything except the URL.
