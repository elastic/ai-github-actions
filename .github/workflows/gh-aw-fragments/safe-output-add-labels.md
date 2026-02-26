---
safe-outputs:
  add-labels:
    max: 3
---

## add-labels Limitations

- **Max labels per run**: 3 (configurable with `max`).
- **Label length**: Max 64 characters per label. Longer labels are truncated.
- **No removal**: Labels starting with `-` are rejected. Use `remove-labels` to remove labels.
- **Deduplication**: Duplicate labels are silently deduplicated.
- **Mentions**: `@mentions` in labels are neutralized (backticked).
- **Special characters**: `<`, `>`, `&`, `'`, `"` are stripped from label names.
