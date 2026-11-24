# Kubernetes deployment strategies

Images used (push these to Docker Hub first): `aceest-fitness:1.0.0` (version 1),
`aceest-fitness:2.0.0` (version 2). `/version` shows which one answered.

| Folder | Strategy | Access |
|---|---|---|
| rolling-update | Rolling update + rollback | NodePort 30080 |
| blue-green | Blue-green | NodePort 30081 |
| canary | Canary (4 stable : 1 canary) | NodePort 30082 |
| ab-testing | A/B by `X-Version` header | Ingress host aceest.local |
| shadow | Traffic mirroring | Ingress host shadow.local |

Before use: `bash k8s/set-dockerhub-user.sh <your-dockerhub-username>`
