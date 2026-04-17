# Stage 1: Build the React app
FROM node:18-slim AS builder

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the production app
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=$REACT_APP_API_URL
RUN npm run build

# Stage 2: Serve the production build using 'serve'
FROM node:18-slim

WORKDIR /app

# Install 'serve' globally
RUN npm install -g serve

# Copy only the build artifacts from the builder stage
COPY --from=builder /app/build ./build

# Expose port 3000
EXPOSE 3000

# Command to serve the app
CMD ["serve", "-s", "build", "-l", "3000"]
