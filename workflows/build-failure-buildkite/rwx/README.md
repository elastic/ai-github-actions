# Build Failure (Buildkite)

Analyze Buildkite CI build failures and suggest fixes. Can provide code suggestions and run tests to verify recommendations. Claude will automatically discover the pipeline and build number from the commit SHA.

## Usage

See [example.yml](example.yml) for a complete workflow example.

## Buildkite Auto-Discovery

- **Pipeline**: Automatically discovered by matching the repository name against available pipelines in the organization
- **Build Number**: Automatically discovered by searching for builds matching the commit SHA
- **Organization**: Defaults to `"elastic"` but can be overridden

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `claude-oauth-token` | Claude OAuth token | Yes | - |
| `github-token` | GitHub token for Claude | Yes | - |
| `buildkite-api-token` | Buildkite API token | Yes | - |
| `buildkite-org` | Buildkite organization slug | No | `"elastic"` |
| `buildkite-pipeline` | Buildkite pipeline slug (auto-discovered if not provided) | No | `""` |
| `buildkite-build-number` | Buildkite build number (auto-discovered if not provided) | No | `""` |
| `model` | Model to use | No | `claude-sonnet-4-20250514` |
| `allowed-tools` | Allowed tools (defaults include: Edit, Write, Bash(*), MCP tools, Buildkite MCP) | No | See action.yml for full default list |
| `extra-allowed-tools` | Additional tools to add to the defaults | No | `""` |
| `additional-instructions` | Extra instructions for the prompt | No | `""` |
| `track-progress` | Track progress with visual indicators | No | `true` |
| `mcp-servers` | Additional MCP server configuration JSON (merged with defaults) | No | `""` |

## Outputs

| Output | Description |
|--------|-------------|
| `conclusion` | The conclusion of the Claude Code run |
