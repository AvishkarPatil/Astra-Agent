# 🌍 Astra Agent

An intelligent assistant that converts natural language queries into executable GIS workflows using AI and open-source geospatial tools.

![image](https://github.com/user-attachments/assets/a627f1de-8bd8-4641-818f-e6783bb5beb9)


## 🚀 Features

- **Natural Language Processing**: Convert plain English queries to GIS operations
- **Multi-Model AI Integration**: Mistral-7B, LLaMA-3-8B via LangChain
- **Comprehensive GIS Tools**: QGIS, GRASS GIS, GDAL/OGR, GeoPandas
- **Real Data Sources**: Bhoonidhi, OpenStreetMap, STAC APIs
- **Interactive Interface**: Streamlit + OpenLayers/Leaflet mapping
- **Scalable Backend**: FastAPI + PostgreSQL/PostGIS

## 🏗️ Architecture

```
User Query → Streamlit UI → FastAPI → AI Models → GIS Tools → Spatial Data → Results
```

## 🛠️ Tech Stack

- **AI**: Mistral-7B-Instruct, LLaMA-3-8B, LangChain, Transformers
- **GIS**: QGIS, GRASS GIS, GDAL/OGR, GeoPandas, PostGIS
- **Backend**: Python FastAPI, PostgreSQL
- **Frontend**: Streamlit, OpenLayers, Leaflet
- **Data**: Bhoonidhi, OpenStreetMap, STAC APIs

## 📦 Installation

### Prerequisites
- Python 3.9+
- PostgreSQL with PostGIS
- QGIS with PyQGIS
- Docker (optional)

### Quick Setup

```bash
# Clone repository
git clone https://github.com/proavipatil/geospatial-ai-assistant.git
cd geospatial-ai-assistant

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your configurations

# Setup database
python scripts/setup_database.py

# Run the application
python scripts/run_app.py
```

### Docker Setup

```bash
# Build and run with Docker
docker-compose up --build
```

## 🚀 Usage

### Example Queries

```python
# Natural language queries the system can handle:
"Find all schools within 1km of hospitals in Mumbai"
"Calculate population density by district using census data"
"Identify flood-prone areas using elevation and rainfall data"
"Generate land use classification from satellite imagery"
```

### API Usage

```python
import requests

# Submit query
response = requests.post("http://localhost:8000/api/query", 
                        json={"query": "Find schools near hospitals in Mumbai"})

# Get results
result = response.json()
print(result['workflow'])  # AI-generated workflow
print(result['results'])   # GIS analysis results
```

### Web Interface

1. Start the application: `python scripts/run_app.py`
2. Open browser: `http://localhost:8501`
3. Enter natural language query
4. Review AI-generated workflow
5. Execute analysis and view results

## 📁 Project Structure

```
geospatial-ai-assistant/
├── src/
│   ├── ai/                 # AI processing modules
│   │   ├── query_processor.py
│   │   ├── workflow_generator.py
│   │   └── model_manager.py
│   ├── gis/                # GIS processing engines
│   │   ├── qgis_engine.py
│   │   ├── gdal_processor.py
│   │   └── spatial_operations.py
│   ├── data/               # Data access and management
│   │   ├── osm_client.py
│   │   ├── stac_client.py
│   │   └── bhoonidhi_client.py
│   ├── api/                # FastAPI backend
│   │   ├── main.py
│   │   ├── routes/
│   │   └── models/
│   └── frontend/           # Streamlit application
│       ├── app.py
│       ├── components/
│       └── utils/
├── config/                 # Configuration files
├── data/samples/           # Sample datasets
├── tests/                  # Test suites
├── docker/                 # Docker configuration
├── docs/                   # Documentation
└── scripts/                # Utility scripts
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run specific test suite
pytest tests/unit/
pytest tests/integration/

# Run with coverage
pytest --cov=src tests/
```

## 📖 Documentation

- [API Documentation](docs/api.md)
- [User Guide](docs/user_guide.md)
- [Developer Guide](docs/developer_guide.md)
- [Architecture Overview](docs/architecture.md)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- OpenStreetMap contributors
- QGIS development team
- Hugging Face for AI models
- Indian Space Research Organisation (ISRO) for Bhoonidhi

---
