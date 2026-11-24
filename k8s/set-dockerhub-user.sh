#!/usr/bin/env bash
# Usage: bash k8s/set-dockerhub-user.sh <your-dockerhub-username>
# Replaces the DOCKERHUB_USER placeholder in all manifests with your username.
set -e
[ -z "$1" ] && { echo "usage: $0 <dockerhub-username>"; exit 1; }
grep -rl DOCKERHUB_USER "$(dirname "$0")" --include=*.yaml | xargs sed -i "s|DOCKERHUB_USER|$1|g"
echo "Manifests now use image $1/aceest-fitness"
