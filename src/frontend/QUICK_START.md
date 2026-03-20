# Quick Setup Guide for Frontend

## Quick Start (5 minutes)

### Prerequisites
- **Node.js**: Version 20.19.0+ or 22.12.0+
  - Download: https://nodejs.org/
  - Verify: `node --version`

### Installation

1. **Navigate to frontend directory**
   ```bash
   cd cityTrip/src/frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Open in browser**
   - Go to: http://localhost:5173
   - Allow geolocation permission when prompted

**You're ready to develop!**

---

## Available Commands

| Command | Purpose |
|---------|---------|
| `npm run dev` | Start development server with hot reload |
| `npm run build` | Create production build |
| `npm run type-check` | Check TypeScript types |
| `npm run preview` | Preview production build locally |

---

## Configuration

### API Base URL (Optional)

Create `.env.local` in the `frontend` directory:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Default: `http://127.0.0.1:8000`

---

## Production Build

```bash
npm run build
npm run preview
```

Build output: `dist/` directory

---

## Dependencies

See `REQUIREMENTS.md` for detailed information about all dependencies and system requirements.

---

## Troubleshooting

**Port 5173 in use?**
```bash
npm run dev -- --port 3000
```

**Dependencies not installing?**
```bash
rm -rf node_modules package-lock.json
npm install
```

**TypeScript errors?**
```bash
npm run type-check
```

---

**For complete setup documentation, see: ../REQUIREMENTS.md**
