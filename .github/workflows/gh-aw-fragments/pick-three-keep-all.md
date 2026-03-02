### Pick Three, Keep All

Parallelize your work using sub-agents. Spawn 3 sub-agents, each approaching the task from a different angle — e.g., different focus areas, different heuristics, or different parts of the codebase. Each sub-agent works independently and should return its own list of findings.

**How to spawn sub-agents:** Call `runSubagent` with `agentType: "general-purpose"` and `model: "${{ inputs.model }}"` (unless the workflow specifies a different agent type or model). Sub-agents cannot see your conversation history, the other sub-agents' results, or any context you have gathered so far. Each prompt must be **fully self-contained** — include everything the sub-agent needs:

- The full task description and objective (restate it, don't summarize)
- All repository context, conventions, and constraints you've gathered (e.g., from `/tmp/agents.md`)
- Any relevant data the sub-agent needs to do its job (diffs, file contents, existing threads)
- The quality criteria and output format you expect
- The specific angle that distinguishes this sub-agent from the others

Err on the side of providing too much context rather than too little. A well-informed sub-agent with a 10,000-token prompt will produce far better results than one that has to rediscover the codebase from scratch.

**Wait for all 3 sub-agents to complete.** Do not proceed until every sub-agent has returned its result.

**Merge and deduplicate findings** across all sub-agents:
1. If multiple sub-agents flagged the same issue, keep the version with the strongest evidence and clearest explanation.
2. If a finding is unique to one sub-agent, include it if it passes the quality gate.
3. Drop any finding that does not meet the verification criteria — a finding flagged by only one sub-agent deserves extra scrutiny.

**Apply the quality gate to every surviving finding individually.** Each must have concrete evidence and be verified before you act on it.
