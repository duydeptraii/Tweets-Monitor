import { useState, useEffect } from 'react';

const NAMES = ['elonmusk', 'NASA', 'spacex', 'tesla', 'research', 'news', 'dev', 'tech'];
const MESSAGES = [
  "Shipping a small update today.",
  "New post is live.",
  "Quick note: working on improvements.",
  "Sharing a link I found useful.",
  "Short update from today.",
  "Testing a few ideas.",
  "Thanks for the feedback.",
  "New release is rolling out.",
];

function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function generateSeedTweets(count = 30) {
  const now = Date.now();
  return Array.from({ length: count }, (_, i) => {
    // spread across the last 7 days
    const offsetMs = randomInt(0, 7 * 24 * 60 * 60 * 1000);
    const createdAt = new Date(now - offsetMs).toISOString();
    return {
      id: `seed_${now}_${i}`,
      username: NAMES[randomInt(0, NAMES.length - 1)],
      text: MESSAGES[randomInt(0, MESSAGES.length - 1)],
      createdAt,
      likes: randomInt(0, 500),
      retweets: randomInt(0, 250),
    };
  }).sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
}

export const useMockData = () => {
  const [tweets, setTweets] = useState(() => generateSeedTweets(40));

  useEffect(() => {
    // Simulate incoming tweets
    const tweetInterval = setInterval(() => {
      if (Math.random() > 0.6) {
        const newTweet = {
          id: Date.now().toString(),
          username: NAMES[Math.floor(Math.random() * NAMES.length)],
          text: MESSAGES[Math.floor(Math.random() * MESSAGES.length)],
          createdAt: new Date().toISOString(),
          likes: Math.floor(Math.random() * 1000),
          retweets: Math.floor(Math.random() * 500)
        };

        setTweets(prev => [newTweet, ...prev].slice(0, 50));
      }
    }, 3000);

    return () => {
      clearInterval(tweetInterval);
    };
  }, []);

  return { tweets };
};
