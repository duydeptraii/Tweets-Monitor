import React, { useEffect, useRef } from 'react';
import Panel from './Panel';

const FeedPanel = ({ tweets }) => {
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = 0;
    }
  }, [tweets]);

  return (
    <Panel
      title="Tweets"
      className="h-full flex flex-col overflow-hidden"
      right={<span className="text-xs">Showing {tweets.length}</span>}
    >
      <div className="flex-1 overflow-y-auto space-y-3 text-sm" ref={scrollRef}>
        {tweets.length === 0 ? (
          <div className="text-white/70 text-sm">No tweets in this time range.</div>
        ) : (
          tweets.map((tweet) => (
            <article key={tweet.id} className="border border-white/10 rounded-md p-3">
              <div className="flex items-center justify-between gap-4">
                <div className="text-sm font-medium">@{tweet.username}</div>
                <div className="text-xs text-white/60">
                  {new Date(tweet.createdAt).toLocaleString()}
                </div>
              </div>
              <p className="mt-2 text-sm text-white/90 leading-relaxed">{tweet.text}</p>
              <div className="mt-2 text-xs text-white/60 flex gap-4">
                <span>Likes {tweet.likes}</span>
                <span>Reposts {tweet.retweets}</span>
              </div>
            </article>
          ))
        )}
      </div>
    </Panel>
  );
};

export default FeedPanel;
