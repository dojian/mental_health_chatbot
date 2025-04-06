# Frontend Nextjs


## How to build docker image for kubernetes testing

### Notes
1. Make sure database tables are up before running system

```bash

# frontend - WORKING BUILD
docker build \
--build-arg NEXT_PUBLIC_API_URL=http://backend-service:8001 \
--build-arg NEXT_PUBLIC_APP_ENV=staging \
-t genzen-frontend:v1.3 . 

# backend - WORKING BUILD
docker build -t genzen-backend:v1.2 .
```

```bash
k apply -k .k8s/overlays/dev/
k delete -k .k8s/overlays/dev/
```


Run docker
```bash
docker run --rm -p 3000:3000 genzen-frontend:url
```

## How to run things for locat tests
```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```
