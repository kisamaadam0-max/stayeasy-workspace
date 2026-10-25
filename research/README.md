# Research

Data and notes Codex collects so Claude can analyse them. Each delivery answers one `research_request` issue.

- `notes/YYYY-MM-DD-topic.md`: one note per request, using the template below.
- `data/YYYY-MM-DD-topic.csv`: the dataset, if any. UTF-8, one header row, with `source` and `collected_at` columns.

Research is input, not a rule. It becomes a decision only when Adam approves a recommendation based on it.

## Note template

```markdown
# <Topic>

- **Issue:** #
- **Question answered:**
- **Sources and dates collected:**
- **What was found:** facts only, each with its source
- **Estimates:** labelled, with the method
- **Gaps:** what could not be found and why
- **Licence or terms of use:**
- **Data file:** research/data/...
```
