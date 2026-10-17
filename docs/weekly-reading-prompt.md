# The scheduled reading's prompt

Written 2026-10-17, the day the site went live, in the session that built the weekly reading. This is the text the scheduled cloud task is given every week, in the siblings' form (The Quiet Galaxy's `docs/weekly-reading-prompt.md` and The Upgrade Tree's). It is deliberately short: it says where the repository is and which file to follow, so that the procedure (`docs/weekly-reading.md`) can change without anyone touching the task. The scheduled task itself has not been created: that is done at claude.ai/code/routines by John or by the master session, from this text, and the section after the prompt says how.

## The prompt

> You are running Outrunning Ageing's weekly reading of its records against the news, for John Fredrickson. Do this without asking questions:
>
> 1. The repository jfredson/outrunning-ageing is cloned in the workspace; cd into it, then run `git fetch origin && git checkout -B main origin/main` before anything else (the clone lands on a session branch and may be behind).
> 2. Read docs/weekly-reading.md and follow its procedure exactly, top to bottom. It tells you which records to read (every treatment, every claim and every self-experiment), how to search the web against each one, the four verdicts, what you may and may not edit, how to log a publication, how to move a treatment one rung and when you may not, how to write data/scans/YYYY-MM-DD.toml, and how to commit and push to main with the one publish command.
> 3. If the push to main is refused, the publish command parks the commit on a branch named claude/reading-YYYY-MM-DD and says so; report the branch name and do not retry or look for another route. If that push is refused too, put the reading record's contents in your final report and stop.
> 4. Finish with the report format the procedure specifies: a short numbered list, John's action items first. No prose beyond that.
>
> Get the date in John's time zone first (`TZ=America/Los_Angeles date +%F`); all dates you write are absolute, year-month-day. Web search is your main tool; use it for every record, at least twice. Plain language throughout, UK spelling, and never a bare id: every treatment, claim, self-experiment and publication is named in words beside its id.

## How the scheduled task is to be created

At claude.ai/code/routines, copying The Quiet Galaxy's weekly reading routine field for field:

- **Name:** "Outrunning Ageing weekly reading".
- **Schedule:** proposed Sundays at 06:00 Pacific (as a cron expression in John's time zone, `CRON_TZ=America/Los_Angeles 0 6 * * 0`), between The Quiet Galaxy's Saturday evening reading and The Upgrade Tree's Monday morning one, and before The Belt Equation's Sunday evening scan, so no two of the family's runs push at once and all four are on the record by Monday. The schedule is proposed, not ruled (`docs/weekly-reading.md`, design choice 10), and is one field to change.
- **Environment:** the default cloud environment, with the repository `https://github.com/jfredson/outrunning-ageing` attached as its source and permission to push to main (the "outcomes" field naming the branch `main`, as the siblings' routines have). Pushing needs the Claude GitHub App to have access to the repository; if a run's push is refused, the commit lands on the fallback branch and the report says so, and giving the app access is John's action. The environment's network access must allow the journal, registry and company hosts the reading opens (the first reading, run from a cloud session on 2026-10-17, could reach none of them, and logged nothing for that reason; `docs/weekly-reading.md`, "What the first reading found").
- **Tools:** Bash, Read, Write, Edit, Glob, Grep, WebFetch and WebSearch, the siblings' list. The search allowance must cover about 170 to 200 searches in one run (every record, at least twice).
- **Connector:** Time-Assembler, for the worklog entry at the end of the procedure (step 8).
- **Model:** the routine's default, as the siblings'.
- **Notifications:** the routine's own push notification when a run finishes; the run's report is in the routine's run list at claude.ai/code/routines.

When it exists, its id and page are recorded here, and the date of its first firing.

## How to switch it off, change it or run it now

At claude.ai/code/routines, open "Outrunning Ageing weekly reading": the toggle disables it without deleting it; the schedule, the prompt and the tools are fields on the same page; "Run now" starts a run outside the schedule. A Claude Code session can do the same with the scheduled-task tools (pause with the enabled flag, start a run, list runs and read a run's log). Deleting it is done on the page, not from a session.
