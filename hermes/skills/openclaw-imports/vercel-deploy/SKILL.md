---
name: vercel-deploy
description: Deploy and manage Vercel projects. Use when deploying applications to Vercel, managing environment variables, checking deployment status, viewing logs, or performing Vercel operations. Supports production and preview deployments. Practical infrastructure operations - no "AI will build your app" magic.
---

# Vercel Deployment & Management

Deploy and manage Vercel projects. No "AI will build your app" nonsense - just practical Vercel operations.

## Configuration

### Vercel Setup

**Get your token:**
1. Go to https://vercel.com/account/tokens
2. Create token (name it "OpenClaw")
3. Set in environment:

```bash
export VERCEL_TOKEN="your-token-here"
```

Or store in `.env`:
```
VERCEL_TOKEN=your-token-here
```

## Vercel Operations

### Deploy Project

```bash
# Deploy to preview
scripts/vercel_deploy.sh --project bountylock --preview

# Deploy to production
scripts/vercel_deploy.sh --project bountylock --production
```

### Manage Environment Variables

```bash
# List env vars
scripts/vercel_env.sh --project bountylock --list

# Set env var
scripts/vercel_env.sh --project bountylock --set \
  --key NEXT_PUBLIC_RPC_URL \
  --value "https://sepolia.base.org" \
  --env production

# Delete env var
scripts/vercel_env.sh --project bountylock --delete \
  --key OLD_VAR \
  --env production
```

### Check Deployment Status

```bash
# Get latest deployment
scripts/vercel_status.sh --project bountylock

# Get specific deployment
scripts/vercel_status.sh --deployment dpl_abc123
```

### View Logs

```bash
# Get deployment logs
scripts/vercel_logs.sh --deployment dpl_abc123

# Get runtime logs
scripts/vercel_logs.sh --project bountylock --function api/bounties
```

## Common Workflows

### Initial Testnet Deployment

1. **Set environment variables:**
```bash
# Contract addresses (after deploying to Sepolia)
scripts/vercel_env.sh --project bountylock --set \
  --key NEXT_PUBLIC_CONTRACT_ADDRESS \
  --value "0x..." \
  --env production

# RPC URL
scripts/vercel_env.sh --project bountylock --set \
  --key NEXT_PUBLIC_RPC_URL \
  --value "https://sepolia.base.org" \
  --env production

# Chain ID
scripts/vercel_env.sh --project bountylock --set \
  --key NEXT_PUBLIC_CHAIN_ID \
  --value "84532" \
  --env production
```

2. **Deploy:**
```bash
scripts/vercel_deploy.sh --project bountylock --production
```

3. **Check status:**
```bash
scripts/vercel_status.sh --project bountylock
```

### Update Environment Variables

```bash
# Update contract address after redeployment
scripts/vercel_env.sh --project bountylock --set \
  --key NEXT_PUBLIC_CONTRACT_ADDRESS \
  --value "0xNEW_ADDRESS" \
  --env production

# Trigger new deployment to use updated vars
scripts/vercel_deploy.sh --project bountylock --production
```

### Debug Deployment Issues

```bash
# Get latest deployment info
scripts/vercel_status.sh --project bountylock

# Get build logs
scripts/vercel_logs.sh --deployment dpl_abc123

# Check environment variables
scripts/vercel_env.sh --project bountylock --list
```

## Security Best Practices

1. **Token Scope:** Use project-scoped tokens when possible
2. **Rotation:** Rotate tokens periodically
3. **Audit:** Review deployment logs regularly
4. **Secrets:** Never commit tokens to git

## Troubleshooting

**"Authentication failed"**
- Check token is set correctly
- Verify token hasn't expired

**"Not authorized: Trying to access resource under scope"**
- The token belongs to a different team/scope than the project
- Common when project was created under personal account but token is for a team
- **Fix:** Use `npx vercel login` to authenticate with the correct scope, then deploy
- Or create a new token scoped to the specific team that owns the project
- Check which teams you have access to: `curl -s -H "Authorization: Bearer $TOKEN" https://api.vercel.com/v1/user`
- **Quick fix:** Remove stale `.vercel/` directory and re-deploy: `rm -rf .vercel/ && npx vercel --prod`
- See `references/token-scope-mismatch-fix.md` for complete diagnosis and 4 solutions

**"Project not found"**
- Verify project name matches Vercel project
- Check account has access to project
- The project ID in `.vercel/project.json` may be stale if project was recreated

**"Deployment failed"**
- Check build logs: `scripts/vercel_logs.sh --deployment dpl_xxx`
- Verify environment variables are set correctly
- Check for build errors in code

**"No Next.js version detected" (API deployment error)**
- Occurs when deploying via API without proper source files
- **Fix:** Use CLI deployment (`npx vercel --prod`) instead of API for Next.js projects
- Or ensure `package.json` with `next` dependency is included in the deployment files

**Token works for API but CLI still asks for login**
- CLI stores auth separately from API tokens
- **Fix:** Run `npx vercel login` once, or write token to `~/.vercel/auth.json`:
  ```bash
  mkdir -p ~/.vercel && echo '{"token": "___TOKEN___"}' > ~/.vercel/auth.json
  ```

## Reference Files

- **Vercel API Reference:** See [vercel-api.md](references/vercel-api.md) for complete API documentation
- **Deployment Patterns:** See [deployment-patterns.md](references/deployment-patterns.md) for common deployment workflows
- **Token Scope Mismatch:** See [token-scope-mismatch-fix.md](references/token-scope-mismatch-fix.md) when `npx vercel` fails with "Not authorized" despite valid token