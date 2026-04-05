FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build
RUN npm run build

# Use a simple HTTP server to serve the build
RUN npm install -g serve

# Expose port
EXPOSE 5173

# Start server
CMD ["serve", "-s", "dist", "-l", "5173"]
