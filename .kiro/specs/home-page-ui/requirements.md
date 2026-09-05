# Requirements Document

## Introduction

The Home Page UI is the primary entry point of the Indian Legal AI web application. It provides users with a visually rich, three-column layout featuring a persistent dark sidebar for navigation, a central content panel with a hero section, quick-action cards, an AI chat input area, and feature navigation cards, plus a right-hand panel surfacing official legal sources and recent query history. The page is built with React 19, TypeScript, Vite, and styled with Tailwind CSS v4. All required third-party dependencies (Radix UI primitives, Redux Toolkit, react-router-dom v7, lucide-react, framer-motion, next-themes, etc.) must be installed and configured as part of this feature.

---

## Glossary

- **HomePage**: The root page component rendered at the `/` route, composed of Sidebar, Header, MainPanel, and RightPanel.
- **Sidebar**: The fixed left navigation panel (~185 px wide) with dark background (`#1a1f2e`).
- **Header**: The top navigation bar spanning the main content area, containing a search bar, theme toggle, notification bell, and account dropdown.
- **MainPanel**: The scrollable centre content area containing the HeroSection, QuickActionGrid, ChatInput, and FeatureCards.
- **HeroSection**: The full-width banner displaying the Supreme Court background image, headline text, feature badges, and watermark.
- **QuickActionGrid**: A 2×2 card grid offering pre-populated AI query shortcuts.
- **ChatInput**: The AI question textarea with toolbar (file attach, law filter dropdown, submit button) and suggestion chips.
- **FeatureCards**: A three-column row of navigation cards at the bottom of MainPanel.
- **RightPanel**: The fixed right sidebar (~185 px wide) showing the official sources badge, law card, recent queries list, and inspirational quote card.
- **ThemeToggle**: The sun/moon icon button that switches between light and dark colour modes via next-themes.
- **AccountDropdown**: The avatar + "Account" label + chevron dropdown in the Header.
- **SuggestionChip**: A clickable text pill that pre-fills the ChatInput textarea.
- **RecentQuery**: A single entry in the RightPanel recent queries list showing query text and a relative timestamp.
- **LegalResource**: A sidebar link pointing to a specific Indian legal act or document.

---

## Requirements

### Requirement 1: Dependency Installation and Project Configuration

**User Story:** As a developer, I want all required third-party packages installed and Tailwind CSS v4 configured, so that the project builds and styles render correctly.

#### Acceptance Criteria

1. THE Project SHALL include the following production dependencies at the specified versions: `@hookform/resolvers ^5.2.2`, `@radix-ui/react-slot ^1.2.4`, `@react-oauth/google ^0.13.0`, `@reduxjs/toolkit ^2.11.2`, `@tailwindcss/vite ^4.1.17`, `@tanstack/react-table ^8.21.3`, `axios ^1.13.2`, `class-variance-authority ^0.7.1`, `clsx ^2.1.1`, `framer-motion ^12.23.25`, `lucide-react ^0.556.0`, `next-themes ^0.4.6`, `react-hook-form ^7.68.0`, `react-redux ^9.2.0`, `react-router-dom ^7.11.0`, `redux-persist ^6.0.0`, `redux-thunk ^3.1.0`, `tailwind-merge ^3.4.0`, `tailwindcss ^4.1.17`, `uuid ^13.0.0`, `zod ^4.2.1`.
2. WHEN the Vite build runs, THE Project SHALL compile without TypeScript or Tailwind CSS errors.
3. THE Project SHALL expose a `cn()` utility function in `src/lib/utils.ts` that merges Tailwind class names using `clsx` and `tailwind-merge`.
4. THE Project SHALL configure Tailwind CSS v4 via the `@tailwindcss/vite` plugin in `vite.config.ts`.

---

### Requirement 2: Application Shell and Routing

**User Story:** As a user, I want the application to load a consistent shell with navigation so that I can move between pages without full page reloads.

#### Acceptance Criteria

1. THE App SHALL define a `BrowserRouter` wrapping all routes in `src/main.tsx` or `src/App.tsx`.
2. WHEN the user navigates to `/`, THE Router SHALL render the `HomePage` component.
3. THE App SHALL wrap the component tree with a `ThemeProvider` from next-themes that defaults to the `dark` colour scheme.
4. THE App SHALL initialise a Redux store using Redux Toolkit and wrap the component tree with a `Provider`.
5. WHEN the page first loads, THE App SHALL restore any persisted Redux state from `localStorage` via redux-persist.

---

### Requirement 3: Sidebar Navigation

**User Story:** As a user, I want a persistent left sidebar so that I can navigate to different sections of the application at any time.

#### Acceptance Criteria

1. THE Sidebar SHALL render with a fixed width of 185 px and a background colour of `#1a1f2e` on all viewport sizes.
2. THE Sidebar SHALL display a logo mark, the title "Indian Legal AI", and the subtitle "Law Made Simple" at the top.
3. THE Sidebar SHALL render navigation links for: Home, Chat, Browse Laws, Compare Laws, Saved, and History, each accompanied by a relevant lucide-react icon.
4. WHEN the user is on the Home route (`/`), THE Sidebar SHALL visually highlight the Home navigation link as the active item.
5. THE Sidebar SHALL render a section header labelled "LEGAL RESOURCES" followed by the following links: Constitution of India, BNS 2023, BNSS 2023, BSA 2023, IPC 1860 (Historical), CrPC 1973 (Historical), Indian Evidence Act 1872, and a "More Acts" link with a right-arrow indicator.
6. THE Sidebar SHALL render a bottom card displaying the text "Building a more informed India" with an Indian flag emoji and the tagline "Accurate. Reliable. Accessible."
7. WHEN a LegalResource link is clicked, THE Sidebar SHALL navigate to the corresponding route without triggering a full page reload.

---

### Requirement 4: Header Navigation Bar

**User Story:** As a user, I want a top navigation bar with search, theme toggle, notifications, and account access so that I can quickly find information and manage my session.

#### Acceptance Criteria

1. THE Header SHALL render a search input with the placeholder text "Search sections, acts, keywords..." and a keyboard shortcut hint displaying "Ctrl+K".
2. WHEN the user presses `Ctrl+K`, THE Header SHALL focus the search input.
3. THE Header SHALL render a ThemeToggle icon button that displays a sun icon in dark mode and a moon icon in light mode.
4. WHEN the ThemeToggle is clicked, THE ThemeProvider SHALL switch the active colour scheme between `dark` and `light`.
5. THE Header SHALL render a notification bell icon button.
6. THE Header SHALL render an AccountDropdown containing a circular dark avatar displaying the letter "A", the label "Account", and a chevron icon.
7. WHEN the AccountDropdown trigger is clicked, THE Header SHALL display a dropdown menu with account management options.

---

### Requirement 5: Hero Section

**User Story:** As a user, I want a visually prominent hero section so that I immediately understand the purpose of the application.

#### Acceptance Criteria

1. THE HeroSection SHALL display the `hero.png` image from `src/assets/` as a background or prominently placed image showing the Supreme Court building.
2. THE HeroSection SHALL display the label "YOUR AI LEGAL ASSISTANT" in small uppercase text above the main heading.
3. THE HeroSection SHALL display the heading "Understand Indian Laws with Confidence" as the primary H1 or equivalent landmark text.
4. THE HeroSection SHALL display the subtitle "Get clear, accurate and easy-to-understand answers from the Constitution, criminal laws, and major Indian Acts."
5. THE HeroSection SHALL render a watermark-style text "JUSTICE LIBERTY EQUALITY FOR ALL" overlaid on the hero image.
6. THE HeroSection SHALL display three feature badges with icons: "Cited from official sources", "Includes latest & historical laws", and "Simple explanations".

---

### Requirement 6: Quick Action Cards

**User Story:** As a user, I want pre-built question shortcuts so that I can quickly explore common legal queries without typing.

#### Acceptance Criteria

1. THE QuickActionGrid SHALL render four cards arranged in a 2-column, 2-row grid.
2. THE QuickActionGrid SHALL display the following card titles and descriptions in order:
   - "What is Section 420?" — "Explain IPC Section 420 and its current equivalent"
   - "My rights if I am arrested" — "Understand your legal rights and relevant sections"
   - "Explain Article 21" — "Get a simple explanation with examples"
   - "Compare IPC and BNS" — "See the corresponding sections"
3. WHEN a QuickActionCard is clicked, THE ChatInput textarea SHALL be pre-filled with the card's title text.
4. WHEN a QuickActionCard is hovered, THE Card SHALL display a visual hover state (e.g., border highlight or background change) to indicate interactivity.

---

### Requirement 7: AI Chat Input Area

**User Story:** As a user, I want an AI question input area so that I can ask legal questions and receive AI-generated answers.

#### Acceptance Criteria

1. THE ChatInput SHALL render a multi-line `textarea` with the placeholder text "Ask a legal question...".
2. THE ChatInput SHALL render a bottom toolbar containing: an "Attach file (PDF)" button with a paperclip icon, an "All Laws" dropdown selector, and an "Ask AI" submit button with a rocket icon and dark background.
3. WHEN the "Ask AI" button is clicked with non-empty textarea content, THE ChatInput SHALL dispatch an action or callback representing query submission.
4. IF the "Ask AI" button is clicked with an empty textarea, THEN THE ChatInput SHALL display a validation indication without submitting.
5. THE ChatInput SHALL display a row of SuggestionChips labelled: "What is Section 420?", "Difference between BNS and IPC?", "Explain Article 14", "Bail procedure under BNSS", "Rights of a consumer", and a refresh icon chip.
6. WHEN a SuggestionChip is clicked, THE ChatInput textarea SHALL be pre-filled with the chip's label text.
7. WHEN the refresh SuggestionChip is clicked, THE ChatInput SHALL rotate through an alternative set of suggestion texts.

---

### Requirement 8: Bottom Feature Navigation Cards

**User Story:** As a user, I want bottom navigation cards so that I can discover and access the main functional areas of the application.

#### Acceptance Criteria

1. THE FeatureCards section SHALL render three cards in a single row.
2. THE FeatureCards SHALL display the following content in order:
   - Title "Browse Laws", description "Explore all Acts, chapters and sections", with a right-arrow navigation indicator.
   - Title "Compare Sections", description "Find old to new section mappings (e.g., IPC → BNS)", with a right-arrow navigation indicator.
   - Title "Save & Organize", description "Save important answers for later", with a right-arrow navigation indicator.
3. WHEN a FeatureCard is clicked, THE Router SHALL navigate to the corresponding route for that feature.

---

### Requirement 9: Right Panel — Official Sources and Recent Queries

**User Story:** As a user, I want a right-hand panel showing source information and my recent activity so that I can quickly return to prior queries and trust the data sources.

#### Acceptance Criteria

1. THE RightPanel SHALL render with a fixed width of approximately 185 px and a background consistent with the overall dark theme.
2. THE RightPanel SHALL display a "Powered by Official Sources" badge with a green or teal accent colour at the top.
3. THE RightPanel SHALL render a law card displaying a law book icon alongside the text "BNS • BNSS • BSA and many more...".
4. THE RightPanel SHALL render a "Recent Queries" section header with a "See all" link.
5. THE RightPanel SHALL display five RecentQuery items with the following texts and relative timestamps:
   - "What is Section 420?" — 2 minutes ago
   - "Explain Article 21" — 1 hour ago
   - "Difference between IPC and BNS" — 3 hours ago
   - "My rights if I am arrested" — 5 hours ago
   - "Consumer protection for online fraud" — 1 day ago
6. WHEN a RecentQuery item is clicked, THE ChatInput textarea SHALL be pre-filled with the query text.
7. THE RightPanel SHALL render a bottom quote card with a dark background displaying the quote: "A more informed citizenry is the foundation of a stronger India." attributed to "— Constitution of India".

---

### Requirement 10: Theme Support

**User Story:** As a user, I want to toggle between dark and light themes so that I can use the application comfortably in different lighting conditions.

#### Acceptance Criteria

1. THE App SHALL support both `dark` and `light` colour modes managed by the `next-themes` ThemeProvider.
2. WHEN the `dark` theme is active, THE HomePage SHALL render with dark background colours (approximately `#0f1117` to `#1a1f2e` range) and light text.
3. WHEN the `light` theme is active, THE HomePage SHALL render with light background colours and dark text for all major sections.
4. WHEN the theme is toggled, THE transition SHALL apply without a full page reload.

---

### Requirement 11: Responsive Layout Structure

**User Story:** As a user, I want the three-column layout to be accessible on standard desktop viewports so that I can use the application comfortably.

#### Acceptance Criteria

1. THE HomePage SHALL render a three-column layout on viewports ≥ 1280 px wide: Sidebar (left), MainPanel (centre, flex-1), RightPanel (right).
2. THE MainPanel SHALL be independently scrollable when its content overflows the viewport height.
3. THE Sidebar and RightPanel SHALL remain fixed/sticky and not scroll with the main content.
4. THE Header SHALL remain at the top of the MainPanel and stick to the top of the viewport on scroll.

---

### Requirement 12: Redux Store Setup

**User Story:** As a developer, I want a Redux store configured with persistence so that application state (e.g., recent queries, theme preference) survives page refreshes.

#### Acceptance Criteria

1. THE Store SHALL be created in `src/store/store.ts` using `configureStore` from Redux Toolkit.
2. THE Store SHALL include a `ui` slice in `src/store/slices/uiSlice.ts` that tracks `chatInput` (string), `suggestions` (string[]), and `recentQueries` (array of `{ id, text, timestamp }`).
3. THE Store SHALL be wrapped with `redux-persist` persisting to `localStorage` with the key `india-legal-ai`.
4. WHEN the `setChatInput` action is dispatched, THE uiSlice SHALL update the `chatInput` state.
5. WHEN the `addRecentQuery` action is dispatched with a query text, THE uiSlice SHALL prepend the new query to the `recentQueries` array and limit the array to 20 entries.

---

### Requirement 13: File and Directory Structure

**User Story:** As a developer, I want a consistent file and directory structure so that the codebase is easy to navigate and extend.

#### Acceptance Criteria

1. THE Project SHALL create and use the directory `src/pages/` for page-level components.
2. THE Project SHALL place the HomePage component at `src/pages/HomePage.tsx`.
3. THE Project SHALL create the directory `src/store/` containing `store.ts` and a `slices/` subdirectory.
4. THE Project SHALL create the directory `src/hooks/` for custom React hooks.
5. THE Project SHALL provide `src/lib/utils.ts` exporting the `cn()` utility.
6. THE Project SHALL organise reusable UI primitives under `src/components/ui/` following the existing folder-per-component pattern already present in the codebase.
