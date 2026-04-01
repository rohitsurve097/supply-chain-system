# Learning + Deployment Guide (Beginner Friendly)

This guide teaches the full journey end-to-end:
1. Local containers
2. GitHub + Actions
3. AWS basics
4. EKS + RDS + SQS
5. Production deploy

## Phase 0: Understand the flow

Your system flow is:
1. User creates order (`order_service`)
2. Order event sent to SQS (`ORDER_CREATED`)
3. Inventory consumes event and reserves stock
4. Inventory publishes `INVENTORY_RESERVED`
5. Shipment consumes and creates shipment

## Phase 1: Run locally (already done)

```bash
cp .env.example .env
docker compose up --build -d
```

Check:
```bash
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
```

## Phase 2: GitHub + Actions basics

### What CI/CD means
- CI (Continuous Integration): every push is validated automatically.
- CD (Continuous Deployment): if checks pass, deploy automatically.

### What your pipeline does
- Job 1 `test`: compile-check Python code.
- Job 2 `build-and-push`: build/push images to GHCR.
- Job 3 `deploy`: apply Kubernetes manifests (only when secrets are configured).

## Phase 3: AWS setup (first time)

## 3.1 Create AWS account
- Sign up at aws.amazon.com
- Choose a region and keep it consistent (recommended: `ap-south-1`)

## 3.2 Create IAM user for programmatic access
- Go to IAM -> Users -> Create user
- Enable programmatic access
- Attach policies (learning phase):
  - `AmazonEKSClusterPolicy`
  - `AmazonEKSWorkerNodePolicy`
  - `AmazonEC2ContainerRegistryFullAccess`
  - `AmazonRDSFullAccess`
  - `AmazonSQSFullAccess`
  - `IAMFullAccess` (learning only; tighten later)
- Save Access Key ID + Secret Access Key

## 3.3 Install local tools
- AWS CLI
- kubectl
- eksctl

Verify:
```bash
aws --version
kubectl version --client
eksctl version
```

Configure AWS CLI:
```bash
aws configure
```
Use your access key, secret, region (`ap-south-1`), output `json`.

## 3.4 Create SQS queues
```bash
aws sqs create-queue --queue-name order-events
aws sqs create-queue --queue-name inventory-events
```
Then fetch queue URLs from AWS console or via CLI list command.

## 3.5 Create RDS PostgreSQL
- Service: RDS -> Create database
- Engine: PostgreSQL
- Template: Free tier (if available)
- Public access: Yes (learning phase only)
- Security group: allow inbound 5432 from your IP
- Note endpoint, username, password, db name

Build DB URL format:
`postgresql+asyncpg://<user>:<password>@<rds-endpoint>:5432/<database>`

## 3.6 Create EKS cluster
Example with eksctl:
```bash
eksctl create cluster \
  --name supply-chain-cluster \
  --region ap-south-1 \
  --nodegroup-name supply-chain-ng \
  --node-type t3.medium \
  --nodes 2 \
  --nodes-min 2 \
  --nodes-max 3 \
  --managed
```

Update kubeconfig:
```bash
aws eks update-kubeconfig --name supply-chain-cluster --region ap-south-1
kubectl get nodes
```

## Phase 4: GitHub secrets (when AWS is ready)

Add repository secrets:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `ORDER_SERVICE_DB_URL`
- `INVENTORY_SERVICE_DB_URL`
- `SHIPMENT_SERVICE_DB_URL`
- `KUBE_CONFIG_DATA`

Generate `KUBE_CONFIG_DATA`:
```bash
base64 < ~/.kube/config | tr -d '\n'
```
Copy output and save as `KUBE_CONFIG_DATA`.

## Phase 5: Update Kubernetes manifests for real queues

Edit:
- `infra/kubernetes/base/configmap.yaml`

Set:
- real `ORDER_SQS_QUEUE_URL`
- real `INVENTORY_SQS_QUEUE_URL`
- real `INVENTORY_EVENT_QUEUE_URL`
- real `SHIPMENT_SQS_QUEUE_URL`

And ensure image names are your GHCR images.

## Phase 6: First production deployment

Push to `main`:
```bash
git add .
git commit -m "Enable production deployment"
git push origin main
```

Then GitHub Actions should:
1. test
2. build/push images
3. deploy to EKS

Verify:
```bash
kubectl -n supply-chain get pods
kubectl -n supply-chain get svc
kubectl -n supply-chain get hpa
```

## Phase 7: Test in cluster

Port-forward services for quick test:
```bash
kubectl -n supply-chain port-forward svc/order-service 8001:80
kubectl -n supply-chain port-forward svc/inventory-service 8002:80
kubectl -n supply-chain port-forward svc/shipment-service 8003:80
```

Then use the same curl flow from local testing.

## Safety notes
- IAM policies above are broad for learning speed; reduce permissions later.
- Public RDS access is only for learning; lock down for production.
- Move secrets to AWS Secrets Manager + External Secrets after first successful deploy.
