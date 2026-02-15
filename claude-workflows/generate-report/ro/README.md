# Generate Report

Generate reports on a schedule using Claude with user-provided instructions. A general-purpose action for any kind of periodic reporting: weekly summaries, CVE triage, dependency audits, activity digests, etc.

## Capabilities

- ✅ Read and analyze code
- ✅ Read-only git commands
- ✅ Full `gh` CLI access (issues, PRs, releases, discussions, API)
- ✅ Web search and URL fetching
- ✅ Create GitHub issues with reports
- ❌ Cannot modify repository files
- ❌ Cannot commit or push changes

## Usage

See [example.yml](example.yml) for a complete workflow example.

The key input is `instructions` -- this tells Claude what to research, analyze, and how to format the report. Think of it as the "prompt" that defines your report.

```yaml
- uses: elastic/ai-github-actions/workflows/generate-report/ro@v0
  with:
    claude-oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    github-token: ${{ github.token }}
    instructions: |
      Analyze open CVEs labeled 'security' and produce a triage report.
      For each CVE: determine the owning team, assess severity, and recommend an action.
```

## How It Works

1. Claude reads the repository context (via `agents-md-generator` and `AGENTS.md`)
2. Claude follows your `instructions` to research and analyze
3. Claude writes the report to a temp file
4. The action creates a GitHub issue with the report contents

Because Claude reads `AGENTS.md` automatically, you can reference documentation files from there to provide additional context. For example, if you have a `triage-cve.md` runbook, reference it from `AGENTS.md` and Claude will discover and follow it.

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `claude-oauth-token` | Claude OAuth token | Yes | - |
| `github-token` | GitHub token for Claude | Yes | - |
| `instructions` | Instructions for the report (what to analyze, how to format) | Yes | - |
| `model` | Model to use | No | `claude-opus-4-5-20251101` |
| `allowed-tools` | Allowed tools (defaults include: file reading, `gh` CLI, git, web search, MCP tools) | No | See action.yml |
| `extra-allowed-tools` | Additional allowed tools (concatenated with allowed-tools) | No | `""` |
| `additional-instructions` | Extra instructions appended to the prompt | No | `""` |
| `issue-title` | Title for the created issue | No | `""` (defaults to `Report - YYYY-MM-DD` at runtime) |
| `issue-labels` | Comma-separated labels for the issue | No | `report,automated` |
| `mcp-servers` | MCP server configuration JSON | No | See main README |
| `repository-owner` | Repository owner | No | Auto-detected |
| `repository-name` | Repository name | No | Auto-detected |
| `assignee` | Comma-separated GitHub usernames to assign the issue | No | `""` |

## Outputs

| Output | Description |
|--------|-------------|
| `conclusion` | The conclusion of the Claude Code run |
| `issue-url` | URL of the created issue |

## Examples

### CVE Triage Report

```yaml
- uses: elastic/ai-github-actions/workflows/generate-report/ro@v0
  with:
    claude-oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    github-token: ${{ github.token }}
    issue-title: "CVE Triage Report - $(date +%Y-%m-%d)"
    issue-labels: "security,triage,automated"
    instructions: |
      Triage open CVE issues in this repository.

      1. Find all open issues labeled 'CVE' or 'security'
      2. For each CVE:
         - Identify the affected component and owning team
         - Assess severity (Critical/High/Medium/Low)
         - Check if a fix is already in progress (linked PRs)
         - Recommend an action (fix, mitigate, accept, defer)
      3. Produce a summary table sorted by severity
```

### Dependency Audit

```yaml
- uses: elastic/ai-github-actions/workflows/generate-report/ro@v0
  with:
    claude-oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    github-token: ${{ github.token }}
    issue-title: "Dependency Audit - $(date +%Y-%m-%d)"
    issue-labels: "dependencies,automated"
    instructions: |
      Audit the project's dependencies for known issues.

      1. Read package.json / requirements.txt / go.mod (whichever applies)
      2. Search for known vulnerabilities in major dependencies
      3. Check for outdated dependencies with available updates
      4. Produce a report with: dependency name, current version, latest version, known issues
```

### Weekly Activity Digest

```yaml
- uses: elastic/ai-github-actions/workflows/generate-report/ro@v0
  with:
    claude-oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    github-token: ${{ github.token }}
    issue-title: "Weekly Digest - $(date +%Y-%m-%d)"
    issue-labels: "report,weekly"
    instructions: |
      Summarize repository activity for the past 7 days.

      Include: new issues, merged PRs, new contributors, CI health, and any blockers.
```
