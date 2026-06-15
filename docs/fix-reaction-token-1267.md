# Fix for Reaction Token Issue (#1267)

## Problem

After upgrading to gh-aw v0.79.3, workflows with reaction steps started failing with:
```
POST /repos/elastic/<repo>/issues/comments/4705949931/reactions - 403 Resource not accessible by integration
Error: Failed to add reaction: Resource not accessible by integration
```

## Root Cause

The gh-aw v0.79.3 compiler was generating reaction steps with:
```yaml
github-token: ${{ secrets.GITHUB_TOKEN }}
```

This refers to a user-defined secret named `GITHUB_TOKEN` which may not exist or have the correct permissions. When this secret doesn't exist, the API call fails with a 403 error.

## Solution

The fix replaces `secrets.GITHUB_TOKEN` with `github.token` in reaction steps:
```yaml
github-token: ${{ github.token }}
```

The `github.token` is the automatic token provided by GitHub Actions with the permissions specified in the workflow's `permissions` section.

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
