# Fix for Reaction Token Issue (#1267)

## Problem

After upgrading to gh-aw v0.79.3, workflows with reaction steps started failing with:
```
POST /repos/elastic/<repo>/issues/comments/4705949931/reactions - 403 Resource not accessible by integration
Error: Failed to add reaction: Resource not accessible by integration
```

## Root Cause

The gh-aw v0.79.3 compiler generates reaction steps in the `activation` job with:
```yaml
github-token: ${{ secrets.GITHUB_TOKEN }}
```

This has **two problems**:

1. **Token reference**: `secrets.GITHUB_TOKEN` refers to a user-defined secret (not the automatic GitHub Actions token) which may not exist.

2. **Missing permissions**: The `activation` job only has `actions: read` and `contents: read` permissions, but adding reactions requires `issues: write` permission.

Even with the correct token, reactions will fail without `issues: write` permission.

## Solution

This fix addresses the **token reference issue** by replacing `secrets.GITHUB_TOKEN` with `github.token` in reaction steps:
```yaml
github-token: ${{ github.token }}
```

However, **the permissions issue remains** - the `activation` job still lacks `issues: write`. This appears to be a gh-aw compiler limitation: even when `issues: write` is specified in the source `.md` file, the compiler does not grant it to the `activation` job where the reaction step runs.

The `safe_outputs` job (which runs later) has `issues: write`, but reactions need to run early for immediate feedback.

## Implementation

1. **Post-processing script** (`scripts/fix-reaction-token.py`):
   - Automatically fixes token references in all `.lock.yml` files
   - Only modifies reaction steps (identified by "Add eyes reaction for immediate feedback")
   - Preserves other uses of `secrets.GITHUB_TOKEN` which are intentional

2. **Makefile integration**:
   - Added to the `postprocess-setup-action` target
   - Runs automatically after workflow compilation

## Affected Workflows

The fix was applied to 10 workflows:
- gh-aw-deep-research.lock.yml
- gh-aw-internal-gemini-cli-web-search.lock.yml
- gh-aw-internal-gemini-cli.lock.yml
- gh-aw-issue-fixer.lock.yml
- gh-aw-issue-triage.lock.yml
- gh-aw-mention-in-issue-no-sandbox.lock.yml
- gh-aw-mention-in-issue.lock.yml
- gh-aw-mention-in-pr-no-sandbox.lock.yml
- gh-aw-mention-in-pr.lock.yml
- gh-aw-plan.lock.yml

## Testing

Run the validation script to verify all reaction steps use the correct token:
```bash
bash /tmp/test-reaction-token.sh
```

## Future Considerations

This issue may be resolved in a future version of the gh-aw compiler. Monitor upstream releases and consider removing this post-processing step if the compiler is fixed.

### Recommended Actions

1. **Short-term**: The token fix in this PR reduces the likelihood of 403 errors by using the correct token reference.

2. **Long-term**: Report to gh-aw upstream that:
   - The `activation` job needs `issues: write` permission when `reaction:` is configured
   - The compiler should respect permissions specified in source `.md` files for jobs that need them
   - Or provide a way to configure which job the reaction step runs in

3. **Alternative workaround**: Remove the `reaction: "eyes"` directive from source `.md` files until gh-aw properly grants the necessary permissions.
