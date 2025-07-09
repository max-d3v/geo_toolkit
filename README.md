# 🤖 GEO (Generative Engine Optimization) Tools

> **Discover how your brand appears in LLM responses and optimize your presence in AI-generated content.**

[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![OpenAI](https://img.shields.io/badge/Powered%20by-OpenAI-black.svg)](https://openai.com)

## 📖 Overview

GEO Tools is a comprehensive FastAPI-based platform that helps you understand and optimize how your company or brand is positioned in Large Language Model (LLM) responses. Built with OpenAI's web research capabilities and LangGraph for intelligent workflow orchestration.

## 🚀 Features

### 🔍 GEO Evaluator API

The GEO Evaluator provides REST and streaming endpoints for:

- **🔎 Brand Analysis**: Intelligent brand discovery and contextualization
- **🔑 Keyword Extraction**: AI-powered keyword identification from brand research
- **🌐 Web Research Integration**: Uses OpenAI's web search for real-time data
- **📊 Competitive Intelligence**: Generates dominance graphs showing competitor positioning
- **🎯 Location-aware Analysis**: City-specific search results and rankings

## 🛠️ Installation & Setup

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/max-d3v/geo_toolkit
cd geo_agents

# Create environment file
cp .env.example .env
# Add your OpenAI API key to .env:
# GEO_AVAL_API_KEY=your_openai_api_key_here

# Development environment
docker-compose -f docker-compose-dev.yml up --build

# Production environment  
docker-compose up --build
```

## 🔧 Configuration

### Environment Variables

```bash
# Required
GEO_AVAL_API_KEY=your_openai_api_key_here

# Optional (for frontend integration)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Supported Languages & Locations

- **Languages**: `en_US`, `pt_BR`
- **Locations**: Any city name for location-aware search

## 🔍 How It Works

1. **Brand Research**: Agent researches your brand using OpenAI's web search
2. **Keyword Extraction**: AI extracts relevant search keywords from research
3. **Competitive Analysis**: Searches for each keyword + location to find competitors
4. **Dominance Mapping**: Creates a graph showing which companies dominate each keyword
5. **Results Aggregation**: Combines data into actionable competitive intelligence

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📋 Requirements

- Python 3.12+
- OpenAI API Key with web search access
- Docker (for containerized deployment)

## 🌟 Support

If you find this project helpful, please give it a ⭐ on GitHub!

---

**Built with:** LangGraph + Next.js
