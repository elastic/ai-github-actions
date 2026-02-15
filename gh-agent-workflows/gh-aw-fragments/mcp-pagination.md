---
# DO NOT EDIT — this is a synced copy. Source: .github/workflows/gh-aw-fragments/mcp-pagination.md

MCP tool responses have a **25,000 token limit**. When responses exceed this limit, the call fails and you must retry with pagination — wasting turns and tokens. Use proactive pagination to stay under the limit.

### Recommended `perPage` Values

- **5-10**: For detailed items (PR diffs, files with patches, issues with comments)
- **20-30**: For medium-detail lists (commits, review comments, issue lists)
- **50-100**: For simple list operations (branches, labels, tags)

### Pagination Pattern

When you need all results from a paginated API:

1. Fetch the first page with a conservative `perPage` value
2. Process the results before fetching the next page
3. Continue fetching pages until you receive fewer results than `perPage` (indicating the last page)

### Error Recovery

If you see an error like:
- `MCP tool response exceeds maximum allowed tokens (25000)`
- `Response too large for tool [tool_name]`

Retry the same call with a smaller `perPage` value (halve it).

### Tips

- **Start small**: It's better to make multiple small requests than one that fails
- **Fetch incrementally**: Get an overview first, then details for specific items
- **Use filters**: Combine `perPage` with state, label, or date filters to reduce result size
- **Process as you go**: Don't accumulate all pages before acting — process each batch immediately
