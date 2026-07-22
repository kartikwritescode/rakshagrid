# et-AI - Module 3: Fraud Network Graph Intelligence

This repository hosts **Module 3: Fraud Network Graph Intelligence**, part of the et-AI platform. It is structured to separate the backend core intelligence service and the client visualization dashboard.

## Project Structure

```
/
├── backend/       # Express.js, TypeScript, and MongoDB backend logic (Active CRUD APIs)
└── frontend/      # Next.js and TypeScript frontend dashboard placeholder
```

## Quick Start

### 1. Database
Ensure you have a MongoDB instance running locally (e.g., `mongodb://127.0.0.1:27017/fraud_network_db`) or provide a connection string.

### 2. Run Backend API
Navigate to the `backend` folder, install dependencies, and start the development server:
```bash
cd backend
npm install
npm run dev
```
The server will run on [http://localhost:5000](http://localhost:5000).

### 3. Run Frontend Dashboard
Navigate to the `frontend` folder, install dependencies, and start the Next.js server:
```bash
cd frontend
npm install
npm run dev
```
The frontend dashboard will run on [http://localhost:3000](http://localhost:3000).
