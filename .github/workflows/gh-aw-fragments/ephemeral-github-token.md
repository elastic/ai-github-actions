---
# Mint an Elastic OIDC ephemeral GitHub token in each token-consuming job.
# Import this fragment and add workflow_call inputs `mint-ephemeral-token` (boolean)
# and `token-policy` (string) plus `permissions.id-token: write` on the workflow.
# Callers that set mint-ephemeral-token: true must pass the shared catalog TokenPolicy
# id and grant id-token: write on the job that uses the compiled lock workflow.
#
# The compiler only accepts a single secrets.* chain or a single steps.*.outputs.*
# expression for github-token, so scripts/wire-ephemeral-token.py rewrites compiled
# lock files to prefer the minted step outputs before GH_AW_GITHUB_TOKEN / GITHUB_TOKEN.
jobs:
  activation:
    pre-steps:
      - name: Require token-policy when minting ephemeral token
        if: ${{ inputs.mint-ephemeral-token && inputs.token-policy == '' }}
        run: |
          echo "::error::token-policy is required when mint-ephemeral-token is true"
          exit 1
      - name: Create ephemeral GitHub token
        id: create-token
        if: ${{ inputs.mint-ephemeral-token && inputs.token-policy != '' }}
        uses: elastic/oblt-actions/github/create-token@v1
        with:
          token-policy: ${{ inputs.token-policy }}
  agent:
    pre-steps:
      - name: Require token-policy when minting ephemeral token
        if: ${{ inputs.mint-ephemeral-token && inputs.token-policy == '' }}
        run: |
          echo "::error::token-policy is required when mint-ephemeral-token is true"
          exit 1
      - name: Create ephemeral GitHub token
        id: create-token
        if: ${{ inputs.mint-ephemeral-token && inputs.token-policy != '' }}
        uses: elastic/oblt-actions/github/create-token@v1
        with:
          token-policy: ${{ inputs.token-policy }}
  safe_outputs:
    pre-steps:
      - name: Require token-policy when minting ephemeral token
        if: ${{ inputs.mint-ephemeral-token && inputs.token-policy == '' }}
        run: |
          echo "::error::token-policy is required when mint-ephemeral-token is true"
          exit 1
      - name: Create ephemeral GitHub token
        id: create-token
        if: ${{ inputs.mint-ephemeral-token && inputs.token-policy != '' }}
        uses: elastic/oblt-actions/github/create-token@v1
        with:
          token-policy: ${{ inputs.token-policy }}
  conclusion:
    pre-steps:
      - name: Require token-policy when minting ephemeral token
        if: ${{ inputs.mint-ephemeral-token && inputs.token-policy == '' }}
        run: |
          echo "::error::token-policy is required when mint-ephemeral-token is true"
          exit 1
      - name: Create ephemeral GitHub token
        id: create-token
        if: ${{ inputs.mint-ephemeral-token && inputs.token-policy != '' }}
        uses: elastic/oblt-actions/github/create-token@v1
        with:
          token-policy: ${{ inputs.token-policy }}
---
