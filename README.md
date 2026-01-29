# X-TERMINAL

A dark cyberpunk-themed dashboard for monitoring X/Twitter activity. Built with React, Vite, and Tailwind CSS.

## Features

- Glassmorphism UI panels with neon accent highlights
- Real-time metrics display (followers, tweets, engagement)
- Live tweet feed with terminal-style interface
- Activity volume chart visualization
- Monospace typography throughout
- Fully responsive layout

## Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling with custom cyberpunk theme

## Getting Started

### Prerequisites

- Node.js 18+ installed

### Installation

```bash
cd dashboard
npm install
```

### Run Development Server

```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

### Build for Production

```bash
npm run build
```

Output will be in the `dashboard/dist` folder.

## Project Structure

```
dashboard/
├── src/
│   ├── components/
│   │   ├── ChartArea.jsx    # Activity volume chart
│   │   ├── FeedPanel.jsx    # Live tweet feed
│   │   ├── Header.jsx       # Top navigation bar
│   │   └── StatCard.jsx     # Metric display cards
│   ├── hooks/
│   │   └── useMockData.js   # Simulated real-time data
│   ├── App.jsx              # Main dashboard layout
│   ├── index.css            # Tailwind + custom styles
│   └── main.jsx             # Entry point
├── tailwind.config.js       # Custom color palette
└── index.html
```

## Customization

### Colors

Edit `tailwind.config.js` to adjust the neon color scheme:

```js
colors: {
  'neon-green': '#00ff9f',
  'neon-blue': '#00d2ff',
  'neon-pink': '#ff0055',
  'cyber-black': '#0b0c15',
}
```

### Mock Data

Modify `src/hooks/useMockData.js` to change simulated usernames, messages, or update intervals.

## License

MIT
