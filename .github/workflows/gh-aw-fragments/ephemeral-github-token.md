---
# Mint an Elastic OIDC ephemeral GitHub token in each token-consuming job.
# Import this fragment and add workflow_call inputs `mint-ephemeral-token` (boolean)
# and `token-policy` (string) plus `permissions.id-token: write` on the workflow.
# Callers that set mint-ephemeral-token: true must also grant id-token: write on the
# job that uses the compiled lock workflow.
#
# The compiler only accepts a single secrets.* chain or a single steps.*.outputs.*
# expression for github-token, so scripts/wire-ephemeral-token.py rewrites compiled
# lock files to prefer the minted step outputs before GH_AW_GITHUB_TOKEN / GITHUB_TOKEN.
jobs:
  activation:
    pre-steps:
      - name: Create ephemeral GitHub token (configured policy)
        id: create-token-explicit
        if: ${{ inputs.mint-ephemeral-token && inputs.token-policy != '' }}
        uses: elastic/oblt-actions/github/create-token@v1
        with:
          token-policy: ${{ inputs.token-policy }}
      - name: Create ephemeral GitHub token (Vault auto policy)
        id: create-token-auto
        if: ${{ inputs.mint-ephemeral-token && inputs.token-policy == '' }}
        uses: elastic/oblt-actions/github/create-token@v1
  agent:
    pre-steps:
      - name: Create ephemeral GitHub token (configured policy)
        id: create-token-explicit
        if: ${{ inputs.mint-ephemeral-token && inputs.token-policy != '' }}
        uses: elastic/oblt-actions/github/create-token@v1
        with:
          token-policy: ${{ inputs.token-policy }}
      - name: Create ephemeral GitHub token (Vault auto policy)
        id: create-token-auto
        if: ${{ inputs.mint-ephemeral-token && inputs.token-policy == '' }}
        uses: elastic/oblt-actions/github/create-token@v1
  safe_outputs:
    pre-steps:
      - name: Create ephemeral GitHub token (configured policy)
        id: create-token-explicit
        if: ${{ inputs.mint-ephemeral-token && inputs.token-policy != '' }}
        uses: elastic/oblt-actions/github/create-token@v1
        with:
          token-policy: ${{ inputs.token-policy }}
      - name: Create ephemeral GitHub token (Vault auto policy)
        id: create-token-auto
        if: ${{ inputs.mint-ephemeral-token && inputs.token-policy == '' }}
        uses: elastic/oblt-actions/github/create-token@v1
  conclusion:
    pre-steps:
      - name: Create ephemeral GitHub token (configured policy)
        id: create-token-explicit
        if: ${{ inputs.mint-ephemeral-token && inputs.token-policy != '' }}
        uses: elastic/oblt-actions/github/create-token@v1
        with:
          token-policy: ${{ inputs.token-policy }}
      - name: Create ephemeral GitHub token (Vault auto policy)
        id: create-token-auto
        if: ${{ inputs.mint-ephemeral-token && inputs.token-policy == '' }}
        uses: elastic/oblt-actions/github/create-token@v1
---
