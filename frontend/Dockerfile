# Fleet Tracker Frontend Dockerfile
# Development version - Optimized

FROM node:18-alpine

LABEL maintainer="Trương Quốc Huân <truonghuan0709@gmail.com>"
LABEL description="Fleet Tracker Frontend React Application"

# Set working directory
WORKDIR /app

# Install curl for health check
RUN apk add --no-cache curl

# Copy package files first for better caching
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S reactjs -u 1001 && \
    chown -R reactjs:nodejs /app
USER reactjs

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Expose port
EXPOSE 3000

# Development command
CMD ["npm", "start"]
