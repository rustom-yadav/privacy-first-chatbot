# 🛡️ Privacy-First Chatbot — Client (Frontend)

![Next.js](https://img.shields.io/badge/Next.js-black?style=for-the-badge&logo=next.js&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)

Welcome to the frontend of the **Privacy-First Chatbot**. This is a modern, dark-themed chat interface built with Next.js 16, React 19, TypeScript, and Tailwind CSS v4. It connects to the FastAPI backend to provide a premium, completely local, and privacy-first AI chat experience.

---

## ✨ Features

- **🔒 Privacy-First Design** — No data leaves your machine. All processing is local.
- **💬 Real-time Chat** — Send questions and get AI responses with source attribution.
- **📄 PDF Document Management** — Upload (via click or drag-and-drop), list, and delete documents.
- **🎨 Premium Dark UI** — Glassmorphism, smooth animations, and curated emerald accent colors.
- **📱 Fully Responsive** — Seamless experience on desktop and mobile with a collapsible sidebar.
- **⚡ Session Persistence** — Chat sessions automatically persist across page reloads via `localStorage`.
- **🏥 Health Monitoring** — Live API health status indicator integrated right into the sidebar.

---

## 🚀 Getting Started

> **💡 Recommendation:** The easiest way to run the _entire_ application (Frontend + Backend + Database + ollama) is using the `pnpm run dev` or `docker compose up -d --build` from the root directory. With `pnpm run dev`, Ollama must already be running on your laptop and the model you pulled must exactly match `LLM_MODEL` in `api/.env`. With Docker Compose, no separate Ollama setup is needed: Docker starts Ollama and downloads the model configured in the root `.env` automatically.
>
> If you want to run the frontend in isolation for development, follow the steps below.

### 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (v24 LTS recommended)
- **pnpm** (v12.x required)
- The **API Backend** must be running (see [../api/README.md](../api/README.md))

### 📂 1. Navigate to the Client Directory

All commands below must be run from inside the `client` folder:

```bash
cd client
```

### ⚙️ 2. Environment Setup

Copy the sample environment file to create your local configuration:

```bash
cp sample.env .env.local
```

Inside `.env.local`, you will find:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Note: Adjust the `NEXT_PUBLIC_API_URL` if your backend is running on a different host or port.**

### 🛠️ 3. Running Locally (Development Mode)

If you are developing the frontend, running it locally without Docker provides the best experience (Hot Module Replacement, faster reloads).

1. **Install Dependencies:**
   Make sure you have [pnpm v12](https://pnpm.io/) activated.

   ```bash
   pnpm install
   ```

2. **Start the Development Server:**

   ```bash
   pnpm run dev
   ```

3. **Access the App:**
   Open **[http://localhost:3000](http://localhost:3000)** in your browser.

### 🐳 4. Running with Docker (Standalone)

If you want to build and run _only_ the frontend via Docker:

1. **Build the image:**

   ```bash
      docker build \
        --build-arg NEXT_PUBLIC_API_URL=http://localhost:8000 \
        -t privacy-chatbot-client .
   ```

2. **Run the container:**

   ```bash
   docker run -p 3000:3000 privacy-chatbot-client
   ```

   **Note: Adjust the `NEXT_PUBLIC_API_URL` if your backend is running on a different host or port.**

---

## 🌐 How to Use the App

1. **Check Connection:** Ensure the health status indicator in the sidebar shows a green "Connected" status.
2. **Upload a PDF:** Click the designated zone in the sidebar to select a PDF, or simply drag and drop the file.
3. **Ask Questions:** Type your query in the chat input at the bottom and press Enter.
4. **View Sources:** Click "Show Sources" on the AI's response to see exactly which pages of your PDF were referenced.
5. **New Chat:** Click the "New Chat" button in the sidebar to start the new conversation.

---

## 🏗️ Tech Stack

| Technology          | Purpose                                                |
| ------------------- | ------------------------------------------------------ |
| **Next.js**         | React framework utilizing the App Router               |
| **React 19**        | Core UI library for building interactive components    |
| **TypeScript**      | Ensures type-safe JavaScript across the application    |
| **Tailwind CSS v4** | Utility-first CSS framework for rapid, premium styling |
| **pnpm v12**        | Fast, disk space efficient package manager             |

---

## 📁 Project Structure

```text
client/
├── src/
│   ├── app/                  # Next.js App Router pages
│   │   ├── layout.tsx        # Root layout with SEO metadata
│   │   ├── page.tsx          # Main 2-column chat page
│   │   └── globals.css       # Design system + animations
│   ├── components/
│   │   ├── chat/             # Chat UI components (Input, Messages, etc.)
│   │   └── sidebar/          # Sidebar components (Upload, Status, etc.)
│   ├── hooks/                # Custom React hooks (useChat, useDocuments)
│   └── lib/                  # Utilities
│       ├── api.ts            # Type-safe API client (handles proxy routing)
│       └── types.ts          # TypeScript interfaces
├── Dockerfile                # Multi-stage Docker build (deps, builder, runner)
├── next.config.ts            # Next.js configuration (standalone, compiler etc.)
├── sample.env                # Environment variable reference
└── package.json              # Project dependencies and scripts
```
