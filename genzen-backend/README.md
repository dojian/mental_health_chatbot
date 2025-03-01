# GenZen Backend

This is the backend for the GenZen Chatbot.

### Misc Notes
run server: `poetry run uvicorn src.main:app --reload --port 8001` or `./start_backend.sh`

### Docker Notes
Build the image: `docker build -t genzen-backend:v01 .`
Run the image: `docker run -p 8001:8001 genzen-backend:v01`

### Minikube Notes
Install minikube: [Installation Instruction](https://minikube.sigs.k8s.io/docs/start/?arch=%2Fmacos%2Farm64%2Fstable%2Fbinary+download)
Start minikube: `minikube start --driver=docker --kubernetes-version=v1.32`
Integrate minikube with docker: `eval $(minikube docker-env)`

### Kustomize Notes
apply dev overlay: `kubectl apply -k .k8s/overlays/dev`
delete dev overlay: `kubectl delete -k .k8s/overlays/dev`
