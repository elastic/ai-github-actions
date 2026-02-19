# Release process

This repository uses semver tags with floating major tags. For the full release guide, see https://github.com/elastic/ai-github-actions/blob/main/RELEASE.md.

## Summary

- Use `@v0` for the floating major tag, or `@v0.1.0` for an exact release.
- Run `make release VERSION=x.y.z` from `main` to create a new tag and trigger the release workflow.
