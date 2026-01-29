import React from 'react';

export default function Panel({ title, right, children, className = '' }) {
  return (
    <section className={`border border-white/15 rounded-md bg-black ${className}`}>
      {(title || right) && (
        <div className="px-4 py-3 border-b border-white/10 flex items-center justify-between">
          <h2 className="text-sm font-medium">{title}</h2>
          {right ? <div className="text-sm text-white/70">{right}</div> : null}
        </div>
      )}
      <div className="p-4">{children}</div>
    </section>
  );
}

