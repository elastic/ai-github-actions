### Pick Three, Keep One

Parallelize your initial investigation using sub-agents. Spawn 3 sub-agents, each with a distinct angle — e.g., different starting points, different areas of the codebase, or different heuristics. Each sub-agent works independently and should return its single best candidate finding (with file paths, line numbers, and evidence) or a recommendation to `noop`. The goal is competition: 3 sub-agents each produce their best shot, and you pick the winner.

**How to spawn sub-agents:** Call `runSubagent` with `model: "${{ inputs.model }}"` and the `agentType` specified by the workflow instructions below (defaulting to `agentType: "general-purpose"` if not specified). Always pass the model explicitly. Sub-agents cannot see your conversation history, the other sub-agents' results, or any context you have gathered so far. Each prompt must be **fully self-contained** — include everything the sub-agent needs to do its job:

- The full task description and objective (restate it, don't summarize)
- All repository context, conventions, and constraints you've gathered (e.g., from `generate_agents_md`)
- Any relevant findings from your initial exploration (file paths, git log output, code snippets)
- The quality gate criteria and output format you expect
- The specific angle that distinguishes this sub-agent from the others

Err on the side of providing too much context rather than too little. A well-informed sub-agent with a 10,000-token prompt will produce far better results than one with a 200-token prompt that has to rediscover everything from scratch.

**Wait for all 3 sub-agents to complete.** Do not proceed until every sub-agent has returned its result.

**Evaluate the candidates** by comparing evidence quality, specificity, and actionability. Prefer candidates with concrete file paths, line numbers, and verifiable evidence over general observations. If most or all sub-agents recommend `noop`, that is a strong signal to `noop`.

**Select the single best candidate** and proceed with it. Discard the others. If no candidate meets the quality gate, call `noop`.
