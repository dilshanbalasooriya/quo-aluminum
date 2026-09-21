FROM node:20-slim

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Expose Vite dev server port
EXPOSE 5000

# Start Vite with --host flag so it accepts external requests from the host machine
CMD ["npm", "run", "dev", "--", "--host"]