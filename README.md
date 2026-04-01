# Supply Chain Microservices Platform

Production-grade async microservices platform for Order, Inventory, and Shipment domains.

## Tech Stack
- Python (Async)
- FastAPI
- Pydantic
- SQLAlchemy (Async)
- PostgreSQL
- Docker / Docker Compose
- Kubernetes (EKS-ready)
- AWS-ready integrations (SQS, S3, CloudWatch, Secrets Manager)

## Repository Structure
```
supply-chain-system/
├── services/
│   ├── order_service/
│   ├── inventory_service/
│   └── shipment_service/
├── common/
│   ├── database/
│   ├── models/
│   ├── schemas/
│   └── utils/
├── infra/
│   ├── docker/
│   ├── kubernetes/
│   └── terraform/
├── scripts/
├── docker-compose.yml
├── .env.example
└── README.md
```

## Current Status
- [x] Step 1A: Project scaffold and baseline config
- [x] Step 1B: Order Service implementation (FastAPI + Async SQLAlchemy + Docker)
- [x] Step 2: Inventory Service + event consumer
- [x] Step 3: Shipment Service + tracking workflow
- [x] Step 4: Kubernetes manifests and CI/CD baseline

## Order Service (Implemented)
### Endpoints
- `POST /orders`
- `GET /orders/{id}`
- `GET /health`

### Eventing
- Publishes `ORDER_CREATED` events to SQS.
- Local development uses LocalStack SQS.

## Inventory Service (Implemented)
### Endpoints
- `GET /inventory/{product_id}`
- `POST /inventory/update`
- `GET /health`

### Eventing
- Consumes `ORDER_CREATED` events from `order-events` queue.
- Uses atomic DB update (`stock >= quantity`) to reserve stock safely under concurrency.
- Publishes `INVENTORY_RESERVED` events to `inventory-events` queue.

## Shipment Service (Implemented)
### Endpoints
- `GET /shipments/{shipment_id}`
- `GET /shipments/order/{order_id}`
- `POST /shipments/{shipment_id}/status`
- `GET /health`

### Eventing
- Consumes `INVENTORY_RESERVED` events from `inventory-events`.
- Creates shipment records idempotently (unique `order_id`).
- Initializes each shipment with `PROCESSING` status and generated tracking ID.

## Local Run
1. Create env file:
   ```bash
   cp .env.example .env
   ```
2. Start infrastructure and services:
   ```bash
   docker compose up --build
   ```
3. Test health endpoints:
   ```bash
   curl http://localhost:8001/health
   curl http://localhost:8002/health
   curl http://localhost:8003/health
   ```
4. Seed inventory first:
   ```bash
   curl -X POST http://localhost:8002/inventory/update \
     -H "Content-Type: application/json" \
     -d '{"product_id":"P-1001","stock":10}'
   ```
5. Create order:
   ```bash
   curl -X POST http://localhost:8001/orders \
     -H "Content-Type: application/json" \
     -d '{"product_id":"P-1001","quantity":2,"user_id":"U-42"}'
   ```
6. Fetch shipment by order ID (after event processing):
   ```bash
   curl http://localhost:8003/shipments/order/<ORDER_ID>
   ```
7. Update shipment status:
   ```bash
   curl -X POST http://localhost:8003/shipments/<SHIPMENT_ID>/status \
     -H "Content-Type: application/json" \
     -d '{"status":"IN_TRANSIT"}'
   ```

## Notes
- Database table auto-creation is enabled at startup for local development.
- Production setup should use Alembic migrations.

## Kubernetes (EKS-ready)
- Base manifests are in `infra/kubernetes/` with:
  - Namespace
  - Shared ConfigMap
  - Secret template
  - Deployments, Services, HPAs for all services
- Kustomize entry point: `infra/kubernetes/kustomization.yaml`

Quick deploy:
```bash
cp infra/kubernetes/base/secret.template.yaml infra/kubernetes/base/secret.yaml
# Fill real secret values
kubectl apply -f infra/kubernetes/base/secret.yaml
kubectl apply -k infra/kubernetes
```

## CI/CD (GitHub Actions)
Workflow file:
- `.github/workflows/ci-cd.yml`
- Deploy job automatically runs only after all required GitHub secrets are configured.

Pipeline stages:
1. Compile-check Python services.
2. Build and push Docker images to GHCR.
3. Deploy to Kubernetes on `main` branch.

Required GitHub Secrets:
- `KUBE_CONFIG_DATA` (base64 kubeconfig)
- `ORDER_SERVICE_DB_URL`
- `INVENTORY_SERVICE_DB_URL`
- `SHIPMENT_SERVICE_DB_URL`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

## Learning Path
- Beginner step-by-step guide:
  - `docs/LEARNING_AND_DEPLOYMENT_GUIDE.md`
- Full master handbook (architecture, diagrams, incidents, AWS + CI/CD + teardown):
  - `docs/MASTER_END_TO_END_GUIDE.md`
- Helper to generate `KUBE_CONFIG_DATA`:
  - `scripts/print_kube_config_secret.sh`
