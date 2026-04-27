---
safe-outputs:
  add-labels:
    max: 3
  steps:
    - name: Pre-sanitize labels from input allowlist
      uses: actions/github-script@v9
      env:
        GH_AW_AGENT_OUTPUT: ${{ steps.setup-agent-output-env.outputs.GH_AW_AGENT_OUTPUT }}
        CLASSIFICATION_LABELS: ${{ inputs.classification-labels }}
      with:
        script: |
          const fs = require('fs');
          const outputPath = process.env.GH_AW_AGENT_OUTPUT;
          if (!outputPath || !fs.existsSync(outputPath)) {
            core.info('No GH_AW_AGENT_OUTPUT file found; skipping.');
            return;
          }
          const doc = JSON.parse(fs.readFileSync(outputPath, 'utf8'));
          if (!Array.isArray(doc.items)) {
            core.warning('agent output has no items array; skipping.');
            return;
          }
          const allowed = new Set(
            String(process.env.CLASSIFICATION_LABELS || '')
              .split(',')
              .map((s) => s.trim())
              .filter(Boolean)
          );
          if (allowed.size === 0) {
            const before = doc.items.length;
            doc.items = doc.items.filter((item) => item?.type !== 'add_labels');
            fs.writeFileSync(outputPath, JSON.stringify(doc));
            core.info(`No allowed labels provided; removed ${before - doc.items.length} add_labels operations.`);
            return;
          }
          let removed = 0;
          let dropped = 0;
          doc.items = doc.items.filter((item) => {
            if (item?.type !== 'add_labels' || !Array.isArray(item.labels)) {
              return true;
            }
            const before = item.labels.length;
            item.labels = item.labels
              .map((v) => String(v).trim())
              .filter((v) => v && allowed.has(v));
            removed += Math.max(0, before - item.labels.length);
            if (item.labels.length === 0) {
              dropped++;
              return false;
            }
            return true;
          });
          fs.writeFileSync(outputPath, JSON.stringify(doc));
          core.info(`Sanitized label ops: removed=${removed}, dropped_messages=${dropped}`);
---

## add-labels Limitations

- **Labels**: Max 3 labels per run. Each label max 64 characters. Labels starting with `-` are rejected.
- **Allowlist**: Only labels in `classification-labels` are accepted; all others are stripped before processing.
- **Sanitization**: Labels are trimmed, deduplicated, and Unicode-normalized. `@` mentions are neutralized (backticked).
