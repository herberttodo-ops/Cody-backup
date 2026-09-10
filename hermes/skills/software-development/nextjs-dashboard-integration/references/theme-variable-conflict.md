# Theme Variable Naming Conflict

## Problem

When integrating a new page with an existing Next.js dashboard using a global ThemeProvider, variable naming conflicts can cause TypeScript errors and incorrect dark mode behavior.

### Symptoms
- `Property 'x' does not exist on type 'Theme'` errors
- Dark mode works in sidebar but not in new page
- Build fails with TypeScript errors about theme properties

### Root Cause

The `useTheme()` hook returns an object with a `theme` property ("light" | "dark"). If you also create a local `theme` variable for styling (common pattern), TypeScript gets confused:

```tsx
const { theme } = useTheme();  // returns "light" | "dark"
const theme = {              // ERROR: Duplicate identifier
  bg: isDark ? 'bg-black' : 'bg-white',
  // ...
};
```

## Solution

Rename your local theme colors object to avoid conflict:

```tsx
const { theme } = useTheme();
const isDark = theme === "dark";

// Use different name (not 'theme')
const colors = {
  bg: isDark ? 'bg-slate-950' : 'bg-gray-50',
  textPrimary: isDark ? 'text-slate-100' : 'text-gray-900',
  // ...
};

// Usage
<div className={`${colors.bg} ${colors.textPrimary}`}>
```

## Complete Working Pattern

```tsx
"use client";

import { useTheme } from "@/components/ThemeProvider";

export default function MyPage() {
  const { theme } = useTheme();
  const isDark = theme === "dark";
  
  const colors = {
    bg: isDark ? 'bg-slate-950' : 'bg-gray-50',
    cardBg: isDark ? 'bg-slate-900' : 'bg-white',
    cardBorder: isDark ? 'border-slate-700' : 'border-gray-200',
    textPrimary: isDark ? 'text-slate-100' : 'text-gray-900',
    textSecondary: isDark ? 'text-slate-400' : 'text-gray-600',
  };
  
  return (
    <div className={`min-h-screen ${colors.bg} p-6`}>
      <h1 className={colors.textPrimary}>Title</h1>
      <p className={colors.textSecondary}>Subtitle</p>
    </div>
  );
}
```

## Prevention

1. Always check if `useTheme()` is already imported somewhere
2. Use `grep -r "const theme" app/ --include="*.tsx"` to find conflicts
3. Use semantic names like `colors`, `styles`, or `uiTheme` instead of `theme`
4. Consider using Tailwind's `dark:` prefix instead of conditional classes when possible
