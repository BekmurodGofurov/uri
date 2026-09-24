FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

CMD ["sh", "-c", "npm run dev -- --host 0.0.0.0 --port ${FRONTEND_PORT:-${VITE_PORT:-${PORT:?FRONTEND_PORT or VITE_PORT environment variable must be set}}}"]

