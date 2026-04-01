#!/usr/bin/env bash
set -euo pipefail

if [ ! -f "$HOME/.kube/config" ]; then
  echo "~/.kube/config not found. Run aws eks update-kubeconfig first."
  exit 1
fi

# Prints one-line base64 suitable for GitHub secret KUBE_CONFIG_DATA
base64 < "$HOME/.kube/config" | tr -d '\n'
echo
