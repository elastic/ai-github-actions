---
tools:
  playwright:
    args: ["--snapshot-mode", "none"]
steps:
  - name: Write Playwright instructions to disk
    run: |
      cat > /tmp/playwright-instructions.md << 'EOF'
      # Playwright MCP Tools

      Use Playwright MCP tools for interactive browser automation.
      Unless otherwise instructed, use the MCP tools directly rather than writing standalone Node.js scripts.

      ## Available tools

      - `browser_navigate` — go to a URL
      - `browser_click` — click an element
      - `browser_type` — type text into an input
      - `browser_snapshot` — get an accessibility tree (YAML) of the current page
      - `browser_take_screenshot` — capture a visual screenshot (PNG/JPEG)
      - `browser_run_code` — run a Playwright code snippet
      - `browser_wait_for` — wait for text to appear/disappear
      - `browser_press_key` — press a keyboard key

      ## Automatic snapshots are disabled

      `browser_click`, `browser_type`, `browser_wait_for`, and
      `browser_run_code` do NOT return page state. You choose when to
      inspect the page.

      ## Batch actions with `browser_run_code`

      When you know the UI structure (button names, input labels), batch
      multiple actions in a single `browser_run_code` call using Playwright's
      role selectors. This is much more efficient than individual tool calls:

      ```js
      async (page) => {
        await page.getByRole('button', { name: 'Settings' }).click();
        await page.getByRole('combobox', { name: 'Theme' }).selectOption('dark');
        await page.getByRole('button', { name: 'Save' }).click();
        return 'Settings saved';
      }
      ```

      **Keep return values small** — return only what you need:
      ```js
      async (page) => {
        const res = await page.request.post(url, {data});
        const json = await res.json();
        // Good: ~50 chars
        return JSON.stringify({success: json.success, errors: json.errors?.length || 0});
        // Bad: entire response body (can be 20K+ chars)
      }
      ```

      ## Discover elements with snapshots

      When you don't know what's on the page, save a snapshot to disk and
      search it:
      ```
      browser_snapshot(filename="/tmp/gh-aw/mcp-logs/page.md")
      ```
      Then grep for elements:
      ```bash
      grep 'button.*Save\|button.*Submit' /tmp/gh-aw/mcp-logs/page.md
      ```
      Use the `ref` value from grep results with `browser_click(ref="...")`.

      Only take snapshots when you need to discover unknown elements.
      If you know the button name or role, use `browser_run_code` instead.

      ## Error handling in `browser_run_code`

      `browser_run_code` blocks can fail mid-execution if a selector doesn't
      match. Keep blocks focused — if a sequence has uncertain steps, split
      it into separate `browser_run_code` calls so you can inspect and adapt
      between them.

      ## Measuring DOM properties

      For programmatic checks (e.g. element heights, contrast), use
      `browser_run_code`:

      ```javascript
      async (page) => {
        const els = await page.locator('input, button, [role="combobox"]').all();
        const results = [];
        for (const el of els.slice(0, 10)) {
          const box = await el.boundingBox();
          const text = await el.textContent();
          if (box) results.push({ h: Math.round(box.height), text: text?.trim().slice(0, 20) });
        }
        return JSON.stringify(results);
      }
      ```

      ## Handling failures

      - Do not retry the same action more than twice — the page is in a different state than expected.
      - Diagnose before moving on: save a snapshot to disk and grep it, or use `browser_take_screenshot` for a visual check.
      - Adapt (different selector, different path) or report the failure as a finding.
      - Never claim you verified something you didn't — if it failed and you skipped it, say so.
      EOF
---

## Playwright MCP Tools

Playwright MCP tools are available for interactive browser automation. Full instructions are in `/tmp/playwright-instructions.md` — read it before using any Playwright tools.
