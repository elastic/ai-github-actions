### Pick Three, Keep Many

If your review strategy requires sub-agents, parallelize your work using sub-agents. Spawn the exact number of sub-agents specified by `/tmp/pr-context/review-strategy.md`, with each sub-agent approaching the task from a different angle (for example, different focus areas, heuristics, or file order). If the strategy says direct review, do not spawn sub-agents.

**How to spawn sub-agents:** Call `runSubagent` with the `agentType` and `model` specified by the workflow instructions below (defaulting to `agentType: "general-purpose"` and `model: "${{ inputs.model }}"` if none are specified). Sub-agents cannot see your conversation history, the other sub-agents' results, or any context you have gathered so far. Each prompt must be **fully self-contained** — include everything the sub-agent needs:

- The full task description and objective (restate it, don't summarize)
- All repository context, conventions, and constraints you've gathered (e.g., from `generate_agents_md`)
- Any relevant data the sub-agent needs to do its job (diffs, file contents, existing threads)
- The quality criteria and output format you expect
- The specific angle that distinguishes this sub-agent from the others

Err on the side of providing too much context rather than too little. A well-informed sub-agent with a 10,000-token prompt will produce far better results than one that has to rediscover the codebase from scratch.

**Wait for all spawned sub-agents to complete.** Do not proceed until every sub-agent you started has returned its result.

**Merge and deduplicate findings** across all sub-agents:
1. If multiple sub-agents flagged the same issue, keep the version with the strongest evidence and clearest explanation.
2. If a finding is unique to one sub-agent, include it only if it passes the quality gate on its own merits — a finding flagged by only one sub-agent deserves extra scrutiny.
3. Drop any finding that does not meet the verification criteria.

**Filter aggressively for quality.** Your job as the parent agent is to be the quality gate. Sub-agents cast a wide net; you decide what's worth keeping. For each surviving finding, verify it yourself — check that file paths exist, line numbers are accurate, the problem is real, and the finding is actionable. Discard anything vague, speculative, or already addressed. If no findings survive filtering, call `noop`.
