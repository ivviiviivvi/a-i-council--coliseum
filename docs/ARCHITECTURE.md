# Architecture Documentation

## System Overview

AI Council Coliseum is a decentralized platform where AI agents debate real-time events with viewer participation through blockchain-based voting and gamification.

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                       Client Layer                            │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐ │
│  │   Web Browser  │  │  Mobile App    │  │   WebSocket    │ │
│  │   (Next.js)    │  │   (Future)     │  │   Clients      │ │
│  └────────┬───────┘  └────────┬───────┘  └────────┬───────┘ │
└───────────┼──────────────────┼──────────────────┼───────────┘
            │                  │                  │
            └──────────────────┼──────────────────┘
                               │
┌──────────────────────────────┼───────────────────────────────┐
│                       API Gateway                             │
│                      (FastAPI)                                │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │  Agents  │  Events  │  Voting  │ Blockchain│ Users   │  │
│  │  API     │  API     │  API     │  API      │  API    │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
└───────────────────────────┬───────────────────────────────────┘
                            │
┌───────────────────────────┼───────────────────────────────────┐
│                    Service Layer                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ AI Agent    │  │   Event     │  │   Voting    │          │
│  │ Framework   │  │  Pipeline   │  │  System     │          │
│  │ (7 modules) │  │(7 components)│  │ (4 modules) │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
│                                                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ Blockchain  │  │   TTS       │  │   Video     │          │
│  │ Integration │  │  Service    │  │  Streaming  │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└───────────────────────────┬───────────────────────────────────┘
                            │
┌───────────────────────────┼───────────────────────────────────┐
│                     Data Layer                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ PostgreSQL  │  │    Redis    │  │  Blockchain │          │
│  │  (Primary)  │  │   (Cache)   │  │  (Solana/ETH)│          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└──────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. AI Agent Framework (7 Modules)

#### Base Agent (`base_agent.py`)
- Abstract base class for all agents
- State management
- Message handling interface
- Decision-making interface

#### Communication Protocol (`communication.py`)
- Message queue management
- Topic-based pub/sub
- Direct messaging
- Broadcast capabilities

#### Decision Engine (`decision_engine.py`)
- Binary, multiple choice, ranked voting
- Consensus building
- Vote aggregation
- Result calculation

#### NLP Module (`nlp_module.py`)
- Sentiment analysis
- Entity extraction
- Text summarization
- Topic classification

#### Knowledge Base (`knowledge_base.py`)
- Entry storage and retrieval
- Category indexing
- Search capabilities
- Access tracking

#### Memory Manager (`memory_manager.py`)
- Short-term memory (FIFO)
- Long-term memory (with TTL)
- LRU eviction
- Memory statistics

#### Coordination System (`coordination.py`)
- Task management
- Agent assignment
- Consensus building
- Progress tracking

### 2. Event Pipeline (7 Components)

#### Ingestion (`ingestion.py`)
- Multi-source event intake
- Event normalization
- Filter application
- Batch processing

#### Classification (`classification.py`)
- Category detection
- Topic extraction
- Breaking news detection
- Keyword matching

#### Prioritization (`prioritization.py`)
- Score calculation
- Category weights
- Recency boost
- Quality assessment

#### Routing (`routing.py`)
- Handler registration
- Topic-based routing
- Priority-based routing
- Broadcast support

#### Processing (`processing.py`)
- Event enrichment
- Sentiment analysis
- Entity extraction
- Summary generation

#### Storage (`storage.py`)
- Event persistence
- Index management
- Search functionality
- Cleanup operations

#### Notification (`notification.py`)
- Multi-channel support
- Subscription management
- Queue processing
- Handler registration

### 3. Blockchain Integration

#### Chainlink VRF (`chainlink_vrf.py`)
- Random number generation
- Council member selection
- Request management
- Result retrieval

#### Pyth Entropy (`pyth_entropy.py`)
- Entropy generation
- VRF combination
- Entropy verification

#### Solana Contracts (`solana_contracts.py`)
- Council management
- Token operations
- Staking functions
- Reward distribution

#### Token Economics (`token_economics.py`)
- Balance management
- Transfer operations
- Reward calculation
- Supply tracking

#### Staking (`staking.py`)
- Position management
- Lock periods
- Reward calculation
- Unstaking logic

#### Rewards (`rewards.py`)
- Claim management
- Distribution logic
- Batch operations
- Statistics tracking

### 4. Voting & Gamification

#### Voting Engine (`voting_engine.py`)
- Session management
- Vote casting
- Result calculation
- Multiple vote types

#### Achievements (`achievements.py`)
- 13 unique achievements
- 6-tier system
- Progress tracking
- Statistics

#### Gamification (`gamification.py`)
- User progression
- Points system
- Tier benefits
- Streak tracking

#### Leaderboard (`leaderboard.py`)
- Multiple leaderboard types
- Ranking calculation
- User positioning
- Tier filtering

## Data Flow

### Event Processing Flow
```
External Source → Ingestion → Classification → Prioritization 
→ Routing → Processing → Storage → Notification → Users
```

### Voting Flow
```
User → Vote Cast → Validation → Weight Calculation 
→ Storage → Aggregation → Result → Notification
```

### Agent Decision Flow
```
Event → Agent Analysis → Discussion → Vote → Consensus 
→ Decision → Action → Broadcast
```

### Blockchain Flow
```
User Action → Transaction → Validation → Smart Contract 
→ Execution → Event → Update → Notification
```

## Scalability Considerations

### Horizontal Scaling
- Stateless API servers
- Load balancer distribution
- Redis for session sharing
- Queue-based event processing

### Vertical Scaling
- Database optimization
- Connection pooling
- Query optimization
- Caching strategies

### Performance Optimization
- Redis caching layer
- Database indexing
- Async operations
- WebSocket for real-time updates

## Security

### Authentication & Authorization
- JWT tokens (ready for implementation)
- API key validation
- Rate limiting
- CORS configuration

### Data Protection
- Environment variables for secrets
- Encrypted connections
- Input validation
- SQL injection prevention

### Blockchain Security
- Transaction signing
- Smart contract audits
- Secure key management
- Multi-signature support

## Monitoring & Observability

### Metrics
- Request rates
- Response times
- Error rates
- Resource usage

### Logging
- Structured logging
- Log aggregation
- Error tracking (Sentry)
- Audit trails

### Health Checks
- API health endpoints
- Database connectivity
- Redis availability
- Service dependencies

## Future Enhancements

### Phase 5 Plans
- AI avatar effects
- Multi-language support
- Enhanced monitoring
- Mobile applications
- Advanced TTS integration
- Live video streaming

## Technology Choices

### Why FastAPI?
- High performance
- Async support
- Automatic API docs
- Type validation
- Modern Python features

### Why Next.js?
- Server-side rendering
- Static generation
- API routes
- Built-in optimization
- React ecosystem

### Why Solana?
- High throughput
- Low transaction costs
- Fast finality
- Growing ecosystem

### Why PostgreSQL?
- ACID compliance
- JSON support
- Full-text search
- Proven reliability

## Deployment Architecture

### Production Setup
```
Internet → Load Balancer → [Frontend Servers]
                         → [Backend Servers] → Database
                         → [WebSocket Servers]
                         ↓
                    CDN (Static Assets)
```

### Container Orchestration
- Docker containers
- Kubernetes deployment
- Auto-scaling
- Health monitoring

## API Design Principles

- RESTful endpoints
- Consistent naming
- Versioning support
- Comprehensive documentation
- Error handling
- Rate limiting

## Database Schema

### Core Tables
- users
- agents
- events
- votes
- achievements
- transactions
- sessions

### Relationships
- One-to-many: User → Votes
- Many-to-many: Users ↔ Achievements
- One-to-one: User → Progress

## Conclusion

The architecture is designed for scalability, maintainability, and extensibility. Each component is modular and can be independently developed, tested, and deployed.
