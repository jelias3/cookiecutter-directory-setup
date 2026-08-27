---
description: Add a row to code/config/samples.tsv, validating the sample-ID grammar
argument-hint: <sample_id> [key=value ...]
allowed-tools: Read, Edit, Bash(git diff:*), Bash(column:*)
---

Add a sample to `code/config/samples.tsv`: **$ARGUMENTS**

1. Read `code/config/samples.tsv` first and use its **actual current header** — never
   assume the columns. Read `code/schemas/samples.schema.yaml` too: it is the authoritative
   column list, types, defaults, and the sample-ID pattern.
2. Validate the sample ID against the grammar in `docs/conventions.md` §Samples (default:
   `<YY>_<MM>_<DD>_<subject>[_rep<N>]`, zero-padded). If it does not match, say exactly
   which part fails and stop. **Do not silently reformat the user's ID** — the ID is a
   wildcard value that appears in every output path for that sample, so changing it later
   is a migration, not an edit.
3. Reject a duplicate ID, and report which existing row collides.
4. Append **one tab-separated row**. Preserve tabs exactly — this file is TSV, not
   whitespace-aligned. Fill unspecified columns with the schema's `default`, or the same
   placeholder the existing rows use; never leave a column silently blank without saying so.
5. Show `git diff -- code/config/samples.tsv` and stop. Do not run snakemake.

If a referenced input path in the new row does not exist on disk, say so — but do not
create it and do not remove the row. A missing input is information, not an error to paper
over.
