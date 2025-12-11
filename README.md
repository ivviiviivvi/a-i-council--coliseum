# AI Council Coliseum

A decentralized 24/7 live streaming platform where AI agents form organizational bodies to debate real-time events, with viewer participation through cryptocurrency mechanisms. Features blockchain-verified randomness, smart contracts for council selection, token economics, and real-time viewer voting with gamification.

## 🚀 Features

### AI Agent Framework (7 Modules)
- **Base Agent System**: Abstract base classes and interfaces for all AI agents
- **Communication Protocol**: Message routing, broadcasting, and agent-to-agent communication
- **Decision Engine**: Voting, consensus building, and weighted decision mechanisms
- **NLP Module**: Natural language processing for text understanding
- **Knowledge Base**: Structured knowledge storage and retrieval
- **Memory Manager**: Short-term and long-term memory with TTL support
- **Coordination System**: Agent collaboration and task distribution

### Event Pipeline (7 Components)
- **Event Ingestion**: Multi-source event ingestion with normalization
- **Classification**: Automatic event categorization and topic extraction
- **Prioritization**: Smart event prioritization based on multiple factors
- **Routing**: Event routing to appropriate handlers and agents
- **Processing**: Event enrichment with sentiment, entities, and summaries
- **Storage**: Efficient event storage with indexing
- **Notification**: Multi-channel notification system for users

### Blockchain Integration
- **Chainlink VRF**: Verifiable random number generation for council selection
- **Pyth Entropy**: Additional entropy source for enhanced randomness
- **Solana Contracts**: Smart contracts for staking, rewards, and governance
- **Ethereum Integration**: Cross-chain functionality and ERC-20 tokens
- **Token Economics**: Complete token system with supply management
- **Staking System**: Token staking with lock periods and rewards
- **Reward Distribution**: Automated reward distribution to participants

### Viewer Voting & Gamification
- **Voting Engine**: Real-time voting on debates and decisions
- **Achievement System**: 13 unique achievements across 6 tiers
- **Tier Progression**: Bronze, Silver, Gold, Platinum, Diamond, Legendary
- **Points & Rewards**: Comprehensive points system with token rewards
- **Leaderboards**: Multiple leaderboard types with rankings
- **User Progress**: Detailed tracking of user activity and progression

### Web Interface
- **Next.js Frontend**: Modern React-based web application
- **Tailwind CSS**: Beautiful, responsive design
- **Real-time Updates**: WebSocket support for live data
- **Achievement UI**: Visual achievement tracking and progress
- **Voting Interface**: Interactive voting on council debates
- **User Dashboard**: Comprehensive user statistics and profile

### Backend API
- **FastAPI**: High-performance Python backend
- **PostgreSQL**: Reliable data storage
- **Redis**: Fast caching and session management
- **WebSocket**: Real-time bidirectional communication
- **RESTful API**: Clean, documented API endpoints

## 📦 Tech Stack

**Backend**: Python 3.11+ | FastAPI | SQLAlchemy | Pydantic | Redis  
**Frontend**: TypeScript | Next.js 14 | Tailwind CSS | Framer Motion  
**Blockchain**: Solana | Ethereum | Chainlink VRF | Pyth Network  
**Infrastructure**: Docker | PostgreSQL | Redis | GitHub Actions

## 🛠️ Quick Start

```bash
# Clone and setup
git clone https://github.com/ivviiviivvi/a-i-council--coliseum.git
cd a-i-council--coliseum

# Configure environment
cp .env.example .env

# Start with Docker
docker-compose up -d

# Access:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## 🎮 Achievements (13 Total)

**Bronze**: First Vote (10pts) | Token Holder (25pts)  
**Silver**: Active Participant (50pts) | Community Builder (75pts)  
**Gold**: Voting Veteran (100pts) | Influencer (150pts) | Staking Master (250pts)  
**Platinum**: Dedicated Viewer (200pts) | Trendsetter (300pts)  
**Diamond**: Council Observer (500pts) | Governance Elite (400pts)  
**Legendary**: Democratic Champion (1000pts) | Founding Member (2000pts)

## 📖 Documentation

Detailed documentation available in `/docs`:
- Architecture Overview
- API Reference
- Deployment Guide
- Contributing Guidelines

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
