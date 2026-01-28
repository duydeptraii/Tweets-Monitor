# X Tweet Monitor

A terminal-based dashboard for monitoring X/Twitter account tweet activity in real-time.

![Monitor Style](assets/c__Users_X13_AppData_Roaming_Cursor_User_workspaceStorage_1a60e6934f102274e33babd814a20f91_images_image-0819262b-0af3-4497-b489-052e20d7842d.png)

## Features

- **Live tweet monitoring** - Track new tweets in real-time
- **Daily tweet counter** - See how many tweets an account posts per day
- **Beautiful terminal UI** - Modern dark theme dashboard inspired by trading terminals
- **Activity log** - View real-time updates and events
- **Session statistics** - Track monitoring duration and tweet counts
- **Demo mode** - Works without API key for testing
- **Custom time range counter** - Count tweets in a specific date/time window
- **Desktop UI (Windows)** - Run without opening a terminal

## Quick Start (Step-by-Step)

### Step 1: Clone or Download the Project

Download the project files to your local machine.

### Step 2: Open Terminal in Project Folder

Navigate to the project directory:

```bash
cd path/to/moniter-tweets
```

### Step 3: Create a Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Run the Monitor

**Option A - Demo Mode (no API key needed):**

```bash
python tweet_monitor.py
```

**Option B - Live Mode (with Twitter API):**

1. Copy the example environment file:
   ```bash
   # Windows
   copy .env.example .env
   
   # macOS/Linux
   cp .env.example .env
   ```

2. Edit `.env` and add your Twitter Bearer Token (see [Getting a Twitter API Key](#getting-a-twitter-api-key) below)

3. Run the monitor:
   ```bash
   python tweet_monitor.py -u elonmusk
   ```

**Option C - Desktop UI (Windows, no terminal):**

Double-click:

- `run_monitor_gui.bat`
- `X Tweet Monitor (Desktop).vbs` (launches hidden, no console window)

Or run:

```bash
pythonw tweet_monitor_gui.pyw
```

### Step 6: Exit the Monitor

Press `Ctrl+C` to stop monitoring and exit.

---

## Installation

1. **Install Python dependencies:**

```bash
pip install -r requirements.txt
```

2. **Configure API access (optional, for live data):**

Copy `.env.example` to `.env` and add your Twitter API Bearer Token:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```
TWITTER_BEARER_TOKEN=your_bearer_token_here
MONITOR_USERNAME=elonmusk
UPDATE_INTERVAL=60
```

### Getting a Twitter API Key

To get a Twitter API Bearer Token:

1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Sign in with your Twitter/X account
3. Click "Create Project" and follow the setup wizard
4. Create an app within your project
5. Go to "Keys and tokens" section
6. Generate a "Bearer Token" and copy it
7. Paste the token into your `.env` file

## Usage

### Basic Usage (Demo Mode)

Run without API key to see the interface with simulated data:

```bash
python tweet_monitor.py
```

### Monitor a Specific Account

```bash
python tweet_monitor.py -u username
```

### Custom Update Interval

```bash
python tweet_monitor.py -u username -i 30
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `-u, --username` | Twitter username to monitor (without @) | elonmusk |
| `-i, --interval` | Update interval in seconds | 60 |
| `--range-start` | Custom range start (e.g. `2026-01-26 09:00`) | (none) |
| `--range-end` | Custom range end (e.g. `2026-01-26 18:00`) | (none) |

### Activity Log Scrolling (Terminal UI)

When running `tweet_monitor.py` in the terminal UI, you can scroll the activity log:

- **Up/Down**: scroll by 1 line
- **Page Up/Page Down**: scroll by 5 lines
- **Home**: jump to oldest
- **End**: jump back to newest

## Interface Overview

```
┌─────────────────────────────────────────────────────────────┐
│ ● X TWEET MONITOR  │  api.twitter.com  │  Live    HH:MM:SS │
├─────────────────────────────────────────────────────────────┤
│ ACCOUNT          TOTAL TWEETS    TODAY'S TWEETS   FOLLOWERS│
│ @username        12,345          42               1,234,567│
├─────────────────────────────────────────────────────────────┤
│ RECENT TWEETS - @username                    │ STATS       │
│ TIME     TWEET              RT    LIKES  REP │ Started:... │
│ 12:34:56 Tweet text...      100   5,000  50  │ Duration:...│
│ 12:30:00 Another tweet...   200   8,000  120 │ Interval:...│
├─────────────────────────────────────────────────────────────┤
│ ACTIVITY LOG                                               │
│ 12:34:56 New tweet detected - Tweet text...                │
│ 12:34:00 Found 1 new tweet(s)                              │
├─────────────────────────────────────────────────────────────┤
│ ACNT: @username     TWEETS: 12,345     TODAY: 42 tweets    │
└─────────────────────────────────────────────────────────────┘
```

## Requirements

- Python 3.8+
- rich >= 13.0.0
- tweepy >= 4.14.0 (optional, for live API access)
- python-dotenv >= 1.0.0

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| Monitor shows "DEMO" mode | Add a valid `TWITTER_BEARER_TOKEN` to your `.env` file |
| API errors | Check that your Bearer Token is correct and has proper permissions |
| Terminal looks broken | Ensure your terminal supports Unicode and has a dark theme |

## License

MIT License
