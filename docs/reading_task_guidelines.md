# Guidelines for human reading tasks

Maintained by ClaudeScope. Every worksheet or reading task given to a human reader must meet the rules below. The rules come from reader feedback, recorded at the end.

## Rules

1. **Say what each list is.** Every group of items gets a label that names its kind and its job in a sentence (for example "determiners: words that come before a noun"). Never separate groups with punctuation alone.
2. **Define every piece of notation before using it.** This includes placeholders (X, Y, N), parentheses for optional parts, slashes for alternatives, ellipses, and made-up forms such as "verbed". If a legend is needed, the notation is probably too heavy; prefer whole example sentences.
3. **Give the patterns as a table of real examples,** one row per pattern, with a valid sentence and, where it helps, an invalid near miss and the reason.
4. **State exactly what counts as valid.** If a question asks whether a sentence fits the language, the worksheet must let a careful reader decide every case from the page alone, including word order, which parts are optional, and which words may fill each position.
5. **Explain why the reader is given each piece of information** and which question it is for.
6. **Test before sending.** Before a worksheet goes to a human, a fresh agent session with no project context answers it and lists everything it found unclear. Fix those points first.
7. **Do not change a worksheet while a reader is working on it.** Record the problem, treat the affected answers with caution at reconciliation, and fix the next version.

## Feedback log

### 21 November 2026 · sponsor, on `fixtures/sponsor_worksheet.md` (fixtures version 1)

Raised while filling in the worksheet, about the section "The controlled language, briefly" (the word list and the sentence patterns):

- The instructions do not say what the listed items are.
- Groups are separated by semicolons. They appear to be different kinds of element, but this is never stated, and it is not explained why some are separated from others.
- It is unclear what counts as a valid construction when read strictly. One example among several: X is written without parentheses and (Y) with them, and the difference is not explained.

**Cause.** The word list labels only some groups (names, person nouns, thing nouns) and leaves the rest unlabelled (*a, every*; *did, not, to*; *quickly*; the verbs, which mix three kinds). The pattern line uses placeholders, parentheses for optional parts, a slash, an ellipsis, and "verbed" with no legend.

**Effect on this round.** Question C ("is every word in the list, and does the sentence fit a pattern?") depends on that section. The sponsor's answers to C are treated as provisional at reconciliation, and a disagreement on C alone is not counted against any specifier. Questions A, B, and D do not depend on it.

**Action.** Rules 1–6 above. The worksheet is not edited mid-task (rule 7).
