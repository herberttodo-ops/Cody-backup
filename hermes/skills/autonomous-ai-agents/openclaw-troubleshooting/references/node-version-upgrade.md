# Node.js Version Upgrade for OpenClaw

## Context
OpenClaw requires specific Node.js versions. When the system Node is too old or too new, the gateway may fail to start or behave unpredictably.

## Quick Check
```bash
node --version
# OpenClaw 2026.8.x requires: >=22.22.3 <23, >=24.15.0 <25, or >=25.9.0 <26
```

## Installing Node.js Without Sudo

When you cannot modify system Node (no sudo access), install locally:

### Using `n` (Node version manager)
```bash
# Install n using current npm
npm install -g n

# Install and use Node 26
export N_PREFIX=$HOME/.n
mkdir -p $N_PREFIX
n 26

# Add to PATH (also add to ~/.bashrc for persistence)
export PATH="$N_PREFIX/bin:$PATH"

# Verify
node --version  # v26.8.1
```

### Manual Download (fallback)
```bash
cd /tmp
curl -O https://nodejs.org/dist/v26.8.1/node-v26.8.1-linux-x64.tar.xz
tar -xf node-v26.8.1-linux-x64.tar.xz

# Use directly
/tmp/node-v26.8.1-linux-x64/bin/node --version

# Or add to PATH
export PATH="/tmp/node-v26.8.1-linux-x64/bin:$PATH"
```

## Restarting OpenClaw After Node Change

**Important:** Changing Node version requires restarting the gateway process:

```bash
# Find running gateway
ps aux | grep openclaw | grep gateway

# Kill it
kill <PID>
sleep 3

# Start with new Node version in PATH
export PATH="$HOME/.n/bin:$PATH"
openclaw gateway

# Or use background mode properly:
openclaw gateway > /tmp/openclaw.log 2>&1 &
```

## Verification
```bash
# Check which node OpenClaw is using
ps aux | grep openclaw | grep gateway
# → Should show the path to the new Node binary

# Check version
node --version
npm --version
```
