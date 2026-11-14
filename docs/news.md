# The news posts: this site's rules

This site's news posts follow the family's tracker pattern, rules 4.10 to 4.19
(`sentient-horizons/design/tracker-pattern.md`, ruled by John from 2026-10-18), with one change
of 2026-11-09 written out below. `scripts/check_news.py` enforces what a script can check; the
build runs it before anything else, and its tests are the `NewsPosts` class in
`scripts/test_compute.py`.

## The change of 2026-11-09: a post may tell a story that changes no record

**What John agreed.** On 2026-11-09, ruling on the trial of the weekly reading
(`docs/readings/fable-trial-2026-11-09.md`), John agreed that a news post may be written about a
story that changes no record, and said he is leaning towards all news of interest to the project
being worth writing about. Until then a post could only explain a change the records already
carried (rule 4.11's six kinds of event, and rule 4.18's test that a change is news only when it
moves a headline number, a stage, a count or a notable first), and the check refused any post that
named no record, or whose records showed no dated change within fourteen days of it.

**What it changes.** A post of an eighth kind, "a story from the field" (`kind: story` in the
frontmatter), may be written about a story from the field that a visitor to the site would care
about, whether or not it moves anything here. It is the post the weekly reading's story shortlist
feeds (`docs/weekly-reading.md`, step 1a part H: a story dated in the reading's window, whose own
source was opened, that a visitor would care about). Rule 4.18's test still decides whether a
*change to the records* gets a post; it no longer decides whether a *story* may be told. The Belt
Equation has had the same kind of post since 2026-10-27, under the name "discovery".

**What a story post must say when no record changes.** It sticks to the news. It does not have to
say what the story leaves unchanged on the site: John ruled on 2026-11-09, for every tracker's news
posts, "Not every article needs to include the statement ... the article itself can stick to the
news" (rule 4.19 as amended that day). So a story post:

1. **Opens on what happened, in one plain sentence** (rule 4.19), then tells the story and why a
   visitor would care: what was found or announced, by whom, when, and how sure anyone can be of it.
2. **Mentions the site's own entries and estimates only where the story bears on one, in a
   sentence, not a section.** If a reader would otherwise think a number here moved, that sentence
   says it did not and why (for example, what would have to be published first). It never explains
   a change in a number: a story that turns out to move a record is written up as the kind of change
   it makes, after the record is changed, not as a story.
3. **Carries no before-and-after line** (`before`, `after` in the frontmatter), since no number
   moved. The post's preview card therefore shows its title and the kind, and no numbers line. The
   check refuses a story post that carries one.
4. **May name the entries it bears on** in `records`, so that each entry's page links the post. It
   need not name any, and the entries it names need show no change; each one named must exist.

Everything every post must carry still holds, and the check still enforces the parts a script can:
the dated file name and the matching date, a title, a summary, at least one source with an https
address, and a link in every paragraph that states a figure. By hand, as before: every date says
what happened on it, world dates and site dates kept apart (rule 4.12); every named thing is linked
at its first mention and the link opened (rule 4.17); no tool is named; the post passes the plain
reading pass and the cold-reader check (rule 4.19); no post goes live while any record on the site
carries an open check (rule 4.11, the promotion gate, written up in the post's file under
`docs/news-checks/`); and John approves every post before it goes live (rule 4.18).

**What does not change.** The other seven kinds keep every rule they had, including the
fourteen-day record change: an "estimate revised" post with no revision behind it is still refused.

**The family's rule.** The tracker pattern still lists, for the trackers other than The Belt
Equation, six kinds of event and the record-change window. Whether the other sibling sites take the
same change is a separate piece of work, and John's to rule; until then this document is where this
site departs from the pattern.

| The choice | Confidence | Standard or judgment | Strongest alternative, and its cost |
|---|---|---|---|
| A new eighth kind, "a story from the field", rather than letting any kind skip the record change | High: it keeps the old check whole for the kinds that announce a change, a reader sees from the label that this is a story, and it is how The Belt Equation did it | Follows the family's precedent | Drop the record-change rule for every kind; simpler, but an "estimate revised" post could then go out with no revision behind it |
| Called "story", not "discovery" as on The Belt Equation | Moderate: most ageing news is a trial result or an approval, not a discovery; the weekly reading already calls these stories | Judgment call | "discovery", for one word across the family; it would mislabel a failed trial or a regulator's decision |
| No limit on how old the story may be | Moderate: The Belt Equation's check sets none, and its model post of 2026-11-09 told a story announced three weeks earlier | Follows the family's precedent | Require the story's date in the frontmatter and refuse one more than fourteen days before the post; a stronger guard against stale news, at the cost of a field and of refusing a late but worthwhile post |
| No required line saying that nothing changed | High: John ruled on 2026-11-09 that a post may stick to the news | John's ruling | A required "What it changes here" sentence; refused by that ruling |

Written 2026-11-14 from John's agreement of 2026-11-09. The choices in the table are proposed, and
are settled when John approves the pull request that carries them.
