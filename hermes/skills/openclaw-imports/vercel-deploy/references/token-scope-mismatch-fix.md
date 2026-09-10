# Token Scope Mismatch Fix

## Problem
`npx vercel --prod` fails with:
```
Error: Not authorized: Trying to access resource under scope "SCOPE_NAME".
You must re-authenticate to this scope or use a token with access to this scope.
```

Even though `curl` with the same token works for API calls.

## Root Causes

1. **Token belongs to different team than project** - The token was created for team A but the project exists under team B
2. **Stale `.vercel/project.json`** - The project was previously linked to an old project ID that's now inaccessible
3. **CLI auth cache vs API token** - `npx vercel` stores auth in `~/.vercel/auth.json` separately from API tokens

## Diagnosis Steps

```bash
# Check which teams the token can access
curl -s "https://api.vercel.com/v2/teams" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Check which user the token belongs to
curl -s "https://api.vercel.com/v1/user" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Solutions (in order)

### Solution 1: Remove stale project link (Most Common Fix)

```bash
cd your-project-directory
rm -rf .vercel/
npx vercel --prod
```

This forces Vercel CLI to create a fresh project link. It will:
1. Detect the current directory as a new project
2. Prompt you to link to an existing project or create new
3. Use your current auth context (from `~/.vercel/auth.json` or browser login)

### Solution 2: Login with correct scope first

```bash
npx vercel login
# Select the team that owns the project
npx vercel --prod
```

### Solution 3: Write token to CLI auth file

```bash
mkdir -p ~/.vercel
echo '{"token": "___TOKEN___"}' > ~/.vercel/auth.json
cd your-project-directory
npx vercel --prod
```

### Solution 4: Deploy via API (Bypass CLI auth)

When all else fails, deploy using the Vercel REST API directly:

```bash
curl -X POST "https://api.vercel.com/v13/deployments" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "your-project-name",
    "files": [],
    "projectSettings": {
      "framework": "nextjs"
    }
  }'
```

Note: API deployment may fail with "No Next.js version detected" if package.json is not properly included. CLI deployment is preferred for Next.js projects.

## Prevention

1. **Use team-scoped tokens** when working with team projects
2. **Don't commit `.vercel/`** to git - add it to `.gitignore`
3. **Document which token belongs to which team** in your project README
4. **Use `vercel.json` for project config** instead of relying on CLI state

## Related
- See `deployment-patterns.md` for general deployment workflows
- See `vercel-api.md` for complete API reference
