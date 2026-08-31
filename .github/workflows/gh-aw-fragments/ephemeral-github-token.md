---
# Mint an Elastic OIDC ephemeral GitHub token in each token-consuming job.
# Import this fragment and add workflow_call input `github-token-policy` (string)
# plus `permissions.id-token: write` on the workflow. A non-empty value mints via
# create-token; empty keeps GITHUB_TOKEN / GH_AW_GITHUB_TOKEN. Callers that set
# github-token-policy must grant id-token: write on the job that uses the lock file.
#
# The compiler only accepts a single secrets.* chain or a single steps.*.outputs.*
# expression for github-token, so scripts/wire-ephemeral-token.py rewrites compiled
# lock files to prefer the minted step outputs before GH_AW_GITHUB_TOKEN / GITHUB_TOKEN.
jobs:
  activation:
    pre-steps:
      - name: Create ephemeral GitHub token
        id: create-token
        if: ${{ inputs.github-token-policy != '' }}
        uses: elastic/oblt-actions/github/create-token@v1
        with:
          token-policy: ${{ inputs.github-token-policy }}
  agent:
    pre-steps:
      - name: Create ephemeral GitHub token
        id: create-token
        if: ${{ inputs.github-token-policy != '' }}
        uses: elastic/oblt-actions/github/create-token@v1
        with:
          token-policy: ${{ inputs.github-token-policy }}
  safe_outputs:
    pre-steps:
      - name: Create ephemeral GitHub token
        id: create-token
        if: ${{ inputs.github-token-policy != '' }}
        uses: elastic/oblt-actions/github/create-token@v1
        with:
          token-policy: ${{ inputs.github-token-policy }}
  conclusion:
    pre-steps:
      - name: Create ephemeral GitHub token
        id: create-token
        if: ${{ inputs.github-token-policy != '' }}
        uses: elastic/oblt-actions/github/create-token@v1
        with:
          token-policy: ${{ inputs.github-token-policy }}
---
