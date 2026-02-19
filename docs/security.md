# Security considerations

This page summarizes key guidance. For the full policy and examples, see https://github.com/elastic/ai-github-actions/blob/main/SECURITY.md.

## Key practices

- Restrict triggers with `author_association` checks for issue and comment events.
- Use minimum `permissions:` and prefer `contents: read` to prevent unintended pushes.
- Treat user-controlled text as untrusted and avoid interpolating it into shell commands.
- Review action pinning guidance and consider SHA pinning for production use.
