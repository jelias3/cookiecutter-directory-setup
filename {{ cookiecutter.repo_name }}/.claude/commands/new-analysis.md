---
description: Create a new dated analysis directory with the correct zero-padded name
argument-hint: <topic_in_snake_case>
allowed-tools: Bash(mkdir:*), Bash(cp:*), Bash(date:*), Bash(ls:*), Read, Write, Edit
---

Today's date prefix: !`date +%y_%m_%d`

Create a new analysis directory for the topic: **$ARGUMENTS**

1. Normalize the topic to lowercase `snake_case`: spaces and hyphens become `_`, strip
   anything outside `[a-z0-9_]`. If the topic is empty, ask for one rather than guessing.
2. The directory is `analysis/<the date prefix above>_<normalized topic>/`. That prefix is
   already zero-padded because `date +%y_%m_%d` produces it that way — **do not
   hand-assemble it, and do not "tidy" it into `YYYY-MM-DD`.** The rule is declared in
   `analysis/README.md`.
3. If a directory with today's date and a similar topic already exists, stop and ask
   whether to use it instead of creating a near-duplicate.
4. Create the directory plus a `figures/` subdirectory.
5. Copy `analysis/_TEMPLATE_SUMMARY.md` to `<dir>/SUMMARY.md`, then fill in only what you
   actually know: the front-matter `date`, the notebook filename if the user named one, and
   the conda env. **Leave the instruction comment block in place** — it is guidance for
   whoever writes the summary later. Do not invent a `title` or `description`; those
   require results that do not exist yet.
6. Print the created paths, and remind the user that `analysis/.gitignore` is a deny-all
   allowlist, so any new file type in here needs an allow line before git will see it.

Do not create a notebook. Do not run anything.
