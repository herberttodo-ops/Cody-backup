---
name: composio
description: "Use Composio MCP tools and CLI for 1500+ app integrations (email, social, CRM, docs, dev tools) with managed OAuth."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Composio, MCP, Integrations, OAuth, Tools]
    related_skills: [native-mcp, buffer-api]
---

# Composio — App Integration via MCP

Composio connects Hermes to 1500+ apps (Gmail, GitHub, Slack, LinkedIn, X, Notion, HubSpot, Salesforce, etc.) through managed OAuth. No manual API key juggling — Composio handles auth, rate limits, and retries.

## Two Modes of Operation

### Mode 1: MCP Tools (Preferred)
When the Composio MCP server is connected, tools appear as `mcp_composio_*` and work like native Hermes tools. Check if available:

```
tool_search(query="composio")
```

If MCP tools are present, use them directly. Example tasks:
- `mcp_composio_gmail_send_email` — send emails
- `mcp_composio_linkedin_create_post` — LinkedIn posts
- `mcp_composio_github_create_issue` — GitHub issues
- `mcp_composio_slack_send_message` — Slack messages
- `mcp_composio_notion_create_page` — Notion pages

### Mode 2: CLI Fallback (Always Available)
If MCP is not connected or tools aren't loaded, use the Composio CLI:

```bash
# Search for the right tool
composio search "send an email" --limit 5

# Link an account (one-time per toolkit)
composio link gmail

# Execute a tool
composio execute GMAIL_SEND_EMAIL -d '{ "recipient_email": "a@b.com", "subject": "Hello", "body": "World" }'
```

## Workflow

### 1. Search — Find the right tool
```bash
composio search "<task>" --limit 5
```
Returns tool slugs, schemas, and connection status.

### 2. Link — Connect the account (if not already)
```bash
composio link <toolkit>
# e.g., composio link github
```
Opens OAuth flow. For Hermes, the user may need to complete this in a browser.

### 3. Execute — Run the tool
```bash
composio execute <SLUG> -d '{ ... }'
```
Always use `--dry-run` first to validate:
```bash
composio execute GMAIL_SEND_EMAIL -d '{...}' --dry-run
```

## Common Toolkits for Andrew's Workflow

| Toolkit | Use Case | Key Tools |
|---------|----------|-----------|
| **gmail** | Email outreach, triage | `GMAIL_SEND_EMAIL`, `GMAIL_FETCH_EMAILS` |
| **linkedin** | Social posts, networking | `LINKEDIN_CREATE_POST`, `LINKEDIN_GET_PERSON` |
| **github** | Code reviews, issues | `GITHUB_CREATE_ISSUE`, `GITHUB_LIST_REPOSITORY_ISSUES` |
| **slack** | Team notifications | `SLACK_SEND_MESSAGE`, `SLACK_UPLOAD_FILE` |
| **notion** | Docs, wikis | `NOTION_CREATE_PAGE`, `NOTION_QUERY_DATABASE` |
| **hubspot** | CRM, leads | `HUBSPOT_CREATE_CONTACT`, `HUBSPOT_SEARCH_CONTACTS` |
| **salesforce** | Enterprise CRM | `SALESFORCE_CREATE_LEAD` |
| **x (twitter)** | Social posts | `TWITTER_CREATION_OF_A_POST`, `TWITTER_RECENT_SEARCH` |
| **google_calendar** | Scheduling | `GOOGLE_CALENDAR_CREATE_EVENT` |
| **google_docs** | Document creation | `GOOGLEDOCS_CREATE_DOCUMENT` |
| **stripe** | Payments | `STRIPE_CREATE_CHARGE`, `STRIPE_CREATE_INVOICE` |
| **linear** | Project management | `LINEAR_CREATE_ISSUE` |
| **typeform** | Surveys | `TYPEFORM_CREATE_FORM` |
| **airtable** | Spreadsheets/DB | `AIRTABLE_CREATE_RECORD` |
| **webflow** | CMS updates | `WEBFLOW_CREATE_ITEM` |

## Rules for Hermes

1. **Prefer MCP tools when available.** Check `tool_search("composio")` first. If tools exist, use them natively.
2. **Use CLI fallback for discovery.** `composio search` is the fastest way to find the right tool slug.
3. **Link before executing.** If `connected_toolkits` is empty for a needed toolkit, prompt the user to link.
4. **Dry-run before irreversible actions.** Email sends, posts, charges — always preview first.
5. **Batch with parallel execution.** `composio execute -p <tool1> -d {...} <tool2> -d {...}` for concurrent ops.
6. **Use Composio over browser automation.** Composio is faster, safer, and better scoped than browser-based actions.
7. **Respect user preference.** If the user insists on browser/manual, honor it.

## Composio MCP Server Config

In `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  composio:
    url: "https://connect.composio.dev/mcp"
    headers:
      x-api-key: "<your-api-key>"
    timeout: 120
    connect_timeout: 30
```

Get your API key from `~/.composio/user_data.json` after `composio login`.

## CLI Auth Check

```bash
composio whoami              # Verify login status
composio dev toolkits list   # List available toolkits
composio connections         # List connected accounts
```

## Examples

### Send a LinkedIn Post via Composio
```
# 1. Search
composio search "create linkedin post" --limit 3

# 2. Link (if not connected)
composio link linkedin

# 3. Execute
composio execute LINKEDIN_CREATE_POST -d '{ "text": "Excited to share our new product launch!" }'
```

### Send Email + Create GitHub Issue in Parallel
```
composio execute -p \
  GMAIL_SEND_EMAIL -d '{ "recipient_email": "team@example.com", "subject": "Bug report", "body": "See issue" }' \
  GITHUB_CREATE_ISSUE -d '{ "owner": "company", "repo": "app", "title": "Bug: crash on login", "body": "Details..." }'
```

### Run a multi-step script
```bash
composio run '
  const emails = await execute("GMAIL_FETCH_EMAILS", { max_results: 5 });
  const urgent = emails.data.filter(e => e.snippet.includes("urgent"));
  console.log(`Found ${urgent.length} urgent emails`);
'
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "Authorization required" on MCP | Check `x-api-key` in config matches `~/.composio/user_data.json` |
| "Not connected" on execute | Run `composio link <toolkit>` first |
| Tool not found | Run `composio search "<task>"` to find the correct slug |
| Schema validation error | Use `--get-schema` to inspect required fields |
| Rate limited | Composio handles retries; wait a few seconds |

## Links

- Dashboard: https://dashboard.composio.dev
- Docs: https://docs.composio.dev
- Hermes Setup: https://composio.dev/hermes
