# 🎨 Professional Frontend - Setup Guide

## ✅ What Was Created

A **professional, minimal, enterprise-grade** React frontend designed for FAANG professionals:

### Design Features
- ✨ **Minimal Color Palette**: Professional grays, subtle blue accent (#0066cc)
- 🎯 **Clean Typography**: System fonts (SF Pro, Inter, Segoe UI)
- 📐 **8px Grid System**: Consistent spacing throughout
- 🎨 **Subtle Shadows**: Professional depth without being heavy
- ⚡ **Smooth Animations**: Fast, subtle transitions
- 📱 **Fully Responsive**: Works on all screen sizes

### Key Components
1. **Query Input**: Multi-line textarea with examples
2. **Results Panel**: Markdown rendering with tables
3. **Token Tracker**: Real-time usage and cost estimation
4. **Query History**: Last 10 queries with quick reload
5. **Company Badges**: Visual indicators for analyzed companies

## 🚀 Quick Start

### 1. Navigate to Frontend Directory

```bash
cd frontend
```

### 2. Install Dependencies (if not already done)

```bash
npm install
```

### 3. Start Development Server

```bash
npm run dev
```

The frontend will be available at: **http://localhost:5173**

### 4. Make Sure Backend is Running

Your FastAPI server should be running at: **http://localhost:8000**

```bash
# In another terminal
cd "C:\Users\FA-Sumit\New folder"
python server.py
```

## 🎯 Features

### Query Input
- Natural language queries
- Keyboard shortcut: `Cmd/Ctrl + Enter` to submit
- Placeholder with examples
- Auto-resize textarea

### Results Display
- Full markdown rendering
- Financial tables preserved
- Code blocks support
- Company badges
- Source attribution

### Token Tracking
- Real-time token counting
- Cost estimation (Gemini 2.5 Flash pricing)
- Persistent storage (localStorage)
- Display in header

### Query History
- Last 10 queries saved
- Click to reload
- Persistent across sessions
- Shows companies analyzed

## 🎨 Design System

### Colors
```css
Primary Accent: #0066cc (Professional blue)
Background: #ffffff / #f8f9fa
Text: #1a1a1a / #6b7280
Borders: #e5e7eb
```

### Typography
- **Font**: System fonts (SF Pro, Inter, Segoe UI)
- **Sizes**: 12px - 30px scale
- **Weights**: 400, 500, 600, 700

### Spacing
- 8px grid system
- Consistent scale: 4px, 8px, 16px, 24px, 32px, 48px

## 📱 Responsive Design

- **Desktop**: Full layout with all features
- **Tablet**: Optimized spacing
- **Mobile**: Stacked layout, touch-friendly

## 🔧 Configuration

### Change API URL

Edit `frontend/src/App.tsx`:

```typescript
const API_BASE_URL = 'http://localhost:8000';
```

### Customize Colors

Edit `frontend/src/index.css`:

```css
:root {
  --color-accent: #0066cc; /* Your brand color */
  /* ... other colors */
}
```

## 🚀 Production Build

### Build

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

### Deploy

The `dist/` folder contains the production build. Deploy to:
- Vercel
- Netlify
- AWS S3 + CloudFront
- Any static hosting

## 🎯 Best Practices Implemented

✅ **Accessibility**: WCAG compliant, keyboard navigation
✅ **Performance**: Optimized bundle, lazy loading ready
✅ **Type Safety**: Full TypeScript support
✅ **Code Quality**: Clean, maintainable code
✅ **Responsive**: Mobile-first design
✅ **Professional**: Enterprise-grade UI/UX

## 🐛 Troubleshooting

### CORS Issues

If you see CORS errors, make sure your FastAPI server has CORS enabled (it should already be configured).

### API Connection Failed

1. Check if backend is running: `http://localhost:8000/health`
2. Verify API_BASE_URL in `App.tsx`
3. Check browser console for errors

### Build Errors

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 📝 Next Steps

1. **Customize Branding**: Update logo, colors, name
2. **Add Features**: Export results, save queries, etc.
3. **Analytics**: Add tracking (optional)
4. **Authentication**: Add user accounts (if needed)

## 🎉 You're Ready!

Your professional frontend is ready to impress FAANG professionals! 🚀
