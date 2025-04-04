

## How to build docker image for docker testing
```bash
docker build \
--build-arg NEXT_PUBLIC_API_URL=http://localhost:8001 \
-t genzen-frontend:v04 . 
```

## How to build docker image for kubernetes testing
```bash

# frontend
docker build \
--build-arg NEXT_PUBLIC_API_URL=http://backend-service:8001 \
--build-arg NEXT_PUBLIC_APP_ENV=staging \
-t genzen-frontend:url . 

# backend
docker build -t genzen-backen:url .
```
```bash
docker build \
--build-arg NEXT_PUBLIC_API_URL=http://localhost:8001 \
-t genzen-frontend:v06 . 
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
