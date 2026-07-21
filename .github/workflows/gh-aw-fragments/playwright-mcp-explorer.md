---
tools:
  playwright:
    mode: cli
steps:
  - name: Write Playwright instructions to disk
    run: |
      mkdir -p /tmp/gh-aw/agent
      cat > /tmp/gh-aw/agent/playwright-instructions.md << 'EOF'
      # Playwright CLI

      Use `playwright-cli` in bash for interactive browser automation.
      Run all Playwright commands as bash subprocesses — do not use MCP browser tools.

      ## Basic usage

      ```bash
      # Navigate and take a snapshot (accessibility tree)
      playwright-cli snapshot <url>

      # Take a screenshot
      playwright-cli screenshot <url> /tmp/gh-aw/agent/screenshot.png

      # Navigate, interact, then snapshot
      playwright-cli run - << 'JS'
      const { chromium } = require('playwright');
      (async () => {
        const browser = await chromium.launch();
        const page = await browser.newPage();
        await page.goto('https://example.com');
        await page.click('button[name="Submit"]');
        console.log(await page.title());
        await browser.close();
      })();
      JS
      ```

      ## Discover page structure

      Save a snapshot to disk and search it:
      ```bash
      playwright-cli snapshot https://example.com > /tmp/gh-aw/agent/page-snapshot.txt
      grep -i 'button\|input\|link' /tmp/gh-aw/agent/page-snapshot.txt
      ```

      ## Error handling

      - Do not retry the same action more than twice.
      - If a step fails, take a screenshot to diagnose:
        `playwright-cli screenshot <url> /tmp/gh-aw/agent/debug.png`
      - Adapt (different selector, different path) or report the failure.
      - Never claim you verified something you didn't.
      EOF
---

## Playwright CLI

Playwright CLI is available for interactive browser automation. Run `playwright-cli <command>` in bash. Full instructions are in `/tmp/gh-aw/agent/playwright-instructions.md` — read it before using Playwright.
