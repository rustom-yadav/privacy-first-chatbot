# 🛡️ Privacy-First Chatbot — Frontend (Client)

Welcome to the frontend of the **Privacy-First Chatbot**. This is a modern, dark-themed chat interface built with Next.js 16, TypeScript, and Tailwind CSS v4. It connects to the FastAPI backend to provide a premium, privacy-first AI chat experience.

## ✨ Features

- **🔒 Privacy-First Design** — No data leaves your machine. All processing is local.
- **💬 Real-time Chat** — Send questions and get AI responses with source attribution.
- **📄 PDF Document Management** — Upload, list, and delete documents via drag-and-drop.
- **🎨 Premium Dark UI** — Glassmorphism, animations, and emerald accent colors.
- **📱 Fully Responsive** — Works on desktop and mobile with collapsible sidebar.
- **⚡ Session Persistence** — Chat sessions persist across page reloads via localStorage.
- **🏥 Health Monitoring** — Live API health status indicator in the sidebar.

## 🚀 Getting Started Step-by-Step

### Step 1: Prerequisites
Make sure the **API server** is running first. See [`../api/README.md`](../api/README.md) for setup instructions.

### Step 2: Set Up Environment Variables
Copy the sample environment file:
```bash
cp sample.env .env.local
```

The default `NEXT_PUBLIC_API_URL` is `http://localhost:8000` which matches the API server's default port.

### Step 3: Run the Application (Choose Option A or B)

#### Option A: Run using Docker (Recommended)
Docker is the easiest way to run the frontend.

1. **Build the image:**
   ```bash
   docker build -t privacy-chatbot-client .
   ```

2. **Run the container:**
   ```bash
   docker run -p 3000:3000 \
     -e NEXT_PUBLIC_API_URL=http://localhost:8000 \
     privacy-chatbot-client
   ```

#### Option B: Run Without Docker (Local Setup)
If you prefer running directly:

1. **Install Dependencies:**
   Make sure you have [pnpm](https://pnpm.io/) installed, then run:
   ```bash
   pnpm install
   ```

2. **Start the Dev Server:**
   ```bash
   pnpm run dev
   ```

---

## 🌐 How to Use

Once the frontend is running (and the API is up):

1. Open **[http://localhost:3000](http://localhost:3000)** in your browser.
2. **Upload a PDF** — Use the drag-and-drop zone in the sidebar.
3. **Ask questions** — Type your question in the chat input and press Enter.
4. **View sources** — Click "Show Sources" on AI responses to see which pages were referenced.
5. **New chat** — Click "New Chat" in the sidebar to start a fresh conversation.

## 🏗️ Tech Stack

| Technology | Purpose |
|---|---|
| [Next.js 16](https://nextjs.org/) | React framework with App Router |
| [TypeScript](https://www.typescriptlang.org/) | Type-safe JavaScript |
| [Tailwind CSS v4](https://tailwindcss.com/) | Utility-first CSS |
| [React 19](https://react.dev/) | UI library |

## 📁 Project Structure

```
client/
├── src/
│   ├── app/                  # Next.js App Router pages
│   │   ├── layout.tsx        # Root layout with SEO metadata
│   │   ├── page.tsx          # Main 2-column chat page
│   │   └── globals.css       # Design system + animations
│   ├── components/
│   │   ├── chat/             # Chat UI components
│   │   │   ├── ChatWindow.tsx
│   │   │   ├── ChatInput.tsx
│   │   │   └── MessageBubble.tsx
│   │   └── sidebar/          # Sidebar components
│   │       ├── Sidebar.tsx
│   │       ├── DocumentCard.tsx
│   │       ├── UploadZone.tsx
│   │       └── StatusBadge.tsx
│   ├── hooks/                # Custom React hooks
│   │   ├── useChat.ts
│   │   └── useDocuments.ts
│   └── lib/                  # Utilities
│       ├── api.ts            # Type-safe API client
│       └── types.ts          # TypeScript interfaces
├── Dockerfile                # Multi-stage Docker build
├── next.config.ts            # Next.js config with API rewrites
├── sample.env                # Environment variable reference
└── package.json
```
