# GenZen Backend

This is the backend for the GenZen Chatbot.

### Requirements
For Local Testing and Development:
- Must have Redis and Postgres Docker Containers running
  - Redis:7.4.2-alpine
```bash
docker run -d -p 6379:6379 redis:7.4.2-alpine
```
  - Postgres:14--alpine
```bash
docker run -e POSTGRES_USER=postgres_user -e POSTGRES_PASSWORD=supersecretpassword -e POSTGRES_DB=postgres_db_name -p 5432:5432 -d postgres:14-alpine
```
- Ensure in the root directory of `genzen-backend`
```bash
poetry install # active env and install all dependencies
```
- Run Server
```bash
poetry run uvicorn src.main:app --reload --port 8001
```

For Local Kubernetes Deployment:
- Minikube (running on top of Docker)
- Kubectl

### Agents Notes
make sure you add your api key in .env file either directly or by:
echo "OPENAI_API_KEY=\"$OPENAI_API_KEY\"" > genzen-backend/src/agents/.env

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

### Testing
#### Test Registration /auth/register with Postman
post with body raw as json
```json
{
  "username": "testuser",
  "password": "strongpassword",
  "email": "example@example.com",
}
```

Returns a response as a json
```json
{
  "access_token": <JWT_token>,
  "token_type": "bearer"
}
```

#### Test Login /auth/login with Postman
post with body form-data
```json
{
  "username": "testuser",
  "password": "strongpassword"
}
```

Returns a response as a json
```json
{
  "access_token": <JWT_token>,
  "token_type": "bearer"
}`

#### Test Logout /auth/logout with Postman
post with headers
```
key: Authorization
value: Bearer <JWT_token>
```

Returns a response as a json
```json
{
  "message": "Successfully logged out"
}
```

#### Test /v1/chat with Postman
post with headers AND body raw as json
```
key: Authorization
value: Bearer <JWT_token>
```
```json
{
  "query": "What is the capital of France?"
}
```

Returns a response from OpenAI.
```json
{
  "session_id": <session_id>,
  "query": "What is the capital of France?",
  "response": "The capital of France is Paris."
}
```

#### Test /v1/chat/sessions with Postman
get with headers
```
key: Authorization
value: Bearer <JWT_token>
```

Returns a list of all chat sessions for the current user.
```json
[
  {
    "session_id": <session_id>,
    "created_at": "2023-03-14T18:30:00.000000",
    "first_query": "What is the capital of France?"
  },
  {
    "session_id": <session_id>,
    "created_at": "2023-03-14T18:30:00.000000",
    "first_query": "What is the capital of France?"
  }
]