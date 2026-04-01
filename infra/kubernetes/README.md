# Kubernetes Deployment (EKS-ready)

## Prerequisites
- EKS cluster access configured in `kubectl`
- Metrics server installed (for HPA)
- Container images pushed to a registry (example: GHCR or ECR)

## 1) Configure Secrets
1. Copy secret template:
   ```bash
   cp infra/kubernetes/base/secret.template.yaml infra/kubernetes/base/secret.yaml
   ```
2. Fill real DB credentials and AWS credentials in `secret.yaml`.

For production, prefer External Secrets + AWS Secrets Manager instead of plaintext Kubernetes secrets.

## 2) Set Image Names
Update image fields in:
- `infra/kubernetes/services/order/deployment.yaml`
- `infra/kubernetes/services/inventory/deployment.yaml`
- `infra/kubernetes/services/shipment/deployment.yaml`

## 3) Deploy
```bash
kubectl apply -f infra/kubernetes/base/secret.yaml
kubectl apply -k infra/kubernetes
```

## 4) Verify
```bash
kubectl -n supply-chain get pods
kubectl -n supply-chain get svc
kubectl -n supply-chain get hpa
```
