# Fleet Tracker Frontend Dockerfile
# Development version

FROM node:18-alpine

LABEL maintainer="Trương Quốc Huân <truonghuan0709@gmail.com>"
LABEL description="Fleet Tracker Frontend React Application"

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S reactjs -u 1001
RUN chown -R reactjs:nodejs /app
USER reactjs

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Expose port
EXPOSE 3000

# Development command
CMD ["npm", "start"]
