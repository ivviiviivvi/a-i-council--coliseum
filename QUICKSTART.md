# Quick Start Guide

Get AI Council Coliseum running in 5 minutes!

## 🚀 Fastest Way: Docker Compose

```bash
# 1. Clone the repository
git clone https://github.com/ivviiviivvi/a-i-council--coliseum.git
cd a-i-council--coliseum

# 2. Setup environment
cp .env.example .env
# Edit .env with your API keys (optional for basic testing)

# 3. Start everything
docker-compose up -d

# 4. Wait ~30 seconds for services to initialize

# 5. Open your browser
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

Done! 🎉

## 📱 What You Can Do Now

### View API Documentation
- Navigate to http://localhost:8000/docs
- Explore all available endpoints
- Test API calls directly from the browser

### Explore the Frontend
- Open http://localhost:3000
- See the landing page with feature cards
- Navigate through different sections

### Check Service Status
```bash
docker-compose ps
docker-compose logs -f backend
```

## 🛠️ Development Mode

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend at http://localhost:8000

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

Frontend at http://localhost:3000

## 🧪 Testing the System

### Test Backend API
```bash
# Health check
curl http://localhost:8000/health

# List agents
curl http://localhost:8000/api/agents

# List events
curl http://localhost:8000/api/events
```

### Test Frontend
- Open http://localhost:3000
- Click on feature cards
- Try interactive elements

## 📚 Next Steps

1. **Read the Documentation**
   - [README.md](../README.md) - Full overview
   - [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System design
   - [DEPLOYMENT.md](docs/DEPLOYMENT.md) - Deployment guide

2. **Configure API Keys** (Optional but recommended)
   - OpenAI API key for AI agents
   - Blockchain RPC endpoints
   - TTS service keys

3. **Customize Your Setup**
   - Modify `.env` for your needs
   - Update `docker-compose.yml` if needed
   - Configure frontend in `frontend/next.config.js`

4. **Start Developing**
   - Check [CONTRIBUTING.md](../CONTRIBUTING.md)
   - Create a feature branch
   - Make your changes
   - Submit a PR

## 🐛 Troubleshooting

### Services Won't Start?
```bash
# Check logs
docker-compose logs

# Restart services
docker-compose down
docker-compose up -d
```

### Port Already in Use?
Edit `docker-compose.yml` and change port mappings:
```yaml
ports:
  - "8001:8000"  # Change 8000 to 8001
```

### Database Issues?
```bash
# Reset database
docker-compose down -v
docker-compose up -d
```

## 💡 Tips

- **API Documentation**: Always available at `/docs`
- **Hot Reload**: Both backend and frontend auto-reload on changes
- **Logs**: Use `docker-compose logs -f [service]` to view logs
- **Shell Access**: Use `docker-compose exec [service] bash`

## 🎯 Key Features to Explore

1. **AI Agent System** - Check `/api/agents`
2. **Event Pipeline** - Check `/api/events`
3. **Voting System** - Check `/api/voting`
4. **Achievements** - Check `/api/achievements`
5. **Blockchain** - Check `/api/blockchain`

## 📞 Need Help?

- **Issues**: [GitHub Issues](https://github.com/ivviiviivvi/a-i-council--coliseum/issues)
- **Docs**: See `/docs` directory
- **Discussions**: [GitHub Discussions](https://github.com/ivviiviivvi/a-i-council--coliseum/discussions)

## 🎉 You're Ready!

You now have a fully functional AI Council Coliseum instance running locally. Start exploring, developing, and building amazing features!

Happy coding! 🚀
