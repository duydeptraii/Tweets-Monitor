import React, { useMemo, useState } from 'react';
import Header from './components/Header';
import FeedPanel from './components/FeedPanel';
import Panel from './components/Panel';
import { useMockData } from './hooks/useMockData';

function toLocalInputValue(date) {
  const pad = (n) => String(n).padStart(2, '0');
  const yyyy = date.getFullYear();
  const mm = pad(date.getMonth() + 1);
  const dd = pad(date.getDate());
  const hh = pad(date.getHours());
  const min = pad(date.getMinutes());
  return `${yyyy}-${mm}-${dd}T${hh}:${min}`;
}

function clampDateRange(start, end) {
  const s = new Date(start);
  const e = new Date(end);
  if (Number.isNaN(s.getTime()) || Number.isNaN(e.getTime())) return null;
  if (s > e) return { start: end, end: start };
  return { start, end };
}

function App() {
  const { tweets } = useMockData();
  const now = new Date();
  const defaultEnd = toLocalInputValue(now);
  const defaultStart = toLocalInputValue(new Date(now.getTime() - 24 * 60 * 60 * 1000));
  const [startLocal, setStartLocal] = useState(defaultStart);
  const [endLocal, setEndLocal] = useState(defaultEnd);

  const range = useMemo(() => clampDateRange(startLocal, endLocal), [startLocal, endLocal]);

  const filteredTweets = useMemo(() => {
    if (!range) return [];
    const startMs = new Date(range.start).getTime();
    const endMs = new Date(range.end).getTime();
    return tweets.filter((t) => {
      const ms = new Date(t.createdAt).getTime();
      return ms >= startMs && ms <= endMs;
    });
  }, [range, tweets]);

  const summary = useMemo(() => {
    if (!range) return { total: 0, dailyAverage: 0, days: 0 };
    const startMs = new Date(range.start).getTime();
    const endMs = new Date(range.end).getTime();
    const days = Math.max((endMs - startMs) / (24 * 60 * 60 * 1000), 1 / 1440); // min 1 minute
    const total = filteredTweets.length;
    const dailyAverage = total / days;
    return { total, dailyAverage, days };
  }, [filteredTweets.length, range]);

  return (
    <div className="h-full w-full flex flex-col bg-black text-white">
      <Header />
      
      <main className="flex-1 p-6 grid grid-cols-12 gap-6 min-h-0">
        <div className="col-span-12 lg:col-span-8 min-h-0 flex flex-col gap-4">
          <Panel title="Time range">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <label className="text-sm">
                <div className="text-xs text-white/70 mb-1">Start</div>
                <input
                  type="datetime-local"
                  value={startLocal}
                  onChange={(e) => setStartLocal(e.target.value)}
                  className="w-full bg-black border border-white/20 rounded-md px-3 py-2 text-sm outline-none focus:border-white/50"
                />
              </label>
              <label className="text-sm">
                <div className="text-xs text-white/70 mb-1">End</div>
                <input
                  type="datetime-local"
                  value={endLocal}
                  onChange={(e) => setEndLocal(e.target.value)}
                  className="w-full bg-black border border-white/20 rounded-md px-3 py-2 text-sm outline-none focus:border-white/50"
                />
              </label>
            </div>
            {!range ? (
              <div className="mt-3 text-sm text-white/70">Choose a valid start and end time.</div>
            ) : (
              <div className="mt-3 text-xs text-white/60">
                Showing tweets from <span className="text-white/80">{new Date(range.start).toLocaleString()}</span> to{' '}
                <span className="text-white/80">{new Date(range.end).toLocaleString()}</span>.
              </div>
            )}
          </Panel>

          <div className="flex-1 min-h-0">
            <FeedPanel tweets={filteredTweets} />
          </div>
        </div>

        <div className="col-span-12 lg:col-span-4 min-h-0 flex flex-col gap-4">
          <Panel title="Summary">
            <div className="space-y-3">
              <div className="flex items-center justify-between border-b border-white/10 pb-2">
                <div className="text-sm text-white/70">Total tweets</div>
                <div className="text-lg font-semibold">{summary.total}</div>
              </div>
              <div className="flex items-center justify-between">
                <div className="text-sm text-white/70">Daily average</div>
                <div className="text-lg font-semibold">{summary.dailyAverage.toFixed(1)}</div>
              </div>
              <div className="text-xs text-white/60">
                Based on a {summary.days.toFixed(2)} day window.
              </div>
            </div>
          </Panel>

          <Panel title="Notes">
            <div className="text-sm text-white/70 space-y-2">
              <p>This is mock data only.</p>
              <p>New tweets are simulated every few seconds.</p>
            </div>
          </Panel>
        </div>
      </main>
    </div>
  );
}

export default App;
