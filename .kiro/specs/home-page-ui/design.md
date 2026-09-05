# Design Document: Home Page UI

## Overview

The Home Page UI is the primary entry point of the Indian Legal AI application. It presents a three-column desktop layout: a fixed left Sidebar for navigation, a scrollable MainPanel containing the hero section and AI interaction areas, and a fixed right panel surfacing official sources and recent queries. The page is built on React 19 + TypeScript + Vite, styled with Tailwind CSS v4, and state-managed via Redux Toolkit with redux-persist.

The existing codebase already has a working Header, Sidebar, and Layout component oriented toward a different application domain (LifeSync). This design specifies replacing those components wholesale with new implementations purpose-built for Indian Legal AI, while preserving the existing UI primitive library (`src/components/ui/`).

### Key Design Decisions

- **Tailwind CSS v4**: The `@tailwindcss/vite` plugin replaces the legacy PostCSS-based setup. This removes the need for a `tailwind.config.*` file; instead, theme customization lives inside the CSS entry point using `@theme` blocks.
- **Redux Toolkit + redux-persist**: Used only for cross-cutting UI state (chatInput, suggestions, recentQueries). Per-component ephemeral state (hover, dropdown open/close) stays in local `useState`.
- **No Radix DropdownMenu wrapper needed**: The existing `src/components/ui/dropDown/index.tsx` is a custom dropdown implementation. The design adds a `dropdown-menu/` component as a lightweight Radix-based alternative for the Header AccountDropdown, following the folder-per-component convention. The existing `dropDown/` folder is left in place.
- **framer-motion for micro-animations**: Card hover states use `motion.div` with `whileHover` rather than CSS-only transitions, per the spec requirement.
- **next-themes ThemeProvider**: Wraps the entire tree; `dark` is the default. `useTheme()` provides `theme` and `setTheme` to the ThemeToggle button.

---

## Architecture

### Application Bootstrap Sequence

```
index.html
  └── main.tsx
        ├── <Provider store={store}>        ← Redux
        │     └── <PersistGate>             ← redux-persist
        │           └── <ThemeProvider>     ← next-themes (defaultTheme="dark")
        │                 └── <BrowserRouter>
        │                       └── <App />
        └── CSS entry: index.css (@import "tailwindcss")
```

### Route Map (`src/App.tsx`)

| Path             | Component         | Description                     |
|------------------|-------------------|---------------------------------|
| `/`              | `HomePage`        | Main home page (this feature)   |
| `/chat`          | `ChatPage`        | AI chat interface (future)      |
| `/browse-laws`   | `BrowseLawsPage`  | Law browser (future)            |
| `/compare-laws`  | `CompareLawsPage` | Law comparator (future)         |
| `/saved`         | `SavedPage`       | Saved answers (future)          |
| `/history`       | `HistoryPage`     | Query history (future)          |
| `/laws/:id`      | `LawDetailPage`   | Law detail view (future)        |

Future pages are rendered as `null` or a placeholder. Routes are defined now to allow Sidebar and FeatureCard navigation links to resolve correctly.

### High-Level Component Diagram

```
HomePage (flex row, h-screen, overflow-hidden)
├── Sidebar (fixed left, w-[185px], bg-[#1a1f2e])
│   ├── SidebarBrand
│   ├── SidebarNav
│   │   └── NavItem × 6 (Home, Chat, Browse Laws, Compare Laws, Saved, History)
│   ├── LegalResourcesSection
│   │   └── LegalResourceLink × 8 + MoreActsLink
│   └── SidebarBottomCard
│
├── MainArea (flex-1, flex col, min-w-0)
│   ├── Header (sticky top-0, z-10)
│   │   ├── SearchBar (input + Ctrl+K hint)
│   │   ├── ThemeToggle
│   │   ├── NotificationBell
│   │   └── AccountDropdown
│   │
│   └── MainPanel (flex-1, overflow-y-auto)
│       ├── HeroSection
│       │   ├── hero.png (background)
│       │   ├── Label + H1 + Subtitle
│       │   ├── WatermarkText
│       │   └── FeatureBadge × 3
│       ├── QuickActionGrid (grid-cols-2, gap-4)
│       │   └── QuickActionCard × 4
│       ├── ChatInput
│       │   ├── Textarea
│       │   ├── Toolbar (AttachButton + LawsDropdown + AskAIButton)
│       │   └── SuggestionChips (× 5 + RefreshChip)
│       └── FeatureCards (grid-cols-3, gap-4)
│           └── FeatureCard × 3
│
└── RightPanel (fixed right, w-[185px])
    ├── OfficialSourcesBadge
    ├── LawCard
    ├── RecentQueriesSection
    │   └── RecentQueryItem × 5
    └── QuoteCard
```

### Data Flow

```
User types in ChatInput textarea
  → dispatches setChatInput(value) → uiSlice.chatInput

User clicks QuickActionCard
  → dispatches setChatInput(cardTitle) → textarea reflects value

User clicks SuggestionChip
  → dispatches setChatInput(chipLabel) → textarea reflects value

User clicks RecentQueryItem (RightPanel)
  → dispatches setChatInput(queryText) → textarea reflects value

User clicks "Ask AI" (non-empty)
  → dispatches addRecentQuery({ id, text, timestamp })
  → uiSlice.recentQueries prepend + cap at 20

User clicks refresh SuggestionChip
  → local useState(chipSet) toggles between CHIP_SET_A / CHIP_SET_B

User clicks ThemeToggle
  → setTheme('light' | 'dark') via useTheme()
  → next-themes updates document class → Tailwind dark: variants react

Ctrl+K keydown
  → useRef to searchInput → searchInput.current.focus()
```

---

## Components and Interfaces

### `src/main.tsx`

```tsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { Provider } from 'react-redux'
import { PersistGate } from 'redux-persist/integration/react'
import { ThemeProvider } from 'next-themes'
import { BrowserRouter } from 'react-router-dom'
import { store, persistor } from './store/store'
import App from './App'
import './index.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Provider store={store}>
      <PersistGate loading={null} persistor={persistor}>
        <ThemeProvider attribute="class" defaultTheme="dark" enableSystem={false}>
          <BrowserRouter>
            <App />
          </BrowserRouter>
        </ThemeProvider>
      </PersistGate>
    </Provider>
  </StrictMode>
)
```

### `src/App.tsx`

```tsx
import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'

// Future pages — stub components until implemented
const ChatPage = () => <div>Chat</div>
const BrowseLawsPage = () => <div>Browse Laws</div>
const CompareLawsPage = () => <div>Compare Laws</div>
const SavedPage = () => <div>Saved</div>
const HistoryPage = () => <div>History</div>
const LawDetailPage = () => <div>Law Detail</div>

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/chat" element={<ChatPage />} />
      <Route path="/browse-laws" element={<BrowseLawsPage />} />
      <Route path="/compare-laws" element={<CompareLawsPage />} />
      <Route path="/saved" element={<SavedPage />} />
      <Route path="/history" element={<HistoryPage />} />
      <Route path="/laws/:id" element={<LawDetailPage />} />
    </Routes>
  )
}
```

### `src/pages/HomePage.tsx`

The top-level page component. Renders the three-column shell; imports and composes Sidebar, MainArea (Header + MainPanel), and RightPanel.

```tsx
interface HomePageProps {} // no external props; all state from Redux

export default function HomePage(): JSX.Element
```

### `src/components/Sidebar.tsx` (replacement)

```tsx
interface NavItem {
  label: string
  icon: LucideIcon
  href: string
}

interface LegalResource {
  label: string
  href: string
}

// Sub-components (colocated or internal):
// SidebarBrand — logo mark + "Indian Legal AI" + "Law Made Simple"
// SidebarNav — renders NavItem list, uses useLocation() for active state
// LegalResourcesSection — "LEGAL RESOURCES" header + LegalResourceLink list
// SidebarBottomCard — "Building a more informed India" card

export default function Sidebar(): JSX.Element
```

Navigation items:

| Label         | Icon (lucide-react) | Route           |
|---------------|---------------------|-----------------|
| Home          | `Home`              | `/`             |
| Chat          | `MessageCircle`     | `/chat`         |
| Browse Laws   | `BookOpen`          | `/browse-laws`  |
| Compare Laws  | `GitCompare`        | `/compare-laws` |
| Saved         | `Bookmark`          | `/saved`        |
| History       | `Clock`             | `/history`      |

Legal Resources links:

| Label                         | Route                  |
|-------------------------------|------------------------|
| Constitution of India         | `/laws/constitution`   |
| BNS 2023                      | `/laws/bns-2023`       |
| BNSS 2023                     | `/laws/bnss-2023`      |
| BSA 2023                      | `/laws/bsa-2023`       |
| IPC 1860 (Historical)         | `/laws/ipc-1860`       |
| CrPC 1973 (Historical)        | `/laws/crpc-1973`      |
| Indian Evidence Act 1872      | `/laws/evidence-1872`  |
| More Acts →                   | `/browse-laws`         |

### `src/components/Header.tsx` (replacement)

```tsx
interface HeaderProps {} // no external props

// Internal hooks:
//   const searchRef = useRef<HTMLInputElement>(null)
//   useEffect — window keydown listener for Ctrl+K → searchRef.current?.focus()
//   const { theme, setTheme } = useTheme()

export default function Header(): JSX.Element
```

The AccountDropdown renders a static dark circular avatar with letter "A" and the text "Account" plus a chevron. Clicking opens a dropdown with placeholder account options.

### `src/components/RightPanel.tsx` (new)

```tsx
interface RecentQueryItemProps {
  text: string
  timestamp: string
  onClick: (text: string) => void
}

interface RightPanelProps {} // reads recentQueries from Redux store

export default function RightPanel(): JSX.Element
```

RecentQuery items from the store are displayed in order (most recent first). Clicking any item dispatches `setChatInput(text)`.

### `src/pages/HomePage.tsx` — Internal Section Components

These are colocated sub-components used only within `HomePage.tsx`. They are not placed in `src/components/` since they have no reuse outside the page.

**HeroSection**
```tsx
// No props. Static content + hero.png background.
function HeroSection(): JSX.Element
```

**QuickActionGrid**
```tsx
interface QuickActionCardData {
  title: string
  description: string
}

const QUICK_ACTIONS: QuickActionCardData[] = [
  { title: "What is Section 420?", description: "Explain IPC Section 420 and its current equivalent" },
  { title: "My rights if I am arrested", description: "Understand your legal rights and relevant sections" },
  { title: "Explain Article 21", description: "Get a simple explanation with examples" },
  { title: "Compare IPC and BNS", description: "See the corresponding sections" },
]

// Clicking a card dispatches setChatInput(card.title)
function QuickActionGrid(): JSX.Element
```

**ChatInput**
```tsx
// Reads chatInput from Redux; dispatches setChatInput on change.
// Dispatches addRecentQuery + navigates on submit.
// Local state: chipSet (0 | 1) for suggestion rotation.
function ChatInput(): JSX.Element

const CHIP_SET_A = [
  "What is Section 420?",
  "Difference between BNS and IPC?",
  "Explain Article 14",
  "Bail procedure under BNSS",
  "Rights of a consumer",
]

const CHIP_SET_B = [
  "What is Article 21?",
  "Explain POCSO Act",
  "Rights during police interrogation",
  "Consumer forum vs civil court",
  "Property rights under Hindu law",
]
```

**FeatureCards**
```tsx
interface FeatureCardData {
  title: string
  description: string
  route: string
}

const FEATURE_CARDS: FeatureCardData[] = [
  { title: "Browse Laws", description: "Explore all Acts, chapters and sections", route: "/browse-laws" },
  { title: "Compare Sections", description: "Find old to new section mappings (e.g., IPC → BNS)", route: "/compare-laws" },
  { title: "Save & Organize", description: "Save important answers for later", route: "/saved" },
]

// Clicking navigates to card.route via useNavigate()
function FeatureCards(): JSX.Element
```

### New UI Primitives

**`src/components/ui/textarea/index.tsx`**

```tsx
import * as React from "react"
import { cn } from "@/lib/utils"

export interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, ...props }, ref) => (
    <textarea
      className={cn(
        "flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50",
        className
      )}
      ref={ref}
      {...props}
    />
  )
)
Textarea.displayName = "Textarea"

export { Textarea }
```

**`src/components/ui/badge/index.tsx`**

```tsx
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground",
        secondary: "bg-secondary text-secondary-foreground",
        outline: "border border-current",
        success: "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30",
      },
    },
    defaultVariants: { variant: "default" },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />
}

export { Badge, badgeVariants }
```

**`src/components/ui/dropdown-menu/index.tsx`**

Thin wrapper over `@radix-ui/react-dropdown-menu` primitives, following the same naming convention as the existing `dropDown/` component but using the Radix primitive for proper accessibility (keyboard navigation, ARIA roles).

```tsx
// Re-exports: DropdownMenu, DropdownMenuTrigger, DropdownMenuContent,
// DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator
// all from @radix-ui/react-dropdown-menu with Tailwind styling applied
```

---

## Data Models

### Redux Store Shape

```typescript
// src/store/store.ts
import { configureStore } from '@reduxjs/toolkit'
import { persistStore, persistReducer } from 'redux-persist'
import storage from 'redux-persist/lib/storage'
import { combineReducers } from 'redux'
import uiReducer from './slices/uiSlice'

const persistConfig = {
  key: 'india-legal-ai',
  storage,
  whitelist: ['ui'],
}

const rootReducer = combineReducers({ ui: uiReducer })
const persistedReducer = persistReducer(persistConfig, rootReducer)

export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({ serializableCheck: { ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'] } }),
})

export const persistor = persistStore(store)
export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
```

### `uiSlice` State

```typescript
// src/store/slices/uiSlice.ts

export interface RecentQuery {
  id: string        // uuid v4
  text: string      // query text
  timestamp: string // ISO 8601 string
}

export interface UIState {
  chatInput: string
  suggestions: string[]       // currently active chip set (persisted)
  recentQueries: RecentQuery[] // capped at 20, prepend-on-add
}

const initialState: UIState = {
  chatInput: '',
  suggestions: [],
  recentQueries: [],
}

// Actions:
// setChatInput(text: string) → state.chatInput = text
// addRecentQuery(payload: { text: string }) → prepend { id: uuid(), text, timestamp: new Date().toISOString() }, slice to 20
// rotateSuggestions(chips: string[]) → state.suggestions = chips
```

### Theme Configuration

next-themes uses the `class` attribute strategy. When `dark` theme is active, the `<html>` element receives `class="dark"`. Tailwind v4 `dark:` variants activate accordingly.

CSS custom properties defined in `src/index.css`:

```css
@import "tailwindcss";

@layer base {
  :root {
    --background: 222 47% 8%;       /* #0f1117 */
    --foreground: 210 40% 98%;
    --card: 222 47% 11%;            /* #1a1f2e */
    --card-foreground: 210 40% 98%;
    --primary: 221 83% 53%;
    --primary-foreground: 210 40% 98%;
    --muted: 217 33% 17%;
    --muted-foreground: 215 20% 65%;
    --border: 217 33% 20%;
    --input: 217 33% 20%;
    --ring: 221 83% 53%;
  }

  .light {
    --background: 0 0% 100%;
    --foreground: 222 47% 8%;
    --card: 0 0% 98%;
    --card-foreground: 222 47% 8%;
    --muted: 210 40% 96%;
    --muted-foreground: 215 16% 47%;
    --border: 214 32% 91%;
    --input: 214 32% 91%;
  }
}
```

### TypeScript Path Aliases

`tsconfig.json` and `vite.config.ts` must both define `@/*`:

```json
// tsconfig.json (compilerOptions)
{
  "paths": { "@/*": ["./src/*"] }
}
```

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') },
  },
})
```

### `src/lib/utils.ts`

```typescript
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

### `src/hooks/useDebounce.ts`

```typescript
import { useState, useEffect } from 'react'

export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay)
    return () => clearTimeout(timer)
  }, [value, delay])

  return debouncedValue
}
```

---

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: setChatInput reducer round-trip

*For any* string `text` (including empty strings), dispatching `setChatInput(text)` to the Redux `uiSlice` reducer SHALL produce a new state where `chatInput === text` exactly, with no transformation or truncation applied.

**Validates: Requirements 12.4**

---

### Property 2: Whitespace-only input is rejected at submission

*For any* string `s` where `s.trim() === ''` (empty string, or any combination of spaces, tabs, and newlines), clicking the "Ask AI" submit button SHALL NOT dispatch `addRecentQuery`, and the `recentQueries` array in the store SHALL remain unchanged in length and contents.

**Validates: Requirements 7.4**

---

### Property 3: addRecentQuery prepend and cap invariant

*For any* initial `recentQueries` array of arbitrary length `n` (0 ≤ n ≤ 25) and any non-empty query text `t`, after dispatching `addRecentQuery({ text: t })`:
- The resulting array length SHALL be `min(n + 1, 20)`.
- The first element `[0]` SHALL have `.text === t`.
- No previously existing entries SHALL be mutated; only the oldest entries beyond index 19 are dropped.

**Validates: Requirements 12.5**

---

### Property 4: Click-to-prefill for QuickActionCards and SuggestionChips

*For any* clickable text-source UI element — either a QuickActionCard with title `t` or a SuggestionChip with label `l` (non-refresh) — clicking that element SHALL dispatch `setChatInput` with the element's text value, resulting in `store.getState().ui.chatInput` equaling that exact text string.

**Validates: Requirements 6.3, 7.6**

---

### Property 5: SuggestionChip refresh alternates between two fixed sets

*For any* initial chip display state (showing either CHIP_SET_A or CHIP_SET_B), clicking the refresh chip SHALL switch the displayed chips to the other set. Clicking refresh a second time SHALL restore the original set. The two sets SHALL never be identical and the rotation SHALL be strictly binary (no third state).

**Validates: Requirements 7.7**

---

### Property 6: RecentQuery click pre-fills chatInput

*For any* `RecentQuery` item `{ id, text, timestamp }` present in `store.getState().ui.recentQueries`, clicking the corresponding item in the RightPanel SHALL dispatch `setChatInput(text)`, resulting in `store.getState().ui.chatInput === text`.

**Validates: Requirements 9.6**

---

### Property 7: Sidebar active state reflects current route

*For any* route `r` from the set `{ '/', '/chat', '/browse-laws', '/compare-laws', '/saved', '/history' }`, rendering the Sidebar while the current location equals `r` SHALL result in exactly one NavItem carrying the active visual indicator class, and that item's `href` SHALL equal `r`. No other NavItem SHALL carry the active class.

**Validates: Requirements 3.4**

---

### Property 8: Theme toggle is a strict binary toggle

*For any* current theme `t ∈ { 'dark', 'light' }`, clicking the ThemeToggle button SHALL set the active theme to the opposite value (`dark` → `light`, `light` → `dark`). Clicking it a second time SHALL restore the theme to `t`. The theme SHALL never be set to any value outside `{ 'dark', 'light' }`.

**Validates: Requirements 4.4, 10.4**

---

### Property 9: FeatureCard click navigates to the card's route

*For any* FeatureCard from the set `{ Browse Laws → /browse-laws, Compare Sections → /compare-laws, Save & Organize → /saved }`, clicking that card SHALL invoke `navigate(card.route)` with the exact route string configured for that card. No card click SHALL navigate to a route belonging to a different card.

**Validates: Requirements 8.3**

---

## Error Handling

### Validation — ChatInput

- If `chatInput.trim() === ''` when "Ask AI" is clicked: show a shake animation on the textarea (CSS `animate-shake` or framer-motion `x` spring) and render an inline message "Please enter a question". Do not dispatch `addRecentQuery`.
- If the textarea exceeds 2000 characters: display a character counter turning red and disable the submit button.

### Persistence Failures

- If `redux-persist` cannot serialize to `localStorage` (e.g., storage full), log the error to `console.error` and continue without crashing. The `PersistGate` `loading` prop shows `null` (no loading spinner) to keep the UX clean.

### Missing Assets

- `hero.png` is bundled via Vite's static import. If the import fails at build time, TypeScript will surface the error. No runtime fallback is required.

### Routing 404

- Any unmatched route falls through the `<Routes>` without a match and renders nothing. A catch-all `<Route path="*" element={<Navigate to="/" />} />` should be added in App.tsx to redirect unknown paths to HomePage.

### Theme Hydration Flicker

- next-themes injects a blocking inline script into `<head>` (via the `ThemeProvider` `attribute="class"`) that applies the stored theme class before React hydrates. This prevents the flash-of-wrong-theme (FOWT) with no additional code needed.

---

## Testing Strategy

### Unit Tests (Vitest + React Testing Library)

Unit tests cover specific example behaviors and edge cases:

- `uiSlice` reducer: verify initial state, `setChatInput` mutation, `addRecentQuery` prepend logic, `addRecentQuery` cap at 20.
- `cn()` utility: verify correct class merging and deduplication.
- `useDebounce` hook: verify delay behavior with fake timers.
- `ChatInput` component: verify "Ask AI" button is disabled when textarea is empty; verify it dispatches on non-empty input.
- `Header` Ctrl+K: verify focus is called on the search input ref when Ctrl+K is pressed.
- `ThemeToggle`: verify `setTheme` is called with opposite value on click.

### Property-Based Tests (Vitest + fast-check)

Property tests validate universal behaviors across arbitrary inputs, with a minimum of 100 iterations per property. Each test is tagged with the design property it validates.

**Library**: `fast-check` — chosen for its TypeScript-first API and compatibility with Vitest.

Property test tag format: `// Feature: home-page-ui, Property N: <property_text>`

| Property | What fast-check generates | What is asserted |
|----------|--------------------------|-----------------|
| P1: setChatInput round-trip | `fc.string()` for `text` (including empty) | `store.getState().ui.chatInput === text` after dispatch |
| P2: Whitespace-only is invalid | `fc.stringOf(fc.constantFrom(' ', '\t', '\n'))` | `recentQueries.length` unchanged; addRecentQuery not dispatched |
| P3: addRecentQuery prepend+cap | `fc.array(fc.record({id: fc.uuidV(4), text: fc.string({minLength:1}), timestamp: fc.string()}), { maxLength: 25 })` as initial state + `fc.string({minLength:1})` for new query | length === min(n+1, 20); [0].text === dispatched text; no mutation of existing entries |
| P4: Click-to-prefill (cards + chips) | `fc.constantFrom(...QUICK_ACTIONS, ...CHIP_SET_A, ...CHIP_SET_B)` as element text | `chatInput === element.text` after simulated click |
| P5: Chip refresh rotation | Simulate N alternating refresh clicks (N generated by `fc.nat({max: 10})`) | After each click chips differ from previous set; after even number of clicks, chips match starting set |
| P6: RecentQuery pre-fills | `fc.array(fc.record({id: fc.uuidV(4), text: fc.string({minLength:1}), timestamp: fc.string()}), {minLength:1, maxLength:20})` as store state | For each item, clicking its rendered element sets chatInput === item.text |
| P7: Sidebar active state | `fc.constantFrom('/', '/chat', '/browse-laws', '/compare-laws', '/saved', '/history')` | Exactly one NavItem has active class; that item's href === generated route |
| P8: Theme toggle binary | `fc.constantFrom('dark', 'light')` as initial theme | Single click → opposite; double click → original; never outside { 'dark', 'light' } |
| P9: FeatureCard navigation | `fc.constantFrom(...FEATURE_CARDS)` | Simulated click calls navigate(card.route); no cross-card navigation |

### Integration Tests

- Full page render smoke test: render `HomePage` inside the full provider tree (store + ThemeProvider + MemoryRouter) and assert no thrown errors and key landmarks are present (sidebar, main, aside).
- redux-persist rehydration: use `redux-persist/lib/storage` mock to verify state rehydrates correctly on second render.

### Visual / Snapshot Tests

- Tailwind v4 is utility-first; snapshot tests on individual components (HeroSection, QuickActionGrid, FeatureCards) using `@testing-library/react` to catch unintended markup changes.
- framer-motion animations are disabled in tests via `import { MotionConfig } from 'framer-motion'` with `reducedMotion="always"` in the test wrapper.
