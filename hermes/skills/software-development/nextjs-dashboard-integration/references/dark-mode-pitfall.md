# Dark Mode Implementation Pitfall: White Text on White Background

## The Issue

User reported: "For visibility I did not mean make everything larger. there was white text on white backgrounds."

**The Problem:**
When implementing dark mode, I added custom dark mode state instead of using the existing ThemeProvider. This caused:
1. Text colors not matching the theme
2. Background colors not matching the theme
3. White text appearing on white backgrounds in light mode

**The Fix:**
```tsx
// BEFORE (broken - custom state)
const [darkMode, setDarkMode] = useState(false);
<div className={darkMode ? "bg-slate-900 text-white" : "bg-white text-black"}>

// AFTER (correct - use existing ThemeProvider)
const { theme } = useTheme();
<div className="bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
```

**Lesson:** Always check for existing theme system in the app before implementing dark mode. Use Tailwind's `dark:` prefix with the app's ThemeProvider rather than custom state.

## Common Symptoms

- White text on white backgrounds (in light mode)
- Black text on black backgrounds (in dark mode)
- Toggle not working consistently across pages
- Flash of wrong color on page load

## Root Cause Analysis

The app already had `ThemeProvider` wrapping the layout in `layout.tsx`:

```tsx
<ThemeProvider>
  <div className="flex h-screen">
    <Sidebar />
    <main className="flex-1 bg-gray-50 dark:bg-gray-950">
      {children}
    </main>
  </div>
</ThemeProvider>
```

Adding independent `useState` for dark mode created a parallel system that conflicted with the global one.

## Correct Pattern

```tsx
// 1. Import the theme hook
import { useTheme } from "@/components/ThemeProvider";

// 2. Use in component
const { theme } = useTheme();

// 3. Apply classes with Tailwind dark: prefix
<div className="bg-white dark:bg-gray-900 text-gray-900 dark:text-white" />

// 4. Existing toggle in sidebar already works globally
```
