# OmniTrade AI - Frontend Dashboard

Modern React-based web dashboard for monitoring and controlling the OmniTrade AI trading system.

## Features

### 📊 Dashboard
- Real-time portfolio performance charts
- P&L tracking (total and daily)
- Win rate and active positions overview
- Recent trades feed
- System status indicators
- Quick action controls

### 📈 Strategies
- View all active trading strategies
- Start/pause individual strategies
- Performance metrics per strategy
- Strategy templates library
- Multi-broker strategy support

### 💼 Positions
- Monitor all open positions
- Real-time P&L updates
- Stop-loss and take-profit levels
- Risk/reward ratios
- Quick position closing
- Multi-broker position view

### ⚙️ Settings
- Trading controls (enable/disable)
- Risk management parameters
- Broker API key configuration
- Notification settings (Telegram)
- Paper trading vs live mode toggle

## Technology Stack

- **React 18** - UI library
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - High-quality UI components
- **Recharts** - Data visualization
- **Lucide React** - Icon library

## Getting Started

### Prerequisites

- Node.js 18+ or 22+ (recommended)
- pnpm (package manager)

### Installation

```bash
# Install dependencies
pnpm install

# Start development server
pnpm run dev

# Build for production
pnpm run build

# Preview production build
pnpm run preview
```

### Development

The development server runs on `http://localhost:5173` with hot module replacement (HMR).

```bash
pnpm run dev --host  # Expose to network
```

## Project Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── assets/         # Images, fonts, etc.
│   ├── components/     # Reusable components
│   │   ├── ui/        # shadcn/ui components
│   │   ├── Header.jsx
│   │   └── Sidebar.jsx
│   ├── pages/          # Page components
│   │   ├── Dashboard.jsx
│   │   ├── Strategies.jsx
│   │   ├── Positions.jsx
│   │   └── Settings.jsx
│   ├── App.jsx         # Main app component
│   ├── App.css         # Global styles
│   ├── main.jsx        # Entry point
│   └── index.css       # Tailwind imports
├── index.html          # HTML template
├── package.json        # Dependencies
└── vite.config.js      # Vite configuration
```

## Connecting to Backend

The frontend is designed to connect to the FastAPI backend at `http://localhost:8000`.

### API Integration (To Be Implemented)

Create an API client in `src/lib/api.js`:

```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = {
  // System
  getSystemStatus: () => fetch(`${API_BASE_URL}/api/v1/system/status`).then(r => r.json()),
  startEngine: () => fetch(`${API_BASE_URL}/api/v1/system/control`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action: 'start' })
  }).then(r => r.json()),
  
  // Account
  getAccount: (broker) => fetch(`${API_BASE_URL}/api/v1/account/${broker}`).then(r => r.json()),
  
  // Positions
  getPositions: (broker) => fetch(`${API_BASE_URL}/api/v1/positions/${broker}`).then(r => r.json()),
  
  // Trading
  executeTrade: (data) => fetch(`${API_BASE_URL}/api/v1/trade/execute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(r => r.json()),
}
```

### Environment Variables

Create `.env` file:

```bash
VITE_API_URL=http://localhost:8000
```

## Deployment

### Build for Production

```bash
pnpm run build
```

This creates an optimized production build in the `dist/` directory.

### Deploy Options

#### 1. Static Hosting (Netlify, Vercel, GitHub Pages)

```bash
# Build
pnpm run build

# Deploy dist/ folder to your hosting service
```

#### 2. Docker (with Backend)

The included `docker-compose.yml` in the root directory will build and serve the frontend alongside the backend.

```bash
cd ..  # Go to project root
docker-compose up -d
```

#### 3. Nginx

Serve the `dist/` folder with Nginx:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
    }
}
```

## Features Roadmap

### Phase 1 (Current)
- ✅ Dashboard with stats and charts
- ✅ Strategy management interface
- ✅ Position monitoring
- ✅ Settings configuration
- ✅ Responsive design
- ✅ Dark mode support

### Phase 2 (Next)
- [ ] Real-time WebSocket updates
- [ ] API integration with backend
- [ ] User authentication
- [ ] Advanced charting (TradingView)
- [ ] Trade history with filters
- [ ] Performance analytics

### Phase 3 (Future)
- [ ] Backtesting interface
- [ ] Strategy builder (visual)
- [ ] Alert management
- [ ] Mobile app (React Native)
- [ ] Multi-user support
- [ ] Role-based access control

## Customization

### Theming

The app uses Tailwind CSS with custom color variables defined in `src/App.css`. Modify the CSS variables to change the theme:

```css
:root {
  --primary: oklch(0.205 0 0);
  --secondary: oklch(0.97 0 0);
  /* ... */
}
```

### Adding Components

Use shadcn/ui CLI to add more components:

```bash
pnpm dlx shadcn@latest add [component-name]
```

Available components: https://ui.shadcn.com/docs/components

## Development Tips

### Hot Reload

Vite provides instant hot module replacement. Changes to components will reflect immediately without full page reload.

### Component Structure

Follow this pattern for new components:

```javascript
import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

const MyComponent = () => {
  const [state, setState] = useState(initialValue)

  return (
    <div className="space-y-6">
      <Card className="p-6">
        {/* Component content */}
      </Card>
    </div>
  )
}

export default MyComponent
```

### Styling Guidelines

- Use Tailwind utility classes
- Leverage shadcn/ui components
- Maintain consistent spacing (space-y-6, gap-4, etc.)
- Use semantic color classes (text-foreground, bg-card, etc.)

## Troubleshooting

### Port Already in Use

```bash
# Vite will automatically try the next port
pnpm run dev --host
```

### Build Errors

```bash
# Clear cache and reinstall
rm -rf node_modules pnpm-lock.yaml
pnpm install
pnpm run build
```

### Component Not Found

```bash
# Reinstall shadcn components
pnpm dlx shadcn@latest add [component-name]
```

## Contributing

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Submit pull request

## License

Same as parent project (OmniTrade AI)

---

**Note**: This frontend is currently using mock data. API integration with the FastAPI backend is the next development priority.

