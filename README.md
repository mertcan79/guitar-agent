# 🎸 Find Me a Guitar

An AI-powered guitar recommendation system that helps guitarists find their perfect instrument using natural language queries and advanced technical specifications.

## ✨ Features

- **Natural Language Search**: Describe your ideal guitar in plain English
- **Technical Specification Support**: Supports detailed specs like pickup types, bridge systems, wood types
- **Artist & Genre Knowledge**: Understands guitar preferences of famous artists and musical genres
- **Smart Budget Analysis**: Visual budget comparison with recommendations
- **Professional Interface**: Clean, modern Streamlit web interface

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/guitar-agent.git
   cd guitar-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   OPENAI_KEY=your_openai_api_key_here
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser** to `http://localhost:8501`

## 🎯 Example Queries

- **Artist-based**: "I want David Gilmour's tone from Pink Floyd. Need Stratocaster with alder body, maple neck, rosewood fretboard, vintage tremolo, single coils, 9.5\" radius. Budget $1500"

- **Genre-specific**: "Need a metal guitar with basswood body, bolt-on maple neck, ebony fretboard, Floyd Rose Original tremolo, active EMG 81/85 pickups, 24 frets, compound radius 12-16\", locking tuners. Budget $1800"

- **Technical**: "Want custom shop quality: ash body, quartersawn maple neck, pau ferro fretboard, hipshot locking tuners, Graph Tech nut, Gotoh 510 tremolo, Seymour Duncan SSL-5 pickups. Budget $2500"

## 🛠️ Technical Features

### Supported Specifications

- **Pickup Types**: Single coil, humbucker, P90, active EMG, coil-tap/split
- **Bridge Types**: Tune-o-matic, Floyd Rose, vintage tremolo, hardtail, wraparound
- **Body Woods**: Alder, ash, mahogany, basswood, maple, chambered
- **Neck Construction**: Bolt-on, set neck, neck-through, quartersawn
- **Fretboard Materials**: Rosewood, maple, ebony, pau ferro
- **Electronics**: Passive, active, coil-tap, push-pull pots, piezo

### Artist Knowledge Base

- David Gilmour (Pink Floyd) → Fender Stratocaster
- Jimmy Page (Led Zeppelin) → Gibson Les Paul
- Eric Clapton → Fender Stratocaster, Gibson Les Paul
- And many more...

## 🏗️ Architecture

```
src/
├── agents/                 # AI agents for guitar recommendations
│   ├── enhanced_guitar_agent.py
│   └── guitar_agent.py
├── knowledge/             # Guitar domain knowledge
│   └── guitar_knowledge.py
├── models/               # Data models
│   └── guitar.py
├── scrapers/            # Data sources
│   ├── mock_scraper.py
│   └── reverb_scraper.py
└── config.py           # Configuration management
```

## 🤖 How It Works

1. **Intent Analysis**: AI analyzes your natural language query to extract technical requirements
2. **Knowledge Integration**: Applies expert knowledge about artists, genres, and technical specifications  
3. **Smart Search**: Finds guitars matching your criteria from curated database
4. **Intelligent Matching**: Ranks results based on how well they match your specific needs
5. **Visual Results**: Presents the best match with detailed analysis and budget comparison

## 🔧 Configuration

Create a `.env` file with:

```env
OPENAI_KEY=your_openai_api_key_here
```

## 🚀 Deployment

The app can be deployed on:
- **Streamlit Cloud**: Connect your GitHub repo for automatic deployment
- **Heroku**: Use the included `requirements.txt`
- **Docker**: Containerized deployment ready

## 🧪 Development

Run tests:
```bash
python -m pytest tests/
```

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🎸 About

Built with love for guitarists who want to find their perfect instrument using the power of AI and comprehensive guitar knowledge.