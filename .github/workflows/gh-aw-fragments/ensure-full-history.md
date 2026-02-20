---
steps:
  - name: Ensure full history
    env:
      GITHUB_TOKEN: ${{ github.token }}
      SERVER_URL: ${{ github.server_url }}
      REPO_NAME: ${{ github.repository }}
    run: |
      if git rev-parse --is-shallow-repository | grep -q true; then
        SERVER_URL_STRIPPED="${SERVER_URL#https://}"
        git remote set-url origin "https://x-access-token:${GITHUB_TOKEN}@${SERVER_URL_STRIPPED}/${REPO_NAME}.git"
        git fetch --unshallow --quiet
      fi
---
