## Review Calibration Examples

Use these examples to calibrate your judgment. Each pair shows a real issue and a similar-looking pattern that is NOT an issue.

### Example 1: Null/Undefined Access

**True positive — flag this:**

```js
// PR adds this handler
app.get('/user/:id', async (req, res) => {
  const user = await db.findUser(req.params.id);
  res.json({ name: user.name, email: user.email });
});
```

Why flag: `db.findUser()` can return `null` when no user matches the ID. Accessing `user.name` will throw a TypeError at runtime. No upstream guard exists — the route handler is the entry point.

**False positive — do NOT flag this:**

```ts
// PR adds this line inside an existing function
const settings = user.getSettings();
```

Why skip: Reading the full file reveals `user` is typed as `User` (not `User | null`), and the calling function only runs after `authenticateUser()` middleware which guarantees a valid user object. The null case is handled at a different layer.

### Example 2: SQL Injection

**True positive — flag this:**

```python
# PR adds this query
cursor.execute(f"SELECT * FROM orders WHERE customer_id = '{customer_id}'")
```

Why flag: String interpolation in a SQL query with user-controlled input (`customer_id` comes from the request). No parameterization or sanitization anywhere in the call chain.

**False positive — do NOT flag this:**

```python
# PR adds this query
cursor.execute(f"SELECT * FROM orders WHERE status = '{OrderStatus.PENDING.value}'")
```

Why skip: The interpolated value is a hardcoded enum constant (`OrderStatus.PENDING`), not user input. There is no injection vector.

### Example 3: Borderline — Do NOT Flag

```go
// PR adds this function
func processItems(items []Item) []Result {
    results := make([]Result, 0)
    for _, item := range items {
        for _, tag := range item.Tags {
            results = append(results, process(item, tag))
        }
    }
    return results
}
```

This looks like an O(n*m) performance concern. But without evidence that `items` or `Tags` are large in practice, this is speculative. The function processes a bounded dataset (items from a single user request). Do not flag theoretical performance issues without evidence of real-world impact.
