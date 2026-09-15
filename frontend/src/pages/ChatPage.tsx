import { useState } from "react";
import { Link } from "react-router-dom";
import ReactMarkdown from "react-markdown";

import {
  Scale,
  Search,
  Bell,
  Moon,
  Paperclip,
  Send,
  Plus,
  MessageSquare,
  FileText,
  History,
  Bookmark,
  ChevronDown,
  Loader2,
} from "lucide-react";


/* ============================================================
   TYPES
============================================================ */

interface SourceDocument {
  content: string;
  act?: string | null;
  section?: string | null;
  chapter?: string | null;
  category?: string | null;
  source_file?: string | null;
  page?: number | null;
  chunk_id?: number | null;
}

interface RAGResponse {
  query: string;
  answer: string;
  sources: SourceDocument[];
}

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: SourceDocument[];
}


/* ============================================================
   API CONFIGURATION
============================================================ */

const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  "http://localhost:8000";


/* ============================================================
   CHAT PAGE
============================================================ */

export default function Chat() {

  /* ----------------------------------------------------------
     STATE
  ---------------------------------------------------------- */

  const [message, setMessage] = useState("");

  const [messages, setMessages] = useState<ChatMessage[]>(
    []
  );

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");


  /* ==========================================================
     SEND QUERY TO BACKEND
  ========================================================== */

  const handleSend = async () => {

    const query = message.trim();

    // Don't send empty messages
    if (!query) {
      return;
    }

    // Don't send another request while one is running
    if (loading) {
      return;
    }

    console.log(
      "================================================"
    );

    console.log(
      "Sending query to backend:"
    );

    console.log(query);

    console.log(
      "API:",
      `${API_BASE_URL}/api/v1/rag/query`
    );

    console.log(
      "================================================"
    );


    // Clear previous error
    setError("");


    // Add user message to UI
    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: query,
      },
    ]);


    // Clear input
    setMessage("");

    // Show loading
    setLoading(true);


    try {

      /* ------------------------------------------------------
         API REQUEST
      ------------------------------------------------------ */

      const response = await fetch(
        `${API_BASE_URL}/api/v1/rag/query`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
          },

          body: JSON.stringify({
            query: query,

            // Number of documents to retrieve
            k: 5,

            // IMPORTANT:
            // null means search across all indexed Acts.
            // Do NOT force crpc_1973 for every question.
            act: null,
          }),
        }
      );


      console.log(
        "Backend HTTP status:",
        response.status
      );


      /* ------------------------------------------------------
         HANDLE HTTP ERROR
      ------------------------------------------------------ */

      if (!response.ok) {

        let errorMessage =
          `Backend returned HTTP ${response.status}`;

        try {

          const errorData =
            await response.json();

          if (errorData?.detail) {

            errorMessage =
              typeof errorData.detail === "string"
                ? errorData.detail
                : JSON.stringify(
                    errorData.detail
                  );
          }

        } catch {
          // Backend did not return JSON
        }

        throw new Error(
          errorMessage
        );
      }


      /* ------------------------------------------------------
         PARSE RESPONSE
      ------------------------------------------------------ */

      const data: RAGResponse =
        await response.json();


      console.log(
        "Backend response:",
        data
      );


      /* ------------------------------------------------------
         VALIDATE ANSWER
      ------------------------------------------------------ */

      if (
        !data ||
        typeof data.answer !== "string"
      ) {

        throw new Error(
          "Backend returned an invalid RAG response."
        );
      }


      /* ------------------------------------------------------
         ADD AI RESPONSE
      ------------------------------------------------------ */

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",

          content: data.answer,

          sources:
            Array.isArray(data.sources)
              ? data.sources
              : [],
        },
      ]);


    } catch (err) {

      console.error(
        "RAG request failed:",
        err
      );


      const errorMessage =
        err instanceof Error
          ? err.message
          : "Unable to connect to the backend.";


      setError(
        errorMessage
      );


    } finally {

      setLoading(false);
    }
  };


  /* ==========================================================
     ENTER KEY
  ========================================================== */

  const handleKeyDown = (
    event: React.KeyboardEvent<HTMLTextAreaElement>
  ) => {

    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {

      event.preventDefault();

      handleSend();
    }
  };


  /* ==========================================================
     NEW CHAT
  ========================================================== */

  const handleNewChat = () => {

    setMessages([]);

    setMessage("");

    setError("");

    setLoading(false);
  };


  /* ==========================================================
     SUGGESTION
  ========================================================== */

  const handleSuggestion = (
    question: string
  ) => {

    setMessage(question);
  };


  /* ==========================================================
     RENDER
  ========================================================== */

  return (

    <div className="flex h-screen overflow-hidden bg-[#f7f9fc] text-slate-800">


      {/* =====================================================
          LEFT SIDEBAR
      ====================================================== */}

      <aside className="flex w-[215px] shrink-0 flex-col bg-[#12263a] text-white">


        {/* ---------------------------------------------------
            LOGO
        ---------------------------------------------------- */}

        <div className="flex h-[82px] items-center gap-3 px-5">

          <Scale
            size={30}
            strokeWidth={1.5}
            className="text-[#f5df9b]"
          />

          <div>

            <h1 className="text-[17px] font-semibold">
              Indian Legal AI
            </h1>

            <p className="mt-1 text-[11px] text-slate-300">
              Law Made Simple
            </p>

          </div>

        </div>


        {/* ---------------------------------------------------
            NAVIGATION
        ---------------------------------------------------- */}

        <nav className="px-2">


          <SidebarItem
            icon={<Search size={17} />}
            label="Home"
            href="/"
          />


          <SidebarItem
            icon={<MessageSquare size={17} />}
            label="Chat"
            href="/chat"
            active
          />


          <SidebarItem
            icon={<FileText size={17} />}
            label="Browse Laws"
            href="/browse-laws"
          />


          <SidebarItem
            icon={<Scale size={17} />}
            label="Compare Laws"
            href="/compare-laws"
          />


          <SidebarItem
            icon={<Bookmark size={17} />}
            label="Saved"
            href="/saved"
          />


          <SidebarItem
            icon={<History size={17} />}
            label="History"
            href="/history"
          />

        </nav>


        {/* ---------------------------------------------------
            SIDEBAR BOTTOM
        ---------------------------------------------------- */}

        <div className="mt-auto p-3">

          <div className="rounded-xl border border-slate-600/40 bg-[#193149] p-4">

            <p className="text-[13px] font-medium">
              Building a more
            </p>

            <p className="text-[13px] font-medium">
              informed India
            </p>

            <div className="mt-3 flex items-center gap-2 text-[10px] text-slate-300">

              <span>
                🇮🇳
              </span>

              <span>
                Accurate. Reliable. Accessible.
              </span>

            </div>

          </div>

        </div>

      </aside>


      {/* =====================================================
          MAIN
      ====================================================== */}

      <main className="flex min-w-0 flex-1 flex-col">


        {/* ===================================================
            TOP HEADER
        ==================================================== */}

        <header className="flex h-[70px] shrink-0 items-center border-b border-slate-200 bg-white px-8">


          {/* SEARCH */}

          <div className="relative w-[680px] max-w-[65%]">

            <Search
              size={18}
              className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500"
            />

            <input
              type="text"
              placeholder="Search sections, acts, keywords..."
              className="h-[40px] w-full rounded-lg border border-slate-200 bg-[#fafbfd] pl-11 pr-16 text-[12px] outline-none transition focus:border-slate-400"
            />

            <span className="absolute right-3 top-1/2 -translate-y-1/2 rounded border border-slate-200 bg-white px-2 py-1 text-[10px] text-slate-500">
              Ctrl+K
            </span>

          </div>


          {/* HEADER ACTIONS */}

          <div className="ml-auto flex items-center gap-5">


            <button
              className="text-slate-600 transition hover:text-slate-900"
              title="Dark mode"
            >
              <Moon size={18} />
            </button>


            <button
              className="text-slate-600 transition hover:text-slate-900"
              title="Notifications"
            >
              <Bell size={18} />
            </button>


            <button className="flex items-center gap-2">

              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-[#102238] text-[13px] text-white">
                A
              </div>

              <span className="text-[12px] font-medium">
                Account
              </span>

              <ChevronDown
                size={13}
                className="text-slate-500"
              />

            </button>

          </div>

        </header>


        {/* ===================================================
            CHAT AREA
        ==================================================== */}

        <div className="flex min-h-0 flex-1">


          {/* =================================================
              CHAT COLUMN
          ================================================== */}

          <section className="flex min-w-0 flex-1 flex-col">


            {/* =================================================
                CHAT HEADER

                Heading LEFT
                New Chat RIGHT
            ================================================== */}

            <div className="shrink-0 border-b border-slate-200 bg-white px-8 py-5">

              <div className="flex items-center">


                {/* LEFT */}

                <div className="flex items-center gap-3">

                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#eef4fb]">

                    <Scale
                      size={21}
                      className="text-[#17304a]"
                    />

                  </div>


                  <div>

                    <h2 className="text-[19px] font-semibold text-[#13283d]">
                      Legal AI Assistant
                    </h2>

                    <p className="mt-1 text-[11px] text-slate-500">
                      Ask questions about Indian laws and legal provisions
                    </p>

                  </div>

                </div>


                {/* RIGHT */}

                <button
                  onClick={handleNewChat}
                  className="ml-auto flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-[12px] font-medium text-slate-700 shadow-sm transition hover:bg-slate-50"
                >

                  <Plus size={15} />

                  New Chat

                </button>

              </div>

            </div>


            {/* =================================================
                MESSAGE AREA
            ================================================== */}

            <div className="min-h-0 flex-1 overflow-y-auto px-6 py-7">


              <div className="mx-auto max-w-[900px]">


                {/* =================================================
                    EMPTY STATE
                ================================================== */}

                {messages.length === 0 && !loading && (

                  <div className="flex min-h-[400px] flex-col items-center justify-center text-center">


                    <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-[#eaf1f8]">

                      <MessageSquare
                        size={27}
                        className="text-[#17304a]"
                      />

                    </div>


                    <h2 className="text-[24px] font-semibold text-[#13283d]">
                      How can I help you?
                    </h2>


                    <p className="mt-3 max-w-[560px] text-[13px] leading-6 text-slate-500">
                      Ask me about Indian laws, sections, legal procedures,
                      rights, or compare provisions across different Acts.
                    </p>


                    {/* SUGGESTIONS */}

                    <div className="mt-7 grid w-full max-w-[700px] grid-cols-2 gap-3">


                      <Suggestion
                        title="What is Section 420?"
                        description="Understand cheating under IPC and its equivalent."
                        onClick={() =>
                          handleSuggestion(
                            "What is Section 420?"
                          )
                        }
                      />


                      <Suggestion
                        title="My rights if I am arrested"
                        description="Understand your legal rights after arrest."
                        onClick={() =>
                          handleSuggestion(
                            "What are my rights if I am arrested?"
                          )
                        }
                      />


                      <Suggestion
                        title="Explain Article 21"
                        description="Understand the right to life and personal liberty."
                        onClick={() =>
                          handleSuggestion(
                            "Explain Article 21"
                          )
                        }
                      />


                      <Suggestion
                        title="Compare IPC and BNS"
                        description="Find corresponding sections between the Acts."
                        onClick={() =>
                          handleSuggestion(
                            "Compare IPC and BNS"
                          )
                        }
                      />

                    </div>

                  </div>

                )}


                {/* =================================================
                    CHAT MESSAGES
                ================================================== */}

                <div className="space-y-5">


                  {messages.map(
                    (chatMessage, index) => (

                      <div
                        key={index}
                        className={
                          chatMessage.role === "user"
                            ? "flex justify-end"
                            : "flex justify-start"
                        }
                      >


                        {/* USER MESSAGE */}

                        {chatMessage.role === "user" ? (

                          <div className="max-w-[75%] rounded-2xl rounded-br-md bg-[#12263a] px-5 py-3 text-[13px] leading-6 text-white shadow-sm">

                            {chatMessage.content}

                          </div>

                        ) : (


                          /* AI MESSAGE */

                          <div className="w-full max-w-[850px]">

                            <div className="rounded-2xl rounded-bl-md border border-slate-200 bg-white p-6 shadow-sm">


                              {/* AI HEADER */}

                              <div className="mb-4 flex items-center gap-3">

                                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#eaf1f8]">

                                  <Scale
                                    size={18}
                                    className="text-[#17304a]"
                                  />

                                </div>


                                <div>

                                  <p className="text-[13px] font-semibold text-[#13283d]">
                                    Indian Legal AI
                                  </p>

                                  <p className="text-[10px] text-slate-400">
                                    Based on retrieved legal sources
                                  </p>

                                </div>

                              </div>


                              {/* MARKDOWN ANSWER */}

                              <div className="legal-markdown text-[14px] leading-7 text-slate-700">

                                <ReactMarkdown
                                  components={{

                                    h1: ({ children }) => (
                                      <h1 className="mb-4 text-xl font-bold text-[#13283d]">
                                        {children}
                                      </h1>
                                    ),

                                    h2: ({ children }) => (
                                      <h2 className="mb-3 mt-5 text-lg font-semibold text-[#13283d]">
                                        {children}
                                      </h2>
                                    ),

                                    h3: ({ children }) => (
                                      <h3 className="mb-2 mt-4 text-base font-semibold text-[#13283d]">
                                        {children}
                                      </h3>
                                    ),

                                    p: ({ children }) => (
                                      <p className="mb-3">
                                        {children}
                                      </p>
                                    ),

                                    ul: ({ children }) => (
                                      <ul className="mb-4 ml-5 list-disc space-y-2">
                                        {children}
                                      </ul>
                                    ),

                                    ol: ({ children }) => (
                                      <ol className="mb-4 ml-5 list-decimal space-y-2">
                                        {children}
                                      </ol>
                                    ),

                                    li: ({ children }) => (
                                      <li className="pl-1">
                                        {children}
                                      </li>
                                    ),

                                    strong: ({ children }) => (
                                      <strong className="font-semibold text-[#13283d]">
                                        {children}
                                      </strong>
                                    ),

                                    blockquote: ({ children }) => (
                                      <blockquote className="my-4 border-l-4 border-slate-300 bg-slate-50 px-4 py-3 text-slate-600">
                                        {children}
                                      </blockquote>
                                    ),

                                    code: ({ children }) => (
                                      <code className="rounded bg-slate-100 px-1.5 py-0.5 text-[12px]">
                                        {children}
                                      </code>
                                    ),

                                  }}
                                >
                                  {chatMessage.content}
                                </ReactMarkdown>

                              </div>


                              {/* =================================================
                                  SOURCES
                              ================================================== */}

                              {chatMessage.sources &&
                                chatMessage.sources.length > 0 && (

                                  <div className="mt-6 border-t border-slate-200 pt-5">


                                    <h3 className="mb-3 flex items-center gap-2 text-[13px] font-semibold text-slate-700">

                                      <FileText
                                        size={15}
                                      />

                                      Retrieved Sources

                                    </h3>


                                    <div className="space-y-2">


                                      {chatMessage.sources.map(
                                        (
                                          source,
                                          sourceIndex
                                        ) => (

                                          <details
                                            key={sourceIndex}
                                            className="rounded-lg border border-slate-200 bg-slate-50"
                                          >


                                            <summary className="cursor-pointer px-4 py-3 text-[12px] font-medium text-slate-700">

                                              <span>
                                                Section{" "}
                                                {source.section ||
                                                  "Unknown"}
                                              </span>


                                              {source.act && (

                                                <span className="ml-2 text-slate-400">
                                                  ·{" "}
                                                  {source.act}
                                                </span>

                                              )}

                                            </summary>


                                            <div className="border-t border-slate-200 px-4 py-4">


                                              {source.chapter && (

                                                <p className="mb-2 text-[11px] text-slate-400">
                                                  Chapter:{" "}
                                                  {source.chapter}
                                                </p>

                                              )}


                                              <p className="whitespace-pre-wrap text-[12px] leading-6 text-slate-600">
                                                {source.content}
                                              </p>


                                              {source.source_file && (

                                                <p className="mt-3 text-[10px] text-slate-400">

                                                  Source:{" "}
                                                  {source.source_file}

                                                  {source.page !==
                                                    null &&
                                                    source.page !==
                                                      undefined &&
                                                    ` · Page ${source.page}`}

                                                </p>

                                              )}

                                            </div>

                                          </details>

                                        )
                                      )}

                                    </div>

                                  </div>

                                )}

                            </div>

                          </div>

                        )}

                      </div>

                    )
                  )}


                  {/* =================================================
                      LOADING
                  ================================================== */}

                  {loading && (

                    <div className="flex justify-start">

                      <div className="rounded-2xl border border-slate-200 bg-white px-6 py-5 shadow-sm">

                        <div className="flex items-center gap-3">

                          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#eaf1f8]">

                            <Scale
                              size={18}
                              className="text-[#17304a]"
                            />

                          </div>


                          <div>

                            <p className="text-[13px] font-semibold text-slate-700">
                              Indian Legal AI
                            </p>


                            <div className="mt-2 flex items-center gap-2 text-[11px] text-slate-400">

                              <Loader2
                                size={13}
                                className="animate-spin"
                              />

                              Searching legal sources...

                            </div>

                          </div>

                        </div>

                      </div>

                    </div>

                  )}

                </div>


                {/* =================================================
                    ERROR
                ================================================== */}

                {error && (

                  <div className="mt-5 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-[12px] leading-5 text-red-700">

                    <strong>
                      Request failed:
                    </strong>{" "}

                    {error}

                  </div>

                )}

              </div>

            </div>


            {/* =================================================
                INPUT
            ================================================== */}

            <div className="shrink-0 border-t border-slate-200 bg-white px-6 py-5">


              <div className="mx-auto max-w-[900px]">


                <div className="rounded-xl border border-slate-300 bg-white shadow-sm">


                  <textarea
                    value={message}
                    onChange={(event) =>
                      setMessage(
                        event.target.value
                      )
                    }
                    onKeyDown={handleKeyDown}
                    placeholder="Ask a legal question..."
                    rows={3}
                    disabled={loading}
                    className="w-full resize-none rounded-t-xl px-4 py-4 text-[13px] outline-none placeholder:text-slate-400 disabled:bg-slate-50"
                  />


                  <div className="flex items-center justify-between border-t border-slate-100 px-3 py-2">


                    <button
                      type="button"
                      className="flex items-center gap-2 rounded-lg px-3 py-2 text-[11px] text-slate-500 transition hover:bg-slate-50"
                    >

                      <Paperclip size={14} />

                      Attach PDF

                    </button>


                    <button
                      type="button"
                      onClick={handleSend}
                      disabled={
                        !message.trim() ||
                        loading
                      }
                      className="flex items-center gap-2 rounded-lg bg-[#12263a] px-4 py-2 text-[11px] font-medium text-white transition hover:bg-[#19354e] disabled:cursor-not-allowed disabled:opacity-40"
                    >

                      {loading ? (

                        <Loader2
                          size={14}
                          className="animate-spin"
                        />

                      ) : (

                        <Send size={14} />

                      )}

                      {loading
                        ? "Thinking..."
                        : "Ask AI"}

                    </button>

                  </div>

                </div>


                <p className="mt-3 text-center text-[10px] text-slate-400">
                  AI-generated legal information may not constitute legal advice.
                  Verify important matters with official sources or a qualified lawyer.
                </p>

              </div>

            </div>

          </section>


          {/* =================================================
              RIGHT SIDEBAR
          ================================================== */}

          <aside className="hidden w-[270px] shrink-0 border-l border-slate-200 bg-white p-4 xl:block">


            {/* OFFICIAL SOURCES */}

            <div className="rounded-xl border border-slate-200 p-4">

              <div className="mb-4 flex items-center gap-2 rounded-lg bg-[#e1f7ef] px-3 py-2 text-[10px] font-semibold text-[#27956b]">

                <span>
                  ●
                </span>

                Powered by Official Sources

              </div>


              <div className="flex items-start gap-3">

                <Scale
                  size={19}
                  className="mt-1 text-slate-700"
                />

                <div>

                  <p className="text-[12px] font-semibold">
                    Constitution of India
                  </p>

                  <p className="mt-1 text-[10px] leading-5 text-slate-500">
                    BNS · BNSS · BSA and many more...
                  </p>

                </div>

              </div>

            </div>


            {/* RECENT QUERIES */}

            <div className="mt-4 rounded-xl border border-slate-200 p-4">

              <div className="mb-2 flex items-center justify-between">

                <h3 className="text-[13px] font-semibold">
                  Recent Queries
                </h3>

                <button className="text-[10px] text-slate-500 hover:text-slate-800">
                  See all
                </button>

              </div>


              <RecentQuery text="Explain Article 21" />

              <RecentQuery text="What is Section 420?" />

              <RecentQuery text="Difference between IPC and BNS" />

              <RecentQuery text="My rights if I am arrested" />

            </div>


            {/* QUOTE */}

            <div className="mt-4 rounded-xl border border-slate-200 bg-[#fafbfd] p-4">

              <div className="text-2xl text-slate-300">
                "
              </div>

              <p className="mt-1 text-[11px] italic leading-5 text-slate-500">
                A more informed citizenry is the foundation of a stronger India.
              </p>

              <p className="mt-3 text-right text-[10px] font-medium text-slate-600">
                — Constitution of India
              </p>

            </div>

          </aside>

        </div>

      </main>

    </div>
  );
}


/* ============================================================
   SIDEBAR ITEM
============================================================ */

function SidebarItem({
  icon,
  label,
  href,
  active = false,
}: {
  icon: React.ReactNode;
  label: string;
  href: string;
  active?: boolean;
}) {

  return (

    <Link
      to={href}
      className={`mb-1 flex h-[41px] items-center gap-3 rounded-lg px-4 text-[12px] transition ${
        active
          ? "bg-[#30455b] text-white"
          : "text-slate-300 hover:bg-[#1c344b] hover:text-white"
      }`}
    >

      {icon}

      <span>
        {label}
      </span>

    </Link>
  );
}


/* ============================================================
   SUGGESTION CARD
============================================================ */

function Suggestion({
  title,
  description,
  onClick,
}: {
  title: string;
  description: string;
  onClick: () => void;
}) {

  return (

    <button
      type="button"
      onClick={onClick}
      className="group rounded-xl border border-slate-200 bg-white p-4 text-left shadow-sm transition hover:-translate-y-[1px] hover:border-slate-300 hover:shadow"
    >

      <div className="flex items-start gap-3">


        <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-[#eef4fb] text-[#17304a]">

          <MessageSquare size={15} />

        </div>


        <div>

          <p className="text-[12px] font-semibold text-slate-800">
            {title}
          </p>

          <p className="mt-1 text-[10px] leading-5 text-slate-500">
            {description}
          </p>

        </div>

      </div>

    </button>
  );
}


/* ============================================================
   RECENT QUERY
============================================================ */

function RecentQuery({
  text,
}: {
  text: string;
}) {

  return (

    <button
      type="button"
      className="block w-full border-b border-slate-100 py-3 text-left last:border-0 hover:bg-slate-50"
    >

      <p className="text-[11px] font-medium text-slate-700">
        {text}
      </p>

      <p className="mt-1 text-[9px] text-slate-400">
        Recent
      </p>

    </button>
  );
}