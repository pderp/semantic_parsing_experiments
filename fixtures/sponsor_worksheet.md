# Reading worksheet for the sponsor · fixtures version 1

**Time:** about 30 to 45 minutes. Please note your start and finish times at the bottom; the plans use them to estimate reading costs.

**What this is for.** Three agents are writing the formal meaning of 12 sentences independently. Your answers are the human reference they are compared with. You answer in plain English. You do not need to write any formal notation, and there are no trick questions.

**Rules.**

1. Do not ask any agent about these sentences until you have finished, and do not look at files under `fixtures/` other than this one.
2. Read each sentence as ordinary English. If you are unsure, say so in the notes; "unsure" is a useful answer.
3. Write your answers into this file under each sentence, then tell ClaudeScope you are done. Do not edit the file afterwards.

## The controlled language, briefly

The parser only accepts a small language. Questions C and D below ask about it.

- **Words:** ten names (Alice, Bob, Ava, Ben, Cara, Dan, Eva, Finn, Gia, Hugo); person nouns (researcher, reviewer, author, editor, scientist, scholar, student, professor, analyst, investigator); thing nouns (paper, manuscript, report, proposal, article, thesis, draft, preprint, abstract, dataset); *a*, *every*; *did*, *not*, *to*; *quickly*; verbs *leave, arrive, wait, speak, review, cite, discuss, evaluate, promise, persuade*.
- **Sentence patterns:** *X verbed (Y) (quickly)*; *X did not verb (Y) (quickly)*; *Not every N verbed …*; *X promised/persuaded Y to verb (Z) (quickly)*. *Quickly* comes only at the end.

## For each sentence, answer

- **A. Who did what to whom?** In your own words.
- **B. One meaning or two?** If two, write both as plain paraphrases. (Example of two meanings, from a sentence not on this list: *Every researcher reviewed a paper* can mean each researcher reviewed some paper or other, or that there is one particular paper they all reviewed.)
- **C. Is every word in the word list above, and does the sentence fit one of the patterns?** Yes or no; if no, what is the problem?
- **D. Anything that does not follow.** For sentences with *not*, *promised*, or *persuaded*: does the sentence say that the leaving, reviewing, and so on actually happened?

---

**F01. Bob cited Ava.**

A: Bob used Ava's ideas, thoughts and/or writing in work of his own.
B: One meaning.
B2: One meaning.
C: Yes.
D:

**F02. A student evaluated every thesis.**

A: One individual student analyzed and/or reviewed, and then gave an opinion, grade, and/or conclusion about each of all existing theses.
B: One meaning.
B2: One meaning.
C: Unsure.
D:

**F03. Every editor discussed every report quickly.**

A: There are one or more editors. Each of them had a conversation (with who they had this conversation is unclear) about each of one or more reports in a set of reports that was the same for each of the editors, and this took place without delay.
B: One meaning
B2: One meaning
C: Unsure.
D:

**F04. Dan did not arrive.**

A: A location where Dan was perhaps previously expected to appear was not one that he appeared at.
B: Given timelessness, one meaning. Considering temporality, there may be more than one thing this sentence could mean.
B2: One meaning.
C: I think so
D: Time is unspecified. All we know is that an expected event did not take place at some time. Whether this time was in the past or is "the present" is not certain (the latter may be assumed?). Where or when Dan was "supposed to" arrive is also unknown.

**F05. A scholar did not cite every dataset.**

A: There may or may not be more than one scholar. One scholar was probably assumed to have (assigned to have?) referred to (in a publication?) all of the datasets in some (unspecified) collection of datasets, but this scholar did not do this with all of the datasets. It may be that the scholar did cite one or or datasets, or it may be that the scholar did no citing of any dataset(s).
B: Many possible meanings (in that it could mean the scholar cited no datasets or some, or most, or just one -- also what is unknown is how many datasets there were).
B2: Unsure.
C: I think so
D: Lots of ambiguity.

**F06. Not every analyst evaluated a proposal quickly.**

A: A collection of people, each with the role of analyst, exists. Each analyst carried out an evaluation (an analysis, review, grading, conclusive measurement and/or comparison to some standard) of a proposal. One or more of them took more time than was expected, or required, or it was assumed they would. Or maybe the speed of their evaluation was just slower than that of other analysts. 
B: Many meanings
B2: One meaning
C: Probably
D: Lots of ambiguity.

**F07. Not every reviewer discussed every abstract.**

A: There were one or more reviewers. Only a subset (perhaps none of them) reviewed every abstract. 
B: One meaning.
C: Yes
D: It does not follow that any abstract was reviewed.

**F08. Gia promised a student to speak quickly.**

A: A promise was made by Gia. That promise was probably to a student and the promise was that Gia would speak quickly.
B: Unsure
C: Yes
D: (Also: who is to speak? What is quick: the promising or the speaking?) I didn't write the parentheticals, but I see no clear evidence more does not follow, even with this parenthetical prompt.

**F09. Every investigator persuaded a scientist to leave.**

A: Either every investigator persuaded a specific scientist to leave or different investigators may have persuaded different scientists to leave.
B: Two meanings.
C: Yes.
D: (Also: who is to leave?) Nothing doesn't follow as far as I can tell (again, i'm unclear where the (first) parenthetical here came from as I didn't write it)

**F10. Hugo did not persuade Eva to review every preprint quickly.**

A: Hugo either persuaded Eva to review none or some preprints quickly, but not all of them, or he persuaded Eva to to only review some preprints (regardless of her speed of review (quickly or not)).
B: Two meanings.
C: Yes.
D: It does not follow that any preprints were reviewed by Eva.

**F11. Cara reviewed the article.**

A: An article exists which was reviewed by Cara.
B: One meaning.
C: Yes
D:

**F12. Finn quickly arrived.**

A: There was no (or very little) delay with Finn's arrival.
B: One meaning.
C: No.
D: Something strikes me as "off" with the temporality here, in that an arrival is an event, and quickly would normally describe a process (rather than a point in time).

---

Start time: 3:27am

Finish time: 3:59am  (for the first half of the assignment only)

During the 2nd attempt in which the B2 entries were appended to some of the previously done first 6 sentences and the final 6 sentences were completed, the elapsed wall clock time was a total of 31 minutes.


General notes:  Some parentheticals weirdly seemed to appear in some of the answers for D in the second half of the questions. I don't think they were originally there (but I may be mistaken). It did just seem odd that I was getting extra prompting and I'm wondering if maybe it might have been something leaking over from other evaluations from one or more agents...
