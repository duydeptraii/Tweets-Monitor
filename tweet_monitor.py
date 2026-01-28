#!/usr/bin/env python3
"""
X/Twitter Tweet Monitor
A terminal-based dashboard for monitoring tweet activity
"""

import os
import sys
import time
import threading
from datetime import datetime, timedelta
from collections import deque
from dataclasses import dataclass, field
from typing import Optional, List, Deque
import random

try:
    from rich.console import Console
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.table import Table
    from rich.live import Live
    from rich.text import Text
    from rich.style import Style
    from rich.align import Align
    from rich import box
except ImportError:
    print("Please install required packages: pip install -r requirements.txt")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Try to import tweepy for real API access
try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False


@dataclass
class Tweet:
    """Represents a single tweet"""
    id: str
    text: str
    created_at: datetime
    kind: str = "tweet"  # tweet | reply | repost | quote
    retweet_count: int = 0
    like_count: int = 0
    reply_count: int = 0


@dataclass
class MonitorStats:
    """Statistics for the monitored account"""
    username: str = ""
    display_name: str = ""
    total_tweets: int = 0
    today_tweets: int = 0
    period_tweets: int = 0
    followers: int = 0
    following: int = 0
    monitoring_start: datetime = field(default_factory=datetime.now)
    last_update: Optional[datetime] = None
    recent_tweets: Deque[Tweet] = field(default_factory=lambda: deque(maxlen=50))
    activity_log: Deque[str] = field(default_factory=lambda: deque(maxlen=200))
    range_start: Optional[datetime] = None
    range_end: Optional[datetime] = None
    range_tweets: Optional[int] = None


class TwitterAPI:
    """Twitter/X API wrapper"""
    
    def __init__(self, bearer_token: Optional[str] = None):
        self.bearer_token = bearer_token or os.getenv("TWITTER_BEARER_TOKEN")
        self.client = None
        self.demo_mode = True
        
        if self.bearer_token and TWEEPY_AVAILABLE and self.bearer_token != "your_bearer_token_here":
            try:
                self.client = tweepy.Client(bearer_token=self.bearer_token)
                self.demo_mode = False
            except Exception as e:
                print(f"Failed to initialize Twitter client: {e}")
    
    def get_user_info(self, username: str) -> dict:
        """Get user information"""
        if self.demo_mode:
            return self._demo_user_info(username)
        
        try:
            user = self.client.get_user(
                username=username,
                user_fields=["public_metrics", "name", "description", "created_at"]
            )
            if user.data:
                metrics = user.data.public_metrics
                return {
                    "id": user.data.id,
                    "username": user.data.username,
                    "name": user.data.name,
                    "followers": metrics["followers_count"],
                    "following": metrics["following_count"],
                    "tweets": metrics["tweet_count"]
                }
        except Exception as e:
            print(f"API Error: {e}")
        
        return self._demo_user_info(username)
    
    def get_recent_tweets(self, user_id: str, max_results: int = 10) -> List[Tweet]:
        """Get recent tweets from a user"""
        if self.demo_mode:
            return self._demo_tweets()
        
        try:
            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=max_results,
                tweet_fields=["created_at", "public_metrics", "referenced_tweets"]
            )
            
            result = []
            if tweets.data:
                for tweet in tweets.data:
                    metrics = tweet.public_metrics or {}
                    kind = "tweet"
                    refs = getattr(tweet, "referenced_tweets", None) or []
                    for ref in refs:
                        ref_type = getattr(ref, "type", None)
                        if ref_type == "replied_to":
                            kind = "reply"
                            break
                        if ref_type == "retweeted":
                            kind = "repost"
                            break
                        if ref_type == "quoted":
                            kind = "quote"
                            break
                    result.append(Tweet(
                        id=tweet.id,
                        text=tweet.text[:100] + "..." if len(tweet.text) > 100 else tweet.text,
                        created_at=tweet.created_at,
                        kind=kind,
                        retweet_count=metrics.get("retweet_count", 0),
                        like_count=metrics.get("like_count", 0),
                        reply_count=metrics.get("reply_count", 0)
                    ))
            return result
        except Exception as e:
            print(f"API Error: {e}")
        
        return self._demo_tweets()

    def count_tweets_in_range(self, user_id: str, start_time: datetime, end_time: datetime) -> int:
        """Count tweets (including replies/reposts) in a specific time range.

        Note: This may paginate and can be slow for large ranges.
        """
        if start_time >= end_time:
            return 0

        if self.demo_mode:
            # simple demo heuristic: ~1 per 2 hours, min 0
            hours = max(0.0, (end_time - start_time).total_seconds() / 3600.0)
            return int(hours / 2.0)

        if not self.client:
            return 0

        try:
            paginator = tweepy.Paginator(
                self.client.get_users_tweets,
                id=user_id,
                start_time=start_time,
                end_time=end_time,
                max_results=100,
                tweet_fields=["created_at"],
            )
            count = 0
            for page in paginator:
                if page and page.data:
                    count += len(page.data)
            return count
        except Exception as e:
            print(f"API Error (range count): {e}")
            return 0
    
    def _demo_user_info(self, username: str) -> dict:
        """Generate demo user info"""
        return {
            "id": "123456789",
            "username": username,
            "name": username.title(),
            "followers": random.randint(10000, 1000000),
            "following": random.randint(100, 5000),
            "tweets": random.randint(5000, 50000)
        }
    
    def _demo_tweets(self) -> List[Tweet]:
        """Generate demo tweets"""
        demo_texts = [
            "Just shipped a new feature! The team worked incredibly hard on this.",
            "Thinking about the future of technology and where we're headed...",
            "Great meeting with the team today. Exciting things coming soon!",
            "Working late tonight. Building something special.",
            "The response to our latest update has been amazing. Thank you all!",
            "New announcement coming tomorrow. Stay tuned!",
            "Reading some interesting papers on AI today.",
            "Coffee and code - the perfect combination.",
            "Replying to some questions from the community.",
            "Just hit a major milestone. More details soon!",
        ]
        
        tweets = []
        now = datetime.now()
        for i, text in enumerate(demo_texts[:5]):
            tweets.append(Tweet(
                id=str(random.randint(1000000, 9999999)),
                text=text,
                created_at=now - timedelta(hours=random.randint(1, 48)),
                retweet_count=random.randint(100, 10000),
                like_count=random.randint(500, 50000),
                reply_count=random.randint(50, 5000)
            ))
        return tweets


class TweetMonitor:
    """Main tweet monitoring application"""
    
    # Color scheme matching the reference image
    COLORS = {
        "header_bg": "#1a1a2e",
        "accent": "#00ff88",
        "accent_red": "#ff4757",
        "accent_blue": "#00d4ff",
        "text_dim": "#666688",
        "text": "#ffffff",
        "border": "#333355",
        "green": "#00ff88",
        "red": "#ff4444",
    }
    
    def __init__(
        self,
        username: str = None,
        update_interval: int = 60,
        range_start: Optional[datetime] = None,
        range_end: Optional[datetime] = None,
    ):
        self.username = username or os.getenv("MONITOR_USERNAME", "elonmusk")
        self.update_interval = int(os.getenv("UPDATE_INTERVAL", update_interval))
        self.console = Console()
        self.api = TwitterAPI()
        self.stats = MonitorStats(username=self.username)
        self.running = True
        self.user_id = None
        self._cycle = 0
        self._log_scroll_offset = 0  # 0 means "bottom"

        self.stats.range_start = range_start
        self.stats.range_end = range_end
        
        # Initialize
        self._log(f"[cyan]Initializing monitor for @{self.username}[/cyan]")
        self._fetch_user_info()
        self._refresh_range_count()
    
    def _log(self, message: str):
        """Add message to activity log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.stats.activity_log.append(f"[dim]{timestamp}[/dim] {message}")
    
    def _fetch_user_info(self):
        """Fetch initial user information"""
        info = self.api.get_user_info(self.username)
        if info:
            self.user_id = info["id"]
            self.stats.username = info["username"]
            self.stats.display_name = info["name"]
            self.stats.total_tweets = info["tweets"]
            self.stats.followers = info["followers"]
            self.stats.following = info["following"]
            self._log(f"[green]Connected to @{self.username}[/green]")
            
            if self.api.demo_mode:
                self._log("[yellow]Running in DEMO mode (no API key)[/yellow]")

    def _refresh_account_metrics(self):
        """Refresh total/followers/following (helps total_tweets update in live mode)."""
        info = self.api.get_user_info(self.username)
        if info:
            self.stats.total_tweets = info["tweets"]
            self.stats.followers = info["followers"]
            self.stats.following = info["following"]

    def _refresh_range_count(self):
        if not self.user_id or not self.stats.range_start or not self.stats.range_end:
            self.stats.range_tweets = None
            return
        self.stats.range_tweets = self.api.count_tweets_in_range(
            self.user_id, self.stats.range_start, self.stats.range_end
        )
    
    def _fetch_tweets(self):
        """Fetch recent tweets and update stats"""
        if not self.user_id:
            return
        
        tweets = self.api.get_recent_tweets(self.user_id)
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        new_count = 0
        for tweet in tweets:
            # Check if tweet is new
            existing_ids = [t.id for t in self.stats.recent_tweets]
            if tweet.id not in existing_ids:
                self.stats.recent_tweets.appendleft(tweet)
                new_count += 1
                kind_label = tweet.kind.upper()
                self._log(f"[green]New {kind_label} detected[/green] - {tweet.text[:60]}...")
        
        # Count today's tweets
        self.stats.today_tweets = sum(
            1 for t in self.stats.recent_tweets 
            if t.created_at >= today_start
        )
        
        # Count tweets in monitoring period
        self.stats.period_tweets = sum(
            1 for t in self.stats.recent_tweets 
            if t.created_at >= self.stats.monitoring_start
        )
        
        self.stats.last_update = now
        
        if new_count > 0:
            # Make counters "jump" immediately when new items arrive.
            self.stats.total_tweets += new_count
            self._log(f"[cyan]Found {new_count} new tweet(s)[/cyan]")

        # Refresh account metrics occasionally (live mode).
        self._cycle += 1
        if not self.api.demo_mode and (self._cycle % max(1, int(300 / max(1, self.update_interval))) == 0):
            # ~every 5 minutes
            self._refresh_account_metrics()

        # Refresh range count occasionally if a custom range is set.
        if self.stats.range_start and self.stats.range_end and (self._cycle % max(1, int(600 / max(1, self.update_interval))) == 0):
            # ~every 10 minutes
            self._refresh_range_count()
    
    def _make_header(self) -> Panel:
        """Create header panel"""
        header_text = Text()
        header_text.append("● ", style="green bold")
        header_text.append("X TWEET MONITOR", style="bold white")
        header_text.append("  |  ", style="dim")
        header_text.append("api.twitter.com", style="cyan")
        header_text.append("  |  ", style="dim")
        if self.api.demo_mode:
            header_text.append("DEMO MODE", style="bold yellow")
        else:
            header_text.append("LIVE MODE", style="bold green")
        
        time_str = datetime.now().strftime("%H:%M:%S")
        
        # Create a table for header layout
        table = Table.grid(expand=True)
        table.add_column(justify="left", ratio=3)
        table.add_column(justify="right", ratio=1)
        table.add_row(header_text, Text(time_str, style="dim"))
        
        return Panel(table, style="dim blue", box=box.SIMPLE)
    
    def _make_stats_panel(self) -> Panel:
        """Create statistics panel"""
        table = Table.grid(expand=True, padding=(0, 2))
        table.add_column(justify="left", ratio=1)
        table.add_column(justify="center", ratio=1)
        table.add_column(justify="center", ratio=1)
        table.add_column(justify="center", ratio=1)
        
        # Account info
        account_text = Text()
        account_text.append("ACCOUNT\n", style="dim")
        account_text.append(f"@{self.stats.username}", style="bold white")
        
        # Total tweets
        total_text = Text()
        total_text.append("TOTAL TWEETS\n", style="dim")
        total_text.append(f"{self.stats.total_tweets:,}", style="bold green")
        
        # Today's tweets
        today_text = Text()
        today_text.append("TODAY'S TWEETS\n", style="dim")
        today_text.append(f"{self.stats.today_tweets:,}", style="bold cyan")
        
        # Followers
        followers_text = Text()
        followers_text.append("FOLLOWERS\n", style="dim")
        followers_text.append(f"{self.stats.followers:,}", style="bold white")
        
        table.add_row(account_text, total_text, today_text, followers_text)
        
        return Panel(table, box=box.SIMPLE, style="dim")
    
    def _make_tweets_table(self) -> Panel:
        """Create tweets table panel"""
        table = Table(
            box=box.SIMPLE_HEAD,
            expand=True,
            show_header=True,
            header_style="bold dim",
            row_styles=["", "dim"]
        )
        
        table.add_column("TIME", style="dim cyan", width=10)
        table.add_column("TYPE", style="magenta", width=7)
        table.add_column("TWEET", style="white", ratio=3)
        table.add_column("RT", justify="right", style="dim", width=8)
        table.add_column("LIKES", justify="right", style="green", width=10)
        table.add_column("REPLIES", justify="right", style="cyan", width=10)
        
        # Sort tweets by date, most recent first
        sorted_tweets = sorted(
            self.stats.recent_tweets, 
            key=lambda t: t.created_at, 
            reverse=True
        )
        
        for tweet in list(sorted_tweets)[:10]:
            time_str = tweet.created_at.strftime("%H:%M:%S")
            text = tweet.text[:50] + "..." if len(tweet.text) > 50 else tweet.text
            text = text.replace("\n", " ")
            
            table.add_row(
                time_str,
                tweet.kind.upper(),
                text,
                f"{tweet.retweet_count:,}",
                f"+{tweet.like_count:,}",
                f"+{tweet.reply_count:,}"
            )
        
        title = f"RECENT TWEETS - @{self.stats.username}"
        return Panel(table, title=title, title_align="left", border_style="blue", box=box.ROUNDED)
    
    def _make_activity_log(self) -> Panel:
        """Create activity log panel"""
        log_text = Text()
        entries = list(self.stats.activity_log)
        window_size = 10
        if len(entries) <= window_size:
            visible = entries
        else:
            # offset=0 shows bottom; offset grows as you scroll up
            offset = max(0, min(self._log_scroll_offset, max(0, len(entries) - window_size)))
            end = len(entries) - offset
            start = max(0, end - window_size)
            visible = entries[start:end]

        for entry in visible:
            log_text.append(entry + "\n")
        
        return Panel(
            log_text,
            title="ACTIVITY LOG  (Scroll: ↑/↓, PgUp/PgDn, Home/End)",
            title_align="left",
            border_style="yellow",
            box=box.ROUNDED
        )
    
    def _make_stats_sidebar(self) -> Panel:
        """Create sidebar with detailed stats"""
        content = Text()
        
        content.append("MONITORING SESSION\n\n", style="bold cyan")
        
        # Session info
        duration = datetime.now() - self.stats.monitoring_start
        hours, remainder = divmod(int(duration.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        content.append("Started: ", style="dim")
        content.append(f"{self.stats.monitoring_start.strftime('%H:%M:%S')}\n", style="white")
        
        content.append("Duration: ", style="dim")
        content.append(f"{hours:02d}:{minutes:02d}:{seconds:02d}\n", style="white")
        
        content.append("Interval: ", style="dim")
        content.append(f"{self.update_interval}s\n\n", style="white")
        
        content.append("PERIOD STATS\n\n", style="bold cyan")
        
        content.append("Tweets detected: ", style="dim")
        content.append(f"{self.stats.period_tweets}\n", style="green bold")

        if self.stats.range_start and self.stats.range_end:
            content.append("\nCUSTOM RANGE\n\n", style="bold cyan")
            content.append("Start: ", style="dim")
            content.append(f"{self.stats.range_start.strftime('%Y-%m-%d %H:%M')}\n", style="white")
            content.append("End:   ", style="dim")
            content.append(f"{self.stats.range_end.strftime('%Y-%m-%d %H:%M')}\n", style="white")
            content.append("Count: ", style="dim")
            if self.stats.range_tweets is None:
                content.append("...\n", style="yellow")
            else:
                content.append(f"{self.stats.range_tweets}\n", style="green bold")
        
        content.append("Following: ", style="dim")
        content.append(f"{self.stats.following:,}\n", style="white")
        
        if self.stats.last_update:
            content.append("\nLast update: ", style="dim")
            content.append(f"{self.stats.last_update.strftime('%H:%M:%S')}\n", style="cyan")
        
        content.append("\n")
        
        if self.api.demo_mode:
            content.append("MODE: ", style="dim")
            content.append("DEMO\n", style="yellow bold")
            content.append("(Add API key for live data)", style="dim italic")
        else:
            content.append("MODE: ", style="dim")
            content.append("LIVE\n", style="green bold")
        
        return Panel(
            content,
            title="STATS",
            title_align="left",
            border_style="cyan",
            box=box.ROUNDED
        )
    
    def _make_status_bar(self) -> Panel:
        """Create bottom status bar"""
        table = Table.grid(expand=True)
        table.add_column(justify="left", ratio=1)
        table.add_column(justify="center", ratio=1)
        table.add_column(justify="right", ratio=1)
        
        status = Text()
        status.append("ACNT: ", style="dim")
        status.append(f"@{self.stats.username}", style="cyan")
        
        tweets_info = Text()
        tweets_info.append("TWEETS: ", style="dim")
        tweets_info.append(f"{self.stats.total_tweets:,}", style="green")
        
        period_info = Text()
        tweets_per_day = self.stats.today_tweets
        period_info.append("TODAY: ", style="dim")
        period_info.append(f"{tweets_per_day} tweets", style="cyan")
        
        table.add_row(status, tweets_info, period_info)
        
        return Panel(table, box=box.SIMPLE, style="dim")
    
    def _make_layout(self) -> Layout:
        """Create the main layout"""
        layout = Layout()
        
        # Main structure
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="stats", size=4),
            Layout(name="body", ratio=1),
            Layout(name="log", size=12),
            Layout(name="footer", size=3)
        )
        
        # Body split into main content and sidebar
        layout["body"].split_row(
            Layout(name="tweets", ratio=3),
            Layout(name="sidebar", ratio=1)
        )
        
        return layout
    
    def _update_layout(self, layout: Layout):
        """Update all layout components"""
        layout["header"].update(self._make_header())
        layout["stats"].update(self._make_stats_panel())
        layout["tweets"].update(self._make_tweets_table())
        layout["sidebar"].update(self._make_stats_sidebar())
        layout["log"].update(self._make_activity_log())
        layout["footer"].update(self._make_status_bar())
    
    def _update_thread(self):
        """Background thread for fetching updates"""
        while self.running:
            try:
                self._fetch_tweets()
            except Exception as e:
                self._log(f"[red]Error: {str(e)}[/red]")
            
            # Sleep in small intervals to allow quick shutdown
            for _ in range(self.update_interval * 2):
                if not self.running:
                    break
                time.sleep(0.5)

    def _input_thread(self):
        """Keyboard input thread (for log scrolling)."""
        try:
            import msvcrt  # Windows-only
        except Exception:
            return

        while self.running:
            try:
                if msvcrt.kbhit():
                    ch = msvcrt.getwch()
                    # Arrow keys come as a prefix char then a code.
                    if ch in ("\x00", "\xe0"):
                        key = msvcrt.getwch()
                        if key == "H":  # Up
                            self._log_scroll_offset += 1
                        elif key == "P":  # Down
                            self._log_scroll_offset = max(0, self._log_scroll_offset - 1)
                        elif key == "I":  # PgUp
                            self._log_scroll_offset += 5
                        elif key == "Q":  # PgDn
                            self._log_scroll_offset = max(0, self._log_scroll_offset - 5)
                        elif key == "G":  # Home
                            self._log_scroll_offset = 10_000_000
                        elif key == "O":  # End
                            self._log_scroll_offset = 0
                time.sleep(0.05)
            except Exception:
                time.sleep(0.1)
    
    def run(self):
        """Run the monitor"""
        layout = self._make_layout()
        
        # Start background update thread
        update_thread = threading.Thread(target=self._update_thread, daemon=True)
        update_thread.start()

        input_thread = threading.Thread(target=self._input_thread, daemon=True)
        input_thread.start()
        
        self._log("[green]Monitor started. Press Ctrl+C to exit.[/green]")
        
        try:
            with Live(layout, console=self.console, refresh_per_second=2, screen=True):
                while self.running:
                    self._update_layout(layout)
                    time.sleep(0.5)
        except KeyboardInterrupt:
            self.running = False
            self.console.print("\n[yellow]Monitor stopped.[/yellow]")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="X/Twitter Tweet Monitor")
    parser.add_argument(
        "-u", "--username",
        help="Twitter username to monitor (without @)",
        default=os.getenv("MONITOR_USERNAME", "elonmusk")
    )
    parser.add_argument(
        "-i", "--interval",
        type=int,
        help="Update interval in seconds",
        default=int(os.getenv("UPDATE_INTERVAL", 60))
    )
    parser.add_argument(
        "--range-start",
        help="Custom range start (e.g. '2026-01-26 09:00' or '2026-01-26T09:00')",
        default=os.getenv("RANGE_START")
    )
    parser.add_argument(
        "--range-end",
        help="Custom range end (e.g. '2026-01-26 18:00' or '2026-01-26T18:00')",
        default=os.getenv("RANGE_END")
    )
    
    args = parser.parse_args()

    def _parse_dt(value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        v = value.strip().replace("T", " ")
        # allow seconds optionally
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
            try:
                return datetime.strptime(v, fmt)
            except ValueError:
                pass
        # last resort: fromisoformat
        try:
            return datetime.fromisoformat(value.strip())
        except Exception:
            return None

    range_start = _parse_dt(args.range_start)
    range_end = _parse_dt(args.range_end)
    
    console = Console()
    console.print(Panel.fit(
        "[bold cyan]X Tweet Monitor[/bold cyan]\n"
        f"Monitoring: [green]@{args.username}[/green]\n"
        f"Update interval: [yellow]{args.interval}s[/yellow]",
        title="Starting",
        border_style="cyan"
    ))
    
    time.sleep(1)
    
    monitor = TweetMonitor(
        username=args.username,
        update_interval=args.interval,
        range_start=range_start,
        range_end=range_end,
    )
    monitor.run()


if __name__ == "__main__":
    main()
