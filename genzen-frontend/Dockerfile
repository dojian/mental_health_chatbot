FROM node:18-alpine AS base
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1

# Define build arguments
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_APP_ENV=staging

FROM base AS dependencies
COPY package.json package-lock.json* ./
RUN npm ci && npm cache clean --force

FROM dependencies AS builder
COPY . .
ENV NODE_ENV=production
# Pass build arguments to environment variables during build
ENV NEXT_PUBLIC_APP_ENV=${NEXT_PUBLIC_APP_ENV}
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

# Create cache directories with proper permissions
RUN mkdir -p .next/cache && \
    chown -R node:node .next

# Build the application
RUN npm run build && npm cache clean --force

FROM node:18-alpine AS runner
WORKDIR /app

# Install curl for healthcheck
RUN apk add --no-cache curl && \
    rm -rf /var/cache/apk/*

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Set production environment
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"
ENV NEXT_SHARP_PATH=/app/node_modules/sharp

# Create the env file with build arguments
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_APP_ENV
RUN echo "NEXT_PUBLIC_APP_ENV=${NEXT_PUBLIC_APP_ENV}" > .env.production && \
    echo "NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}" >> .env.production && \
    echo "NEXT_PUBLIC_JWT_STORAGE_KEY=token" >> .env.production

# Copy built assets
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.mjs ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Create cache directory with proper permissions
RUN mkdir -p .next/cache && chown nextjs:nodejs .next/cache

# Set proper permissions
RUN chown -R nextjs:nodejs /app

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Start the application
CMD ["node", "server.js"]
