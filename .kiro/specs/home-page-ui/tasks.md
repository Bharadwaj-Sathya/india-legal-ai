# Implementation Plan: Home Page UI

## Overview

Implement the Indian Legal AI Home Page from scratch: install and configure all dependencies, bootstrap the Redux store with redux-persist, set up routing and the application shell, build the three-column layout (Sidebar, MainPanel, RightPanel), and wire every interactive element to Redux state. Property-based tests validate the core reducer invariants and UI interaction contracts.

---

## Tasks

- [x] 1. Install dependencies and configure the build toolchain
  - Run `pnpm add @hookform/resolvers@^5.2.2 @radix-ui/react-slot@^1.2.4 @radix-ui/react-dropdown-menu@latest @react-oauth/google@^0.13.0 @reduxjs/toolkit@^2.11.2 @tailwindcss/vite@^4.1.17 @tanstack/react-table@^8.21.3 axios@^1.13.2 class-variance-authority@^0.7.1 clsx@^2.1.1 framer-motion@^12.23.25 lucide-react@^0.556.0 next-themes@^0.4.6 react-hook-form@^7.68.0 react-redux@^9.2.0 react-router-dom@^7.11.0 redux-persist@^6.0.0 redux-thunk@^3.1.0 tailwind-merge@^3.4.0 tailwindcss@^4.1.17 uuid@^13.0.0 zod@^4.2.1`
  - Run `pnpm add -D @types/uuid vitest @vitest/coverage-v8 @testing-library/react @testing-library/jest-dom @testing-library/user-event fast-check jsdom`
  - Update `vite.config.ts`: add `@tailwindcss/vite` plugin and `@` path alias resolving to `./src`
  - Update `tsconfig.app.json` `compilerOptions` to add `"baseUrl": "."` and `"paths": { "@/*": ["./src/*"] }`
  - Replace `src/index.css` content with `@import "tailwindcss";` followed by the `@layer base` CSS custom property block from the design (`:root` dark defaults + `.light` overrides)
  - _Requirements: 1.1, 1.2, 1.4_

- [x] 2. Create `src/lib/utils.ts` and `src/hooks/useDebounce.ts`
  - [x] 2.1 Create `src/lib/utils.ts` exporting the `cn()` helper using `clsx` + `tailwind-merge`
    - Implement exactly as specified in the design's `src/lib/utils.ts` section
    - _Requirements: 1.3, 13.5_
  - [ ]* 2.2 Write unit tests for `cn()` in `src/lib/utils.test.ts`
    - Verify class merging, deduplication of conflicting Tailwind classes, and empty-input handling
    - _Requirements: 1.3_
  - [x] 2.3 Create `src/hooks/useDebounce.ts` with the `useDebounce<T>` hook
    - Implement as specified in the design
    - _Requirements: 13.4_
  - [ ]* 2.4 Write unit tests for `useDebounce` using Vitest fake timers
    - Verify the debounced value only updates after the specified delay
    - _Requirements: 13.4_

- [x] 3. Create the Redux store, `uiSlice`, and type helpers
  - [x] 3.1 Create `src/store/slices/uiSlice.ts`
    - Define `RecentQuery` and `UIState` interfaces
    - Implement `initialState`, `setChatInput`, `addRecentQuery`, and `rotateSuggestions` actions
    - `addRecentQuery` must prepend and cap the array at 20 entries using `uuid` for IDs
    - _Requirements: 12.1, 12.2, 12.4, 12.5_
  - [ ]* 3.2 Write property test for `setChatInput` round-trip (Property 1)
    - **Property 1: setChatInput reducer round-trip**
    - Use `fc.string()` as input; assert `chatInput === dispatched text` for any string including empty
    - **Validates: Requirements 12.4**
  - [ ]* 3.3 Write property test for `addRecentQuery` prepend-and-cap invariant (Property 3)
    - **Property 3: addRecentQuery prepend and cap invariant**
    - Use `fc.array(fc.record({...}), { maxLength: 25 })` as seed state + `fc.string({minLength:1})` for new text
    - Assert length === min(n+1, 20), first element matches dispatched text, existing entries not mutated
    - **Validates: Requirements 12.5**
  - [x] 3.4 Create `src/store/store.ts`
    - Set up `configureStore` with `combineReducers`, `persistReducer`, and serializable-check middleware exception for persist actions
    - Export `store`, `persistor`, `RootState`, and `AppDispatch`
    - Persist key must be `india-legal-ai` with `storage` targeting `localStorage`
    - _Requirements: 12.1, 12.3_

- [x] 4. Bootstrap `src/main.tsx` and `src/App.tsx`
  - [x] 4.1 Rewrite `src/main.tsx`
    - Wrap the tree with `<Provider store>`, `<PersistGate loading={null}>`, `<ThemeProvider attribute="class" defaultTheme="dark" enableSystem={false}>`, and `<BrowserRouter>` in the order specified in the design
    - _Requirements: 2.1, 2.3, 2.4, 2.5_
  - [x] 4.2 Rewrite `src/App.tsx`
    - Define all seven routes as per the design route map using `<Routes>` and `<Route>`
    - Stub future pages as inline arrow components returning a `<div>` with placeholder text
    - Add catch-all `<Route path="*" element={<Navigate to="/" />} />` to handle 404s
    - _Requirements: 2.2_

- [x] 5. Checkpoint — verify build and routing
  - Ensure `pnpm build` compiles with no TypeScript or Tailwind errors. Ensure the app boots and renders at `/`. Ask the user if questions arise.

- [x] 6. Create new UI primitives: Textarea, Badge, DropdownMenu
  - [x] 6.1 Create `src/components/ui/textarea/index.tsx`
    - Implement forwarded-ref `Textarea` component using `cn()` and the design's class string
    - _Requirements: 7.1, 13.6_
  - [x] 6.2 Create `src/components/ui/badge/index.tsx`
    - Implement `Badge` using `cva` with `default`, `secondary`, `outline`, and `success` variants
    - _Requirements: 5.6, 9.2, 13.6_
  - [x] 6.3 Create `src/components/ui/dropdown-menu/index.tsx`
    - Thin Tailwind-styled wrappers over `@radix-ui/react-dropdown-menu` primitives
    - Re-export: `DropdownMenu`, `DropdownMenuTrigger`, `DropdownMenuContent`, `DropdownMenuItem`, `DropdownMenuLabel`, `DropdownMenuSeparator`
    - _Requirements: 4.7, 13.6_

- [x] 7. Replace `src/components/Sidebar.tsx`
  - [x] 7.1 Rewrite `src/components/Sidebar.tsx` with the Indian Legal AI navigation structure
    - Fixed 185 px width, `bg-[#1a1f2e]` background
    - `SidebarBrand` section: logo mark + "Indian Legal AI" title + "Law Made Simple" subtitle
    - `SidebarNav` section: six `NavItem` components with lucide-react icons and routes per the design table
    - Use `useLocation()` to apply active highlight class to the matching NavItem; exactly one item active at any time
    - `LegalResourcesSection`: "LEGAL RESOURCES" header + eight `LegalResourceLink` items + "More Acts →" link
    - `SidebarBottomCard`: "Building a more informed India" card with flag emoji and tagline
    - All links use `<Link>` from react-router-dom (no full-page reload)
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_
  - [ ]* 7.2 Write property test for sidebar active state (Property 7)
    - **Property 7: Sidebar active state reflects current route**
    - Use `fc.constantFrom('/', '/chat', '/browse-laws', '/compare-laws', '/saved', '/history')` as route input
    - Render `Sidebar` inside `MemoryRouter initialEntries={[route]}`; assert exactly one NavItem carries the active class and its `href` equals the route
    - **Validates: Requirements 3.4**

- [x] 8. Replace `src/components/Header.tsx`
  - [x] 8.1 Rewrite `src/components/Header.tsx` for Indian Legal AI
    - Search bar with placeholder "Search sections, acts, keywords..." and "Ctrl+K" shortcut hint
    - `useRef<HTMLInputElement>` + `useEffect` keydown listener that calls `searchRef.current?.focus()` on Ctrl+K
    - `ThemeToggle` button using `useTheme()`: show `Sun` icon in dark mode, `Moon` icon in light mode; clicking calls `setTheme` with the opposite value
    - `Bell` icon notification button
    - `AccountDropdown` using the new `dropdown-menu/` primitive: circular dark avatar with letter "A", "Account" label, chevron; dropdown content with placeholder account items
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_
  - [ ]* 8.2 Write unit test for Ctrl+K focus behaviour
    - Mock `searchRef.current.focus`; simulate `keydown` event with `ctrlKey: true, key: 'k'`; assert focus was called
    - _Requirements: 4.2_
  - [ ]* 8.3 Write property test for theme toggle binary behaviour (Property 8)
    - **Property 8: Theme toggle is a strict binary toggle**
    - Use `fc.constantFrom('dark', 'light')` as initial theme; render `ThemeToggle` with mocked `useTheme`
    - Single click → opposite theme; double click → original theme; result always in `{ 'dark', 'light' }`
    - **Validates: Requirements 4.4, 10.4**

- [x] 9. Create `src/components/RightPanel.tsx`
  - [x] 9.1 Implement `RightPanel` component
    - Fixed ~185 px width, dark theme background consistent with sidebar
    - "Powered by Official Sources" badge using `Badge` with `success` variant
    - Law card with book icon and "BNS • BNSS • BSA and many more..." text
    - "Recent Queries" section header with "See all" link
    - Read `recentQueries` from Redux store; fall back to the five static seed items when store is empty
    - Each `RecentQueryItem` displays query text + relative timestamp; clicking dispatches `setChatInput(text)`
    - Quote card at bottom: "A more informed citizenry..." attributed to "— Constitution of India"
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_
  - [ ]* 9.2 Write property test for RecentQuery click pre-fill (Property 6)
    - **Property 6: RecentQuery click pre-fills chatInput**
    - Use `fc.array(fc.record({id: fc.uuidV(4), text: fc.string({minLength:1}), timestamp: fc.string()}), {minLength:1, maxLength:20})` as store state
    - For each item in the generated array, render `RightPanel` with that store state; simulate click; assert `store.getState().ui.chatInput === item.text`
    - **Validates: Requirements 9.6**

- [x] 10. Create `src/pages/HomePage.tsx` with colocated section components
  - [x] 10.1 Create `HeroSection` sub-component inside `HomePage.tsx`
    - Background image using `hero.png` from `src/assets/`
    - "YOUR AI LEGAL ASSISTANT" uppercase label + H1 "Understand Indian Laws with Confidence" + subtitle text
    - Watermark text "JUSTICE LIBERTY EQUALITY FOR ALL" overlaid on the image
    - Three `Badge` components for feature badges: "Cited from official sources", "Includes latest & historical laws", "Simple explanations"
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_
  - [x] 10.2 Create `QuickActionGrid` sub-component inside `HomePage.tsx`
    - 2×2 grid using `grid grid-cols-2 gap-4`
    - Four `QuickActionCard` items with title + description per the `QUICK_ACTIONS` constant in the design
    - Each card wrapped in `motion.div` with `whileHover` animation from framer-motion
    - Clicking dispatches `setChatInput(card.title)` via Redux
    - _Requirements: 6.1, 6.2, 6.3, 6.4_
  - [ ]* 10.3 Write property test for QuickActionCard click-to-prefill (Property 4, cards)
    - **Property 4: Click-to-prefill for QuickActionCards**
    - Use `fc.constantFrom(...QUICK_ACTIONS)` as element; simulate click on rendered card; assert `store.getState().ui.chatInput === card.title`
    - **Validates: Requirements 6.3**
  - [x] 10.4 Create `ChatInput` sub-component inside `HomePage.tsx`
    - Multi-line `Textarea` with placeholder "Ask a legal question..."
    - Controlled by `chatInput` from Redux; `onChange` dispatches `setChatInput`
    - Toolbar row: paperclip "Attach file (PDF)" button, "All Laws" dropdown (using the new `dropdown-menu/` primitive), "Ask AI" submit button with `Rocket` icon and dark background
    - On submit with non-empty trimmed value: dispatch `addRecentQuery({ text })`; clear input via `setChatInput('')`
    - On submit with empty/whitespace value: show inline validation message "Please enter a question" without dispatching `addRecentQuery`; optionally animate the textarea
    - Display character counter turning red when input exceeds 2000 characters; disable submit button when over limit
    - SuggestionChips row: `CHIP_SET_A` (5 chips) + refresh icon chip; local `useState(0 | 1)` for chip set index
    - Clicking a non-refresh chip dispatches `setChatInput(chipLabel)`
    - Clicking the refresh chip toggles chip set index between 0 and 1, showing `CHIP_SET_B` when index is 1
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7_
  - [ ]* 10.5 Write property test for whitespace-only submit rejection (Property 2)
    - **Property 2: Whitespace-only input is rejected at submission**
    - Use `fc.stringOf(fc.constantFrom(' ', '\t', '\n'))` as textarea value; render `ChatInput` with that value in store; simulate "Ask AI" click; assert `recentQueries.length` unchanged
    - **Validates: Requirements 7.4**
  - [ ]* 10.6 Write property test for SuggestionChip click-to-prefill (Property 4, chips)
    - **Property 4: Click-to-prefill for SuggestionChips**
    - Use `fc.constantFrom(...CHIP_SET_A, ...CHIP_SET_B)` as chip label; render `ChatInput`; simulate chip click; assert `chatInput === chip label`
    - **Validates: Requirements 7.6**
  - [ ]* 10.7 Write property test for SuggestionChip refresh rotation (Property 5)
    - **Property 5: SuggestionChip refresh alternates between two fixed sets**
    - Use `fc.nat({max: 10})` as N; simulate N refresh clicks; assert chips match CHIP_SET_A when N is even, CHIP_SET_B when N is odd; the two sets are never identical
    - **Validates: Requirements 7.7**
  - [x] 10.8 Create `FeatureCards` sub-component inside `HomePage.tsx`
    - Three cards in `grid grid-cols-3 gap-4` using `FEATURE_CARDS` constant
    - Each card wrapped in `motion.div` with `whileHover` from framer-motion
    - Clicking dispatches `useNavigate()` to `card.route`
    - _Requirements: 8.1, 8.2, 8.3_
  - [ ]* 10.9 Write property test for FeatureCard navigation (Property 9)
    - **Property 9: FeatureCard click navigates to the card's route**
    - Use `fc.constantFrom(...FEATURE_CARDS)` as card; render `FeatureCards` inside `MemoryRouter`; simulate click; assert `navigate` was called with `card.route`
    - **Validates: Requirements 8.3**
  - [x] 10.10 Assemble `HomePage.tsx` with the full three-column layout
    - Outer shell: `flex flex-row h-screen overflow-hidden`
    - Import and place `Sidebar` (fixed left), `MainArea` wrapper (flex-1, flex-col, min-w-0), and `RightPanel` (fixed right)
    - `MainArea` contains `Header` (sticky top-0 z-10) and `MainPanel` (flex-1 overflow-y-auto)
    - `MainPanel` renders `HeroSection`, `QuickActionGrid`, `ChatInput`, and `FeatureCards` in order
    - _Requirements: 11.1, 11.2, 11.3, 11.4_

- [x] 11. Checkpoint — full page smoke test
  - Run `pnpm build` and confirm zero errors. Render `HomePage` inside the full provider tree (store + ThemeProvider + MemoryRouter) and assert sidebar, main, and aside landmarks are present. Ask the user if questions arise.

- [x] 12. Theme support wiring and `index.css` finalisation
  - [x] 12.1 Verify `next-themes` `attribute="class"` strategy applies `dark`/`light` class to `<html>`
    - Confirm Tailwind `dark:` variants activate correctly with the CSS custom properties in `index.css`
    - Update any component that needs explicit `dark:` Tailwind classes for light-mode overrides
    - _Requirements: 10.1, 10.2, 10.3, 10.4_

- [x] 13. Integration and final wiring
  - [x] 13.1 Write integration smoke test for `HomePage` full render
    - Render `HomePage` inside the complete provider tree: `<Provider store>` + `<PersistGate>` + `<ThemeProvider>` + `<MemoryRouter>`
    - Assert no thrown errors and key landmarks present (sidebar nav, main content, aside)
    - _Requirements: 2.2, 11.1_
  - [ ]* 13.2 Write redux-persist rehydration integration test
    - Use `redux-persist/lib/storage` mock to pre-populate `localStorage` with serialised state
    - Verify `store.getState().ui.recentQueries` and `chatInput` are restored correctly after second render
    - _Requirements: 2.5, 12.3_

- [x] 14. Final checkpoint — all tests pass
  - Run `pnpm vitest --run` and confirm all tests pass. Ensure `pnpm build` still produces a clean build. Ask the user if questions arise.

---

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP; the core implementation is complete without them.
- Each task references specific requirements for traceability.
- The existing `src/components/ui/` primitive library (`card/`, `button/`, `dialog/`, etc.) is preserved; only `Header.tsx` and `Sidebar.tsx` are replaced.
- The existing `src/components/ui/dropDown/` folder is left in place; the new `dropdown-menu/` is added alongside it per the design note.
- Property tests use `fast-check` with a minimum of 100 iterations; tag each test with `// Feature: home-page-ui, Property N: <title>`.
- Disable framer-motion animations in tests via `<MotionConfig reducedMotion="always">` in the test wrapper.
- framer-motion `motion.div` `whileHover` provides card hover states for `QuickActionCard` and `FeatureCard`.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["2.1", "2.3", "3.1"] },
    { "id": 1, "tasks": ["2.2", "2.4", "3.2", "3.3", "3.4"] },
    { "id": 2, "tasks": ["4.1", "4.2"] },
    { "id": 3, "tasks": ["6.1", "6.2", "6.3"] },
    { "id": 4, "tasks": ["7.1", "8.1", "9.1"] },
    { "id": 5, "tasks": ["7.2", "8.2", "8.3", "9.2"] },
    { "id": 6, "tasks": ["10.1", "10.2", "10.4", "10.8"] },
    { "id": 7, "tasks": ["10.3", "10.5", "10.6", "10.7", "10.9", "10.10"] },
    { "id": 8, "tasks": ["12.1"] },
    { "id": 9, "tasks": ["13.1", "13.2"] }
  ]
}
```
