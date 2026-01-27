# Feedback Summary

Collect reactions on AI agent comments and create a summary issue with analysis.

## Usage

See [example.yml](example.yml) for a complete workflow example.

## Features

The feedback summary workflow:
- Collects reactions (🚀, 👍, 👎, ❤️, 😕) on AI agent comments from issues, PRs, and reviews
- Generates a markdown report with statistics and analysis
- Optionally uses Claude to analyze feedback patterns and suggest improvements
- Creates a GitHub issue with the summary (if `create-issue` is true and interactions are found)

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `github-token` | GitHub token for API access | Yes | - |
| `claude-oauth-token` | Claude OAuth token for AI analysis (optional) | No | `""` |
| `days` | Number of days to look back for feedback | No | `"7"` |
| `bot-pattern` | Regex pattern to match bot usernames | No | `"claude\|github-actions\[bot\]\|copilot\[bot\]"` |
| `model` | Model to use for Claude analysis | No | `claude-sonnet-4-20250514` |
| `issue-labels` | Comma-separated labels for summary issue | No | `"ai-feedback,automated"` |
| `create-issue` | Whether to create a GitHub issue with the summary | No | `"true"` |

## Outputs

| Output | Description |
|--------|-------------|
| `feedback-json` | JSON data with collected feedback |
| `issue-url` | URL of the created issue (if `create-issue` is true and interactions found) |
