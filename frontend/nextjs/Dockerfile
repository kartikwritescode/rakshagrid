# frontend/nextjs/Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY frontend/nextjs/package*.json ./
RUN npm ci

COPY frontend/nextjs/ ./

EXPOSE 3000

CMD ["npm", "run", "dev"]
