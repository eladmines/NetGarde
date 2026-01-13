# Development stage
FROM node:18-alpine AS development

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (use npm ci for consistency)
RUN npm ci

# Copy public folder (required for react-scripts)
COPY public ./public

# Do NOT copy src; it will be mounted as a volume for hot reload
EXPOSE 3000

# Start React dev server (with hot reload)
CMD ["npm", "start"]

# Production build stage
FROM node:18-alpine AS build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production=false

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine AS production

# Copy built files from build stage
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration (optional, for custom config)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Create non-root user (nginx already runs as non-root, but ensure proper permissions)
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:80 || exit 1

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
