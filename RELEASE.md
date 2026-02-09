# Releasing

## Version Tags

This repository uses semver tags with floating major version tags:

- **Semver tags** (`v0.1.0`, `v0.2.0`, `v1.0.0`) — Immutable, point to specific commits
- **Major version tags** (`v0`, `v1`) — Floating, always point to the latest semver in that major

Users can reference actions using:
- `@v0` — Floating major version (recommended for most users)
- `@v0.1.0` — Exact semver (for reproducibility)
- `@<commit-sha>` — Full commit SHA (maximum security)

See [SECURITY.md](SECURITY.md#action-pinning) for security considerations around tag vs SHA pinning.

## Creating a Release

1. Ensure all changes are merged to `main`
2. Run:

```bash
make release VERSION=0.2.0
```

This will:
1. Validate the version format (semver)
2. Check that the tag doesn't already exist
3. Create and push the tag `v0.2.0`
4. Trigger the [release workflow](.github/workflows/release.yml), which:
   - Creates a GitHub release with auto-generated notes
   - Updates the floating major tag (`v0`) to point to this release

You can also create a release manually:

```bash
git tag v0.2.0
git push origin v0.2.0
```

## Version Bump Guidelines

- **Major** (`v0` → `v1`): Breaking changes to action inputs/outputs or behavior
- **Minor** (`v0.1` → `v0.2`): New features, new actions, non-breaking changes
- **Patch** (`v0.1.0` → `v0.1.1`): Bug fixes, documentation updates, prompt improvements
