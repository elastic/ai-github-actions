---
tools:
  playwright:
steps:
  - name: Write Playwright instructions to disk
    run: |
      cat > /tmp/playwright-instructions.md << 'EOF'
      # Playwright MCP Tools

      Use Playwright MCP tools for interactive browser automation.
      Use these tools to explore the app step by step — do NOT write Node.js scripts.

      ## Available tools

      - `browser_navigate` — go to a URL
      - `browser_click` — click an element
      - `browser_type` — type text into an input
      - `browser_snapshot` — get an accessibility tree (YAML) of the current page
      - `browser_take_screenshot` — capture a screenshot
      - `browser_console_execute` — run JavaScript in the browser console

      ## Why MCP tools instead of scripts

      MCP tools are interactive: you see the page state after each action and
      decide what to do next. This is ideal for exploratory testing where you
      need to adapt based on what you find. Scripts are fire-and-forget — if
      a selector is wrong, you don't find out until the script fails.

      ## Measuring DOM properties

      For programmatic checks (e.g. element heights, contrast), use
      `browser_console_execute`:

      ```javascript
      (() => {
        const els = document.querySelectorAll('input, button, [role="combobox"], [role="button"]');
        return JSON.stringify(Array.from(els)
          .map(el => {
            const r = el.getBoundingClientRect();
            return { tag: el.tagName, h: Math.round(r.height), top: Math.round(r.top), text: el.textContent?.trim().slice(0, 20) };
          })
          .filter(el => el.top > 50 && el.top < 250));
      })()
      ```

      ## Handling failures

      - Do not retry the same action more than twice — the page is in a different state than expected.
      - Diagnose before moving on: use `browser_take_screenshot` and `browser_snapshot` to see what's on the page.
      - Adapt (different selector, different path) or report the failure as a finding.
      - Never claim you verified something you didn't — if it failed and you skipped it, say so.
      EOF
---

## Playwright MCP Tools

Playwright MCP tools are available for interactive browser automation. Full instructions are in `/tmp/playwright-instructions.md` — read it before using any Playwright tools.
