## Best-of-Three Investigation

## Process

1. **Spawn 3 sub-agents**. Each sub-agent receives the same Report Assignment (the full investigation task described in this prompt) and works independently.
   - Each sub-agent should explore a different starting point or angle — e.g., different files, different heuristics, or different areas of the codebase.
   - Each sub-agent gathers evidence, analyzes it, and produces either a candidate finding (with title, body, labels, and supporting evidence) or a recommendation to `noop`.

2. **Wait for all 3 to complete.** Do not proceed until every sub-agent has returned its result.

3. **Evaluate the candidates.** Based on the task

4. **Select the best candidate**

## Sub-agent prompt template

When spawning each sub-agent, include:
- The full text of the Report Assignment section from this prompt
- All relevant context (repo name, previous findings, etc.)
- An instruction to return a structured result: either `{ "action": "create_issue", "title": "...", "body": "...", "labels": [...] }` or `{ "action": "noop", "reason": "..." }`
- A unique instruction designed to help the sub-agent explore independently — do not coordinate with other sub-agents
