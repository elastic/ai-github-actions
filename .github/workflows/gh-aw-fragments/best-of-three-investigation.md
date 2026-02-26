### Best-of-Three Investigation

For your initial investigation, use multiple sub-agents to explore the codebase and gather the best possible result. Give each sub-agent a unique instruction to explore a different starting point or angle — e.g., different starting points, different approaches, or different heuristics.

Wait for all the sub-agents to complete. Do not proceed until every sub-agent has returned its result.

Evaluate the candidates by comparing evidence quality, specificity, and actionability. Prefer candidates with concrete file paths, line numbers, and verifiable evidence over general observations. If most or all sub-agents recommend `noop`, that is a strong signal to `noop`.

Select the single best candidate and proceed with it. Discard the others. If no candidate meets the quality gate, call `noop`.