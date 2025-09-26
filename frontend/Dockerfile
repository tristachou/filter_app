# Use the official Node.js 20 image.
FROM node:20-alpine

# Set the working directory in the container.
WORKDIR /app

# Copy package.json and package-lock.json (or yarn.lock, etc.) first.
# This leverages Docker layer caching to avoid re-installing dependencies on every code change.
COPY package*.json ./

# Install project dependencies.
RUN npm install

# Copy the rest of your app's source code into the container.
COPY . .

# Vite's default port is 5173. Make it accessible outside the container.
EXPOSE 5173

# The command to start the Vite development server.
# The --host flag is included in the vite.config.js, so it's not strictly needed here
# but we run it via npm run dev script which should have it.
CMD ["npm", "run", "dev"]
