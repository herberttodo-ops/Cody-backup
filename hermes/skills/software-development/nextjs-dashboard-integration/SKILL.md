---
name: nextjs-dashboard-integration
title: Next.js Dashboard Feature Integration
description: Patterns for adding new features/sections to existing Next.js dashboard applications. Avoid custom implementations when global systems exist.
version: 1.0.0
tags: [nextjs, dashboard, react, integration, theming, navigation]
---

# Next.js Dashboard Feature Integration

## When Adding a New Section/Page to an Existing Dashboard

### Step 1: Check Existing Architecture (Critical)

**Before writing ANY code**, verify these exist:

```bash
# Check for global theme system
grep -r "ThemeProvider\|useTheme\|darkMode" app/ components/ --include="*.tsx" | head -10

# Check for navigation/sidebar
grep -r "Sidebar\|Navigation\|navItems" app/ components/ --include="*.tsx" | head -10

# Check layout structure
ls -la app/layout.tsx
```

**Common Global Systems to Reuse:**
- ThemeProvider (react context for dark/light mode)
- Sidebar/Navigation component with navItems array
- Layout wrapper with shared UI
- Global state (Zustand, Redux, Context)

### Step 2: Theming Integration Pattern

**DO NOT:**
```tsx
// BAD: Custom dark mode state
const [darkMode, setDarkMode] = useState(false);
```

**DO:**
```tsx
// GOOD: Use existing theme system
import { useTheme } from "@/components/ThemeProvider";

const { theme } = useTheme();
const isDark = theme === "dark";
```

**Theme Classes Pattern:**
```tsx
// Always use Tailwind dark: prefix
<div className="bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
```

### Step 3: Navigation Integration Pattern

**Locate the navItems array:**
```tsx
// In components/Sidebar.tsx or similar
const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/content-review", label: "Content", icon: FileText },
  // ADD YOURS HERE
  { href: "/lotsignal", label: "LotSignal", icon: Truck },
];
```

**Checklist for navigation:**
- [ ] Add to Sidebar navItems (if exists)
- [ ] Add icon import (use Lucide icons matching existing style)
- [ ] Add quick access card on homepage (if pattern exists)
- [ ] Verify active state highlighting works

### Step 4: Page Component Structure

**Standard dashboard page template:**

```tsx
// app/your-feature/page.tsx
"use client";

export default function YourFeaturePage() {
  const { theme } = useTheme?.() || { theme: "light" };
  
  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Feature Title
        </h1>
      </div>
      
      {/* Content */}
      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-5">
        {/* Your content */}
      </div>
    </div>
  );
}
```

### Step 5: Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| White text on white background | Use `dark:text-white` with `dark:bg-gray-900` |
| Custom state for existing feature | Search codebase first, reuse global state |
| No navigation to new page | Add to Sidebar.tsx navItems array |
| Inconsistent styling | Copy patterns from existing pages exactly |
| Missing dark mode support | Wrap in ThemeProvider classes |
| **Variable naming conflict** | **NEVER use `const theme` if you already have `const { theme } = useTheme()`. Rename to `colors` or `styles`** |

**Theme Variable Naming Conflict (CRITICAL):**

When using `useTheme()` from ThemeProvider, the returned `theme` is a STRING ("light" | "dark"). If you also write:

```tsx
const { theme } = useTheme();  // string: "light" | "dark"
const theme = {               // ERROR: duplicate identifier
  bg: isDark ? 'bg-black' : 'bg-white'
};
```

**Solution:** Use a different name for your colors object:

```tsx
const { theme } = useTheme();
const isDark = theme === "dark";

const colors = {              // OK: different name
  bg: isDark ? 'bg-slate-950' : 'bg-gray-50',
  textPrimary: isDark ? 'text-slate-100' : 'text-gray-900',
  // ...
};
```

See `references/theme-variable-conflict.md` for full details.

### Step 6: Verification Checklist

Before deploying:
- [ ] Page visible in sidebar navigation
- [ ] Clickable from homepage quick access (if pattern exists)
- [ ] Dark mode toggle works (if app has one)
- [ ] Text readable in both themes
- [ ] Consistent with existing page padding/spacing

## Related Skills

- vercel-deploy - For deployment after integration
- frontend-design - For component design patterns

## References

See `references/component-patterns.md` for specific component integration examples.
