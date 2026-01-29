import React from 'react';

const Header = () => {
  const now = new Date();
  return (
    <header className="sticky top-0 z-50 border-b border-white/10 bg-black">
      <div className="px-6 h-14 flex items-center justify-between">
        <div className="text-base font-semibold tracking-tight">Tweet Monitor</div>
        <div className="text-sm text-white/70">{now.toLocaleString()}</div>
      </div>
    </header>
  );
};

export default Header;
