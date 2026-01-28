import os
import threading
import time
from datetime import datetime
from queue import Queue, Empty
from typing import Optional, List

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText

# Reuse the existing API implementation
from tweet_monitor import TwitterAPI, Tweet


def parse_dt(value: str) -> Optional[datetime]:
    v = (value or "").strip()
    if not v:
        return None
    v2 = v.replace("T", " ")
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(v2, fmt)
        except ValueError:
            pass
    try:
        return datetime.fromisoformat(v)
    except Exception:
        return None


class MonitorGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("X Tweet Monitor (Desktop)")
        self.root.geometry("1100x720")
        self.root.minsize(980, 650)

        self.api: Optional[TwitterAPI] = None
        self.user_id: Optional[str] = None
        self.running = False
        self.monitoring_start: Optional[datetime] = None
        self.range_count: Optional[int] = None

        self._tweet_ids = set()
        self._poll_thread: Optional[threading.Thread] = None
        self._range_thread: Optional[threading.Thread] = None
        self._q: "Queue[dict]" = Queue()

        self._build_ui()
        self._drain_queue()

    def _build_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)

        top = ttk.Frame(self.root, padding=10)
        top.grid(row=0, column=0, sticky="ew")
        top.columnconfigure(9, weight=1)

        self.mode_var = tk.StringVar(value="MODE: (not connected)")
        self.mode_label = ttk.Label(top, textvariable=self.mode_var, font=("Segoe UI", 11, "bold"))
        self.mode_label.grid(row=0, column=0, sticky="w", padx=(0, 12))

        ttk.Label(top, text="Username (@):").grid(row=0, column=1, sticky="w")
        self.username_var = tk.StringVar(value=os.getenv("MONITOR_USERNAME", "elonmusk"))
        ttk.Entry(top, textvariable=self.username_var, width=18).grid(row=0, column=2, sticky="w", padx=(6, 14))

        ttk.Label(top, text="Interval (s):").grid(row=0, column=3, sticky="w")
        self.interval_var = tk.StringVar(value=os.getenv("UPDATE_INTERVAL", "60"))
        ttk.Entry(top, textvariable=self.interval_var, width=8).grid(row=0, column=4, sticky="w", padx=(6, 14))

        ttk.Label(top, text="Range start:").grid(row=0, column=5, sticky="w")
        self.range_start_var = tk.StringVar(value=os.getenv("RANGE_START", ""))
        ttk.Entry(top, textvariable=self.range_start_var, width=18).grid(row=0, column=6, sticky="w", padx=(6, 14))

        ttk.Label(top, text="Range end:").grid(row=0, column=7, sticky="w")
        self.range_end_var = tk.StringVar(value=os.getenv("RANGE_END", ""))
        ttk.Entry(top, textvariable=self.range_end_var, width=18).grid(row=0, column=8, sticky="w", padx=(6, 14))

        buttons = ttk.Frame(top)
        buttons.grid(row=0, column=9, sticky="e")
        self.start_btn = ttk.Button(buttons, text="Start", command=self.start)
        self.stop_btn = ttk.Button(buttons, text="Stop", command=self.stop, state="disabled")
        self.count_btn = ttk.Button(buttons, text="Count range", command=self.count_range)
        self.start_btn.grid(row=0, column=0, padx=(0, 8))
        self.stop_btn.grid(row=0, column=1, padx=(0, 8))
        self.count_btn.grid(row=0, column=2)

        stats = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        stats.grid(row=1, column=0, sticky="ew")
        for i in range(10):
            stats.columnconfigure(i, weight=1)

        self.total_var = tk.StringVar(value="Total: -")
        self.today_var = tk.StringVar(value="Today: -")
        self.period_var = tk.StringVar(value="Session: -")
        self.followers_var = tk.StringVar(value="Followers: -")
        self.following_var = tk.StringVar(value="Following: -")
        self.last_update_var = tk.StringVar(value="Last update: -")
        self.range_var = tk.StringVar(value="Range count: -")

        ttk.Label(stats, textvariable=self.total_var, font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(stats, textvariable=self.today_var, font=("Segoe UI", 10, "bold")).grid(row=0, column=1, sticky="w")
        ttk.Label(stats, textvariable=self.period_var, font=("Segoe UI", 10, "bold")).grid(row=0, column=2, sticky="w")
        ttk.Label(stats, textvariable=self.followers_var).grid(row=0, column=3, sticky="w")
        ttk.Label(stats, textvariable=self.following_var).grid(row=0, column=4, sticky="w")
        ttk.Label(stats, textvariable=self.range_var).grid(row=0, column=5, sticky="w")
        ttk.Label(stats, textvariable=self.last_update_var).grid(row=0, column=9, sticky="e")

        body = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        body.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))

        tweets_frame = ttk.Labelframe(body, text="Recent tweets / replies / reposts")
        body.add(tweets_frame, weight=3)
        tweets_frame.rowconfigure(0, weight=1)
        tweets_frame.columnconfigure(0, weight=1)

        columns = ("time", "type", "text", "rt", "likes", "replies")
        self.tree = ttk.Treeview(tweets_frame, columns=columns, show="headings", height=12)
        self.tree.heading("time", text="Time")
        self.tree.heading("type", text="Type")
        self.tree.heading("text", text="Text")
        self.tree.heading("rt", text="RT")
        self.tree.heading("likes", text="Likes")
        self.tree.heading("replies", text="Replies")
        self.tree.column("time", width=90, anchor="w")
        self.tree.column("type", width=80, anchor="w")
        self.tree.column("text", width=640, anchor="w")
        self.tree.column("rt", width=80, anchor="e")
        self.tree.column("likes", width=90, anchor="e")
        self.tree.column("replies", width=90, anchor="e")

        vsb = ttk.Scrollbar(tweets_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        log_frame = ttk.Labelframe(body, text="Activity log (scrollable)")
        body.add(log_frame, weight=2)
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        self.log = ScrolledText(log_frame, wrap="word", height=10)
        self.log.grid(row=0, column=0, sticky="nsew")
        self._log_line("Ready.")

    def _log_line(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log.insert("end", f"{ts}  {msg}\n")
        self.log.see("end")

    def start(self):
        if self.running:
            return
        username = self.username_var.get().strip().lstrip("@")
        if not username:
            messagebox.showerror("Missing username", "Please enter a username to monitor.")
            return
        try:
            interval = int(self.interval_var.get().strip() or "60")
            interval = max(5, interval)
        except ValueError:
            messagebox.showerror("Invalid interval", "Interval must be a number (seconds).")
            return

        try:
            self.api = TwitterAPI()
            info = self.api.get_user_info(username)
            self.user_id = info.get("id") if info else None
            if not self.user_id:
                raise RuntimeError("Could not fetch user info.")
            self.monitoring_start = datetime.now()
            self._tweet_ids.clear()
            self.range_count = None

            self.mode_var.set("MODE: DEMO (no API key)" if self.api.demo_mode else "MODE: LIVE (API connected)")
            self._log_line(f"Connected to @{username}. Starting monitor.")
        except Exception as e:
            messagebox.showerror("Failed to start", str(e))
            return

        self.running = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")

        self._poll_thread = threading.Thread(target=self._poll_loop, args=(username, interval), daemon=True)
        self._poll_thread.start()

    def stop(self):
        if not self.running:
            return
        self.running = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self._log_line("Stopped.")

    def _poll_loop(self, username: str, interval: int):
        assert self.api and self.user_id
        cycle = 0
        while self.running:
            cycle += 1
            try:
                tweets: List[Tweet] = self.api.get_recent_tweets(self.user_id, max_results=20)
                info = None
                if (cycle % max(1, int(300 / max(1, interval)))) == 0 or cycle == 1:
                    info = self.api.get_user_info(username)

                now = datetime.now()
                today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                monitoring_start = self.monitoring_start or now

                new = []
                for t in tweets:
                    if t.id not in self._tweet_ids:
                        self._tweet_ids.add(t.id)
                        new.append(t)

                today_count = sum(1 for t in tweets if t.created_at >= today_start)
                period_count = sum(1 for t in tweets if t.created_at >= monitoring_start)

                payload = {
                    "type": "update",
                    "now": now,
                    "tweets": tweets,
                    "new": new,
                    "today": today_count,
                    "period": period_count,
                    "info": info,
                }
                self._q.put(payload)
            except Exception as e:
                self._q.put({"type": "error", "error": str(e)})

            for _ in range(int(interval * 10)):
                if not self.running:
                    break
                time.sleep(0.1)

    def count_range(self):
        if not self.api or not self.user_id:
            messagebox.showinfo("Not running", "Start monitoring first (so we know the user id).")
            return

        start = parse_dt(self.range_start_var.get())
        end = parse_dt(self.range_end_var.get())
        if not start or not end:
            messagebox.showerror(
                "Invalid range",
                "Enter start/end like '2026-01-26 09:00' and '2026-01-26 18:00'.",
            )
            return
        if start >= end:
            messagebox.showerror("Invalid range", "Range start must be before range end.")
            return

        self.range_var.set("Range count: ...")
        self._log_line(f"Counting tweets in range {start} → {end} (may take a moment)...")

        def worker():
            try:
                count = self.api.count_tweets_in_range(self.user_id, start, end)
                self._q.put({"type": "range", "count": count})
            except Exception as e:
                self._q.put({"type": "error", "error": str(e)})

        if self._range_thread and self._range_thread.is_alive():
            return
        self._range_thread = threading.Thread(target=worker, daemon=True)
        self._range_thread.start()

    def _drain_queue(self):
        try:
            while True:
                msg = self._q.get_nowait()
                t = msg.get("type")
                if t == "update":
                    self._apply_update(msg)
                elif t == "range":
                    self.range_count = msg.get("count")
                    self.range_var.set(f"Range count: {self.range_count}")
                    self._log_line(f"Range count: {self.range_count}")
                elif t == "error":
                    self._log_line(f"Error: {msg.get('error')}")
        except Empty:
            pass
        self.root.after(100, self._drain_queue)

    def _apply_update(self, msg: dict):
        now: datetime = msg["now"]
        tweets: List[Tweet] = msg["tweets"]
        new: List[Tweet] = msg["new"]
        today = msg["today"]
        period = msg["period"]
        info = msg.get("info")

        if info:
            self.total_var.set(f"Total: {info.get('tweets', '-'):,}" if isinstance(info.get("tweets"), int) else f"Total: {info.get('tweets', '-')}")
            self.followers_var.set(f"Followers: {info.get('followers', '-'):,}" if isinstance(info.get("followers"), int) else f"Followers: {info.get('followers', '-')}")
            self.following_var.set(f"Following: {info.get('following', '-'):,}" if isinstance(info.get("following"), int) else f"Following: {info.get('following', '-')}")

        self.today_var.set(f"Today: {today}")
        self.period_var.set(f"Session: {period}")
        self.last_update_var.set(f"Last update: {now.strftime('%H:%M:%S')}")

        if new:
            for t in new:
                self._log_line(f"New {t.kind.upper()}: {t.text[:120].replace('\\n', ' ')}")

        # refresh table (keep it simple and stable)
        for item in self.tree.get_children():
            self.tree.delete(item)
        for t in sorted(tweets, key=lambda x: x.created_at, reverse=True)[:50]:
            self.tree.insert(
                "",
                "end",
                values=(
                    t.created_at.strftime("%H:%M:%S"),
                    t.kind.upper(),
                    t.text.replace("\n", " "),
                    t.retweet_count,
                    t.like_count,
                    t.reply_count,
                ),
            )


def main():
    root = tk.Tk()
    try:
        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")
        elif "clam" in style.theme_names():
            style.theme_use("clam")
    except Exception:
        pass

    app = MonitorGUI(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.stop(), root.destroy()))
    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        try:
            messagebox.showerror("Fatal error", str(e))
        except Exception:
            raise
