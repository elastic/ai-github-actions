---
safe-outputs:
  steps:
    - name: Create ephemeral token
      if: ${{ inputs.token-policy != '' }}
      id: create-token
      uses: elastic/oblt-actions/github/create-token@55166bdfaa06a86350bd4516af37ceae1d45b757 # v1
      with:
        token-policy: ${{ inputs.token-policy }}
  github-token: ${{ steps.create-token.outputs.token || secrets.GH_AW_GITHUB_TOKEN || secrets.GITHUB_TOKEN }}
---
