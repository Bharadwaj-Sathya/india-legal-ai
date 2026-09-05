// Feature: home-page-ui, Integration: HomePage full render
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Provider } from 'react-redux'
import { PersistGate } from 'redux-persist/integration/react'
import { ThemeProvider } from 'next-themes'
import { MemoryRouter } from 'react-router-dom'
import { MotionConfig } from 'framer-motion'
import { store, persistor } from '@/store/store'
import HomePage from './HomePage'

// Mock framer-motion to avoid animation issues in tests
// Strip framer-motion-specific props so they don't bleed into DOM elements
vi.mock('framer-motion', async () => {
  const actual = await vi.importActual<typeof import('framer-motion')>('framer-motion')
  const motionProps = new Set([
    'initial', 'animate', 'exit', 'whileHover', 'whileTap', 'whileFocus',
    'whileDrag', 'whileInView', 'transition', 'variants', 'drag',
    'dragConstraints', 'layout', 'layoutId', 'onAnimationStart',
    'onAnimationComplete', 'onUpdate',
  ])
  return {
    ...actual,
    motion: {
      div: ({ children, ...props }: Record<string, unknown>) => {
        const domProps: Record<string, unknown> = {}
        for (const key of Object.keys(props)) {
          if (!motionProps.has(key)) domProps[key] = props[key]
        }
        return <div {...(domProps as React.HTMLAttributes<HTMLDivElement>)}>{children as React.ReactNode}</div>
      },
    },
  }
})

function TestWrapper({ children }: { children: React.ReactNode }) {
  return (
    <Provider store={store}>
      <PersistGate loading={null} persistor={persistor}>
        <ThemeProvider attribute="class" defaultTheme="dark" enableSystem={false}>
          <MemoryRouter>
            <MotionConfig reducedMotion="always">
              {children}
            </MotionConfig>
          </MemoryRouter>
        </ThemeProvider>
      </PersistGate>
    </Provider>
  )
}

describe('HomePage integration smoke test', () => {
  it('renders without throwing and has key landmarks', () => {
    render(
      <TestWrapper>
        <HomePage />
      </TestWrapper>
    )

    // Sidebar navigation landmark — Sidebar uses <aside aria-label="Sidebar navigation">
    expect(screen.getByRole('complementary', { name: 'Sidebar navigation', hidden: true })).toBeTruthy()

    // Main content area
    expect(screen.getByRole('main')).toBeTruthy()

    // Right panel aside — RightPanel uses <aside aria-label="Right panel">
    expect(screen.getByRole('complementary', { name: 'Right panel', hidden: true })).toBeTruthy()

    // Key text content
    expect(screen.getByText('Indian Legal AI')).toBeTruthy()
    expect(screen.getByText(/Understand Indian Laws/i)).toBeTruthy()
    expect(screen.getByPlaceholderText('Ask a legal question...')).toBeTruthy()
  })
})
