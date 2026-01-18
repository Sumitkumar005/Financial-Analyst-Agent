# Financial Analyst Frontend

Professional, minimal React frontend for the Table-Aware Financial Analysis RAG system.

## Design Philosophy

- **Minimal & Clean**: Professional design with subtle colors
- **Enterprise-Grade**: Built for FAANG professionals and executives
- **Performance-First**: Fast, responsive, optimized
- **Accessible**: WCAG compliant, keyboard navigation

## Features

- Natural language query input
- Real-time analysis results
- Token usage tracking
- Query history
- Markdown rendering for analysis
- Responsive design

## Tech Stack

- **React 18** + **TypeScript**
- **Vite** - Fast build tool
- **Axios** - HTTP client
- **React Markdown** - Markdown rendering
- **Lucide React** - Professional icons
- **CSS Modules** - Scoped styling

## Getting Started

### Install Dependencies

```bash
npm install
```

### Start Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## API Configuration

Make sure your FastAPI backend is running at `http://localhost:8000`

To change the API URL, edit `src/App.tsx`:

```typescript
const API_BASE_URL = 'http://localhost:8000';
```

## Design System

### Colors
- Primary: `#0066cc` (Professional blue)
- Background: `#ffffff` / `#f8f9fa`
- Text: `#1a1a1a` / `#6b7280`
- Borders: `#e5e7eb`

### Typography
- Font: System fonts (SF Pro, Inter, Segoe UI)
- Sizes: 12px - 30px scale
- Weights: 400, 500, 600, 700

### Spacing
- 8px grid system
- Consistent spacing scale

## Features in Detail

### Query Input
- Multi-line textarea
- Keyboard shortcut: `Cmd/Ctrl + Enter` to submit
- Placeholder with examples
- Auto-resize

### Results Display
- Markdown rendering
- Table support
- Code blocks
- Company badges
- Source attribution

### Token Tracking
- Real-time token counting
- Cost estimation
- Persistent storage (localStorage)

### Query History
- Last 10 queries saved
- Quick reload
- Persistent storage

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## License

MIT
