import heroImg from '@/assets/supreme_court_of_india.png'
import { useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { motion, MotionConfig } from 'framer-motion'
import { Paperclip, Send, RefreshCw, ArrowRight, ChevronDown, ShieldCheck, FileText, Lightbulb, BookOpen, Scale, GitCompare, Bookmark } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import { Textarea } from '@/components/ui/textarea'
import { setChatInput, addRecentQuery } from '@/store/slices/uiSlice'
import type { RootState } from '@/store/store'
import { cn } from '@/lib/utils'
import Sidebar from '@/components/Sidebar'
import Header from '@/components/Header'
import RightPanel from '@/components/RightPanel'

// ─── Constants ──────────────────────────────────────────────────────────────

interface QuickActionCardData {
  title: string
  description: string
  icon: LucideIcon
  iconClass: string
}

const QUICK_ACTIONS: QuickActionCardData[] = [
  { title: 'What is Section 420?', description: 'Explain IPC Section 420 and its current equivalent', icon: BookOpen, iconClass: 'bg-rose-50 text-rose-700' },
  { title: 'My rights if I am arrested', description: 'Understand your legal rights and relevant sections', icon: Scale, iconClass: 'bg-blue-50 text-blue-600' },
  { title: 'Explain Article 21', description: 'Get a simple explanation with examples', icon: FileText, iconClass: 'bg-emerald-50 text-emerald-600' },
  { title: 'Compare IPC and BNS', description: 'See the corresponding sections', icon: GitCompare, iconClass: 'bg-sky-50 text-blue-600' },
]

interface FeatureCardData {
  title: string
  description: string
  route: string
  icon: LucideIcon
  iconClass: string
}

const FEATURE_CARDS: FeatureCardData[] = [
  { title: 'Browse Laws', description: 'Explore all Acts, chapters and sections', route: '/browse-laws', icon: FileText, iconClass: 'bg-violet-50 text-violet-600' },
  { title: 'Compare Sections', description: 'Find old to new section mappings (e.g., IPC → BNS)', route: '/compare-laws', icon: GitCompare, iconClass: 'bg-amber-50 text-amber-500' },
  { title: 'Save & Organize', description: 'Save important answers for later', route: '/saved', icon: Bookmark, iconClass: 'bg-emerald-50 text-emerald-600' },
]

const CHIP_SET_A = [
  'What is Section 420?',
  'Difference between BNS and IPC?',
  'Explain Article 14',
  'Bail procedure under BNSS',
  'Rights of a consumer',
]

const CHIP_SET_B = [
  'What is Article 21?',
  'Explain POCSO Act',
  'Rights during police interrogation',
  'Consumer forum vs civil court',
  'Property rights under Hindu law',
]

// ─── HeroSection ─────────────────────────────────────────────────────────────

function HeroSection() {
  return (
    <section className="dashboard-hero relative w-full h-[320px] overflow-hidden mb-5">
      {/* Background image */}
      <img
        src={heroImg}
        alt="Supreme Court of India"
        className="hero-image absolute h-full object-cover"
      />
      <div className="hero-overlay absolute inset-0" />
      {/* Watermark */}
      <p className="hero-watermark absolute bottom-14 right-7 text-xs font-semibold leading-6 tracking-widest uppercase text-right select-none">
        JUSTICE LIBERTY EQUALITY FOR ALL
      </p>
      {/* Content */}
      <div className="relative z-10 flex h-full flex-col justify-center px-7 py-8">
        <p className="hero-eyebrow text-sm font-semibold tracking-[0.18em] uppercase mb-3">
          YOUR AI LEGAL ASSISTANT
        </p>
        <h1 className="hero-title text-4xl font-bold tracking-tight mb-3 leading-[1.15] lg:text-5xl">
          Understand Indian Laws<br />with Confidence
        </h1>
        <p className="hero-description text-lg leading-7 mb-7 max-w-2xl">
          Get clear, accurate and easy-to-understand answers from the Constitution, criminal laws, and major Indian Acts.
        </p>
        <div className="hero-features flex flex-wrap gap-7 text-sm">
          <span className="flex items-center gap-2"><ShieldCheck className="h-7 w-7 rounded-full bg-emerald-50 p-1.5 text-emerald-600" />Cited from official sources</span>
          <span className="flex items-center gap-2"><FileText className="h-7 w-7 rounded-full bg-blue-50 p-1.5 text-blue-600" />Includes latest &amp; historical laws</span>
          <span className="flex items-center gap-2"><Lightbulb className="h-7 w-7 rounded-full bg-amber-50 p-1.5 text-amber-500" />Simple explanations</span>
        </div>
      </div>
    </section>
  )
}

// ─── QuickActionGrid ──────────────────────────────────────────────────────────

function QuickActionGrid() {
  const dispatch = useDispatch()
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-3 mb-6">
      {QUICK_ACTIONS.map((card) => (
        <motion.div
          key={card.title}
          whileHover={{ scale: 1.02, borderColor: 'hsl(var(--primary))' }}
          transition={{ duration: 0.15 }}
          onClick={() => dispatch(setChatInput(card.title))}
          className="cursor-pointer min-h-[110px] rounded-xl border border-border bg-card p-4 shadow-sm hover:bg-muted/30 transition-colors"
        >
          <div className="flex items-start gap-3">
            <div className={cn('rounded-xl p-2', card.iconClass)}><card.icon className="h-5 w-5" /></div>
            <div><p className="text-sm font-medium text-foreground mb-2">{card.title}</p><p className="text-xs leading-5 text-muted-foreground">{card.description}</p></div>
          </div>
        </motion.div>
      ))}
    </div>
  )
}

// ─── ChatInput ────────────────────────────────────────────────────────────────

function ChatInput() {
  const dispatch = useDispatch()
  const chatInput = useSelector((state: RootState) => state.ui?.chatInput ?? '')
  const [chipSet, setChipSet] = useState<0 | 1>(0)
  const [validationMsg, setValidationMsg] = useState('')

  const chips = chipSet === 0 ? CHIP_SET_A : CHIP_SET_B
  const overLimit = chatInput.length > 2000

  const handleSubmit = () => {
    if (chatInput.trim() === '') {
      setValidationMsg('Please enter a question')
      return
    }
    if (overLimit) return
    dispatch(addRecentQuery({ text: chatInput.trim() }))
    dispatch(setChatInput(''))
    setValidationMsg('')
  }

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    dispatch(setChatInput(e.target.value))
    if (validationMsg) setValidationMsg('')
  }

  return (
    <div className="rounded-xl border border-border bg-card p-3 mb-6 shadow-sm">
      <Textarea
        placeholder="Ask a legal question..."
        value={chatInput}
        onChange={handleChange}
        className={cn(
          'resize-none mb-2 min-h-[104px] border-input bg-background px-3 py-3',
          overLimit && 'border-red-500 focus-visible:ring-red-500'
        )}
        rows={3}
      />
      {/* Char counter */}
      {chatInput.length > 0 && (
        <p className={cn('text-[10px] text-right mb-1', overLimit ? 'text-red-500' : 'text-muted-foreground')}>
          {chatInput.length}/2000
        </p>
      )}
      {/* Validation message */}
      {validationMsg && (
        <p className="text-xs text-red-500 mb-2">{validationMsg}</p>
      )}
      {/* Toolbar */}
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <button className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors px-2 py-1 rounded border border-border">
            <Paperclip className="h-3 w-3" />
            <span>Attach file (PDF)</span>
          </button>
          <button className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors px-2 py-1 rounded border border-border">
            <span>All Laws</span>
            <ChevronDown className="h-3 w-3" />
          </button>
        </div>
        <button
          onClick={handleSubmit}
          disabled={overLimit}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-slate-800 text-white text-sm font-medium shadow-sm hover:bg-slate-700 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <Send className="h-3.5 w-3.5" />
          Ask AI
        </button>
      </div>
      {/* Suggestion chips */}
      <p className="text-sm font-medium text-foreground mt-3 mb-2">Try asking:</p>
      <div className="flex flex-wrap gap-2">
        {chips.map((chip) => (
          <button
            key={chip}
            onClick={() => dispatch(setChatInput(chip))}
            className="text-xs px-2.5 py-1 rounded-full border border-border text-muted-foreground hover:text-foreground hover:border-primary/50 transition-colors"
          >
            {chip}
          </button>
        ))}
        <button
          onClick={() => setChipSet((prev) => (prev === 0 ? 1 : 0))}
          className="text-xs px-2 py-1 rounded-full border border-border text-muted-foreground hover:text-foreground transition-colors"
          aria-label="Refresh suggestions"
        >
          <RefreshCw className="h-3 w-3" />
        </button>
      </div>
    </div>
  )
}

// ─── FeatureCards ─────────────────────────────────────────────────────────────

function FeatureCards() {
  const navigate = useNavigate()
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-5 pb-4">
      {FEATURE_CARDS.map((card) => (
        <motion.div
          key={card.title}
          whileHover={{ scale: 1.02, borderColor: 'hsl(var(--primary))' }}
          transition={{ duration: 0.15 }}
          onClick={() => navigate(card.route)}
          className="cursor-pointer rounded-xl border border-border bg-card p-5 shadow-sm hover:bg-muted/30 transition-colors"
        >
          <div className="flex items-start gap-3">
            <div className={cn('rounded-xl p-2.5', card.iconClass)}><card.icon className="h-6 w-6" /></div>
            <div className="min-w-0 flex-1"><p className="text-base font-semibold text-foreground mb-2">{card.title}</p>
            <p className="text-xs leading-5 text-muted-foreground">{card.description}</p></div>
            <ArrowRight className="mt-3 h-5 w-5 text-slate-700 shrink-0" />
          </div>
        </motion.div>
      ))}
    </div>
  )
}

// ─── HomePage ─────────────────────────────────────────────────────────────────

export { QUICK_ACTIONS, FEATURE_CARDS, CHIP_SET_A, CHIP_SET_B }

export default function HomePage() {
  return (
    <MotionConfig reducedMotion="user">
      <div className="flex h-screen overflow-hidden bg-background">
        {/* Left sidebar */}
        <Sidebar />

        {/* Workspace: one shared header above the content and right sidebar */}
        <div className="flex-1 flex min-w-0 min-h-0 flex-col">
          {/* Sticky header spans the main workspace and right sidebar. */}
          <div className="sticky top-0 z-10">
            <Header />
          </div>
          <div className="flex min-h-0 flex-1">
            {/* Scrollable main panel */}
            <main className="scrollbar-hidden min-h-0 flex-1 overflow-y-auto bg-background p-6 xl:p-7">
              <HeroSection />
              <QuickActionGrid />
              <ChatInput />
              <FeatureCards />
            </main>

            {/* Right panel */}
            <RightPanel />
          </div>
        </div>
      </div>
    </MotionConfig>
  )
}
