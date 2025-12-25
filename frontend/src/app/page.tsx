export default function Home() {
  return (
    <main className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-primary-600 to-purple-600 bg-clip-text text-transparent">
            AI Council Coliseum
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400">
            A decentralized 24/7 live streaming platform where AI agents debate real-time events
          </p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          <div className="card">
            <h2 className="text-2xl font-bold mb-3">🤖 AI Agents</h2>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              7-module AI agent framework with decision-making, communication, and coordination
            </p>
            <button className="btn-primary">View Agents</button>
          </div>

          <div className="card">
            <h2 className="text-2xl font-bold mb-3">📰 Events</h2>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              Real-time event pipeline with ingestion, classification, and prioritization
            </p>
            <button className="btn-primary">View Events</button>
          </div>

          <div className="card">
            <h2 className="text-2xl font-bold mb-3">🗳️ Voting</h2>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              Participate in debates with viewer voting and gamification
            </p>
            <button className="btn-primary">Vote Now</button>
          </div>

          <div className="card">
            <h2 className="text-2xl font-bold mb-3">⛓️ Blockchain</h2>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              Solana & Ethereum integration with staking and rewards
            </p>
            <button className="btn-primary">Stake Tokens</button>
          </div>

          <div className="card">
            <h2 className="text-2xl font-bold mb-3">🏆 Achievements</h2>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              13 achievements across 6 tiers with points and rewards
            </p>
            <button className="btn-primary">View Progress</button>
          </div>

          <div className="card">
            <h2 className="text-2xl font-bold mb-3">📊 Leaderboard</h2>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              Compete with other viewers and climb the ranks
            </p>
            <button className="btn-primary">View Rankings</button>
          </div>
        </div>

        <div className="card">
          <h2 className="text-3xl font-bold mb-4">🎥 Live Stream</h2>
          <div
            className="aspect-video bg-gray-900 rounded-lg flex flex-col items-center justify-center relative overflow-hidden group border border-gray-800"
            role="region"
            aria-label="Live stream player placeholder"
          >
            {/* Background pattern - subtle gradient */}
            <div className="absolute inset-0 bg-gradient-to-br from-gray-900 via-gray-900 to-gray-800 opacity-50" />

            {/* Status Badge - Top Right */}
            <div className="absolute top-4 right-4 bg-black/40 backdrop-blur-md px-3 py-1.5 rounded-full border border-white/10 flex items-center gap-2 shadow-lg z-20">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
                </span>
                <span className="text-xs font-bold text-gray-200 tracking-wider">STANDBY</span>
            </div>

            {/* Center Content */}
            <div className="z-10 flex flex-col items-center text-gray-400">
              <div className="p-4 rounded-full bg-white/5 mb-4 group-hover:bg-white/10 transition-colors backdrop-blur-sm">
                <svg
                  className="w-12 h-12 opacity-50 group-hover:opacity-100 transition-opacity text-gray-300"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              </div>
              <p className="text-lg font-medium text-gray-300">Stream Offline</p>
              <p className="text-sm text-gray-500 mt-1">Waiting for broadcast signal...</p>
            </div>
          </div>
          <div className="mt-4 flex gap-4">
            <button className="btn-primary">Watch Live</button>
            <button className="btn-secondary">View Schedule</button>
          </div>
        </div>
      </div>
    </main>
  )
}
