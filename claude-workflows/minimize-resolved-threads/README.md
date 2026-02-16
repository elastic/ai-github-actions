# Minimize Resolved Review Threads

Minimize resolved pull request review threads authored by specific users (defaults to `github-actions[bot]`).

## Usage

````yaml
- uses: elastic/ai-github-actions/claude-workflows/minimize-resolved-threads@v0
  with:
    github-token: ${{ github.token }}
    # Optional overrides:
    # repository: ${{ github.repository }}
    # pull-request-number: ${{ github.event.pull_request.number }}
    # author-logins: "github-actions[bot]"
````

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `github-token` | GitHub token with permission to minimize review threads | Yes | - |
| `repository` | Repository in owner/repo format | No | `${{ github.repository }}` |
| `pull-request-number` | Pull request number | No | `${{ github.event.pull_request.number }}` |
| `author-logins` | Comma-separated list of comment author logins to minimize | No | `github-actions[bot]` |
| `dry-run` | If `true`, report matching threads without minimizing | No | `false` |

## Permissions

The workflow using this action must grant write access to pull requests (and issues if required by the token).
