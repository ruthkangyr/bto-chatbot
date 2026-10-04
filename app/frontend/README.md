# HDB BTO Assistant - Frontend Application ⚛️🎨

The frontend is a modern web application built with **Node.js**, **React 18**, **Vite**, and **Tailwind CSS**. It provides an intuitive, responsive interface for querying the HDB BTO Assistant backend.

---

## 🌟 Key Features

* **Tailwind CSS Design**: Custom emerald housing theme with sleek dark mode aesthetics.
* **Clickable Starter Topics**: Quick suggestion chips for common housing questions (Singles rules, Standard/Plus/Prime, CPF grants, HFE letter).
* **Rich Markdown Support**: Formats AI responses into bold text, clean bullet lists, and paragraphs with `react-markdown`.
* **One-Click Copy**: Copy any assistant answer directly to clipboard.
* **Live Health Indicator**: Real-time status badge showing connection to the FastAPI backend.
* **Built-In API Proxy**: Automatically forwards `/api` requests to the FastAPI backend on port `8000` during development without CORS issues.

---

## 📋 Prerequisites

* **Node.js**: v18 or higher (tested on Node v22).
* **npm**: v9 or higher.

---

## 🚀 How to Run the Frontend (Locally)

### 1. Open Terminal
Navigate to this frontend directory:
```powershell
cd "c:\Users\ruth\Documents\Courses\AI in Production\app\frontend"
```

### 2. Install Dependencies (First time only)
```powershell
npm install
```

### 3. Start the Development Server
```powershell
npm run dev
```

* Vite will launch on **`http://localhost:5173`**.
* Open your browser and navigate to **`http://localhost:5173`**.
* Any edits made to React components in `src/` will update instantly with **Hot Module Replacement (HMR)**!

---

## 📦 Building for Production

To create an optimized, compiled production build:
```powershell
npm run build
```

* Compiles all React code and Tailwind CSS into the **`dist/`** directory.
* The compiled bundle is automatically mounted and served by the FastAPI backend on port `8000`.

---

## 📁 Component Structure

```
src/
├── components/
│   ├── Header.jsx         # App bar with branding, live status badge, and reset button
│   ├── QuickTopics.jsx    # Clickable starter question cards
│   ├── ChatMessage.jsx    # User & AI message bubbles with ReactMarkdown and copy button
│   └── ChatInput.jsx      # Bottom input bar with keyboard enter submit & loading spinner
├── App.jsx                # Main application state, auto-scrolling, and API connector
├── index.css              # Tailwind CSS directives & scrollbar styles
└── main.jsx               # React entry point
```

