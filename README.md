# BitGuard

BitGuard is a Bitcoin wallet risk-scoring and blockchain transaction analysis platform. It combines a Neo4j graph database for multi-hop transaction subgraphs, a machine learning risk-scoring pipeline with SHAP explainability, and a web interface. 

---
``` Link - https://drive.google.com/drive/folders/1Y6YbqEmjgR4qih_m0gABNMqxYRiVAvyh?usp=sharing
---

## Architecture & Project Structure

```text
bit-guard/
├── admin/                        # Infrastructure, ETL, and deployment configurations
│   ├── infra/                    # Terraform AWS EC2 provisioning (ec2_setup.tf)
│   ├── initial-setup-download-bitcoin-core/ # Bitcoin Core RPC to Parquet ETL pipeline
│   ├── makefile/                 # Backend and frontend Makefiles
│   ├── neo4j/                    # Neo4j Docker setups (Linux/Windows), Cypher queries & batch scripts
│   ├── production-deploy/        # Production Docker Compose & Nginx configurations
│   └── scripts/                  # Server initialization scripts (setup.sh)
├── backend/
│   ├── api/                      # Main REST API, ML inference pipeline, SHAP explainer & payments
│   └── database/                 # Neo4j database service and base Cypher queries
├── frontend/                     # Web UI (HTML/CSS/JS templates, routers, form submission)
├── mock_backend/                 # Lightweight mock API server for local frontend testing
├── notebooks/                    # Model training and experimentation (bitguard_modeling.ipynb)
├── Dockerfile                    # Root container build definition
├── render.yaml                   # Render Blueprint deployment configuration
├── deploy_start.sh               # Production startup script
├── run.sh / run.bat              # Local startup scripts (Unix / Windows)
└── DEPLOY.md                     # Deployment documentation
```

---

## Key Features

* **Graph-Based Blockchain Analysis:** Uses Neo4j and custom Cypher queries (`create_3hop_subgraph.cypher`, `base_query.cypher`) to trace and extract multi-hop transaction subgraphs.
* **ML Risk Scoring & Explainability:** Calculates wallet risk probabilities (`risk_prob.py`) via a trained pipeline (`pipeline.py`, `loader.py`) and generates feature-level explanations using SHAP (`shap_explainer.py`).
* **Bitcoin Core Data Ingestion:** Extracts raw blockchain transactions via RPC into partitioned Parquet files (`rpc_to_partitioned_parquet.py`) for high-throughput batch loading into Neo4j (`run_batch.py`).
* **Web UI & Payment Integration:** Complete user-facing application featuring address validation, detailed risk reporting, interactive pages, and payment handling.
* **Flexible Infrastructure:** Supports local execution scripts, Docker Compose modular deployment, AWS EC2 provisioning via Terraform (`ec2_setup.tf`), and Render Blueprint automation (`render.yaml`).

---

## Prerequisites

* **Python 3.9+**
* **Docker & Docker Compose**
* **Neo4j Database** (Local or containerized via `admin/neo4j/`)
* **Terraform** *(Optional, for AWS EC2 deployment)*

---

## Getting Started (Local Development)

### 1. Clone the Repository
```bash
git clone https://github.com/mayankrises/bit-guard.git
cd bit-guard
```

### 2. Set Up Environment Variables
Copy the `.env.example` templates into `.env` files within their respective service directories:
```bash
cp backend/api/.env.example backend/api/.env
cp backend/database/.env.example backend/database/.env
cp frontend/.env.example frontend/.env
```
*(Ensure model artifacts are placed in `backend/api/pickle/` prior to running the API service).*

### 3. Quick Run (Startup Scripts)
* **macOS / Linux:**
  ```bash
  chmod +x run.sh
  ./run.sh
  ```
* **Windows:**
  ```cmd
  run.bat
  ```

### 4. Running Microservices via Docker Compose
Each stack layer can be started independently:

* **Neo4j Database:**
  ```bash
  cd admin/neo4j/linux   # or admin/neo4j/windows
  docker-compose up -d
  ```
* **Database Service:**
  ```bash
  cd backend/database
  docker-compose up --build -d
  ```
* **Backend API:**
  ```bash
  cd backend/api
  docker-compose up --build -d
  ```
* **Frontend Web App:**
  ```bash
  cd frontend
  docker-compose up --build -d
  ```

*(To test the frontend without running Neo4j or the full ML pipeline, launch `python mock_backend/mock_api.py` to emulate backend endpoints).*

---

## Data Pipeline & Modeling Workflow

1. **Ingest Blockchain Data:** Update `admin/initial-setup-download-bitcoin-core/.env` and execute `rpc_to_partitioned_parquet.py` against your Bitcoin Core node.
2. **Build Graph Database:** Apply database indices (`admin/neo4j/queries/CREATE_ADDRESS_INDICES.cypher`) and run `admin/neo4j/script/run_batch.py` to populate nodes and edges.
3. **Train & Inspect Model:** Open `notebooks/bitguard_modeling.ipynb` to explore feature processing, training logic, and model export procedures.

---

## Deployment Options

* **Render Blueprints:** Connect your repository and deploy automatically using the root `render.yaml`.
* **Production Docker Stack:** Production compose settings, Nginx reverse proxy, and SSL mounts reside in `admin/production-deploy/`.
* **AWS Cloud Infrastructure:** Provision EC2 instances using `admin/infra/ec2_setup.tf` and initialize using `admin/scripts/setup.sh`.
* Refer to `DEPLOY.md` for extended deployment guidelines.

---

## License

This project is licensed under the terms of the [LICENSE](LICENSE) file.
