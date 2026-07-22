# Fraud Network Graph Intelligence - Backend API Service

This is the backend service for Module 3: Fraud Network Graph Intelligence. It is built using Node.js, Express, TypeScript, and MongoDB.

## Features

- **Express & TypeScript**: Strongly-typed routing and controllers.
- **Mongoose / MongoDB**: Persistent storage of Fraud Reports.
- **CRUD Operations**: Complete CRUD REST APIs for fraud reports.
- **Indexed Search**: Optimizations on identifiers like `victimId`, `phoneNumber`, and `upiId`.

## Prerequisites

- [Node.js](https://nodejs.org/) (v18.0.0 or higher)
- [MongoDB](https://www.mongodb.com/) (running instance local or remote)

## Getting Started

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Configure Environment Variables**:
   Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```
   Specify your `MONGODB_URI` and `PORT`.

3. **Run in development mode (with hot-reload)**:
   ```bash
   npm run dev
   ```

4. **Build for production**:
   ```bash
   npm run build
   ```

5. **Start production server**:
   ```bash
   npm run start
   ```

## REST API Endpoints

### 1. Welcome / Health Check
- **Route**: `GET /`
- **Response**:
  ```json
  {
    "message": "Welcome to the Fraud Network Graph Intelligence API",
    "status": "healthy",
    "timestamp": "..."
  }
  ```

### 2. Create Fraud Report
- **Route**: `POST /api/report`
- **Body**:
  ```json
  {
    "victimId": "VIC-10928",
    "victimName": "John Doe",
    "phoneNumber": "+1234567890",
    "upiId": "john@upi",
    "bankAccount": "123456789012",
    "deviceFingerprint": "df-8f4e2c9a",
    "reportTimestamp": "2026-07-05T11:52:00Z"
  }
  ```
- **Response**: `201 Created`

### 3. List Fraud Reports
- **Route**: `GET /api/report`
- **Query Params**:
  - `victimId` (optional) - filter by victim ID
  - `phoneNumber` (optional) - filter by phone number
- **Response**: `200 OK`

### 4. Get Single Fraud Report
- **Route**: `GET /api/report/:id`
- **Params**:
  - `:id` can be either the MongoDB ObjectID or the `victimId` value.
- **Response**: `200 OK` (or `404 Not Found`)

### 5. Delete Fraud Report
- **Route**: `DELETE /api/report/:id`
- **Params**:
  - `:id` can be either the MongoDB ObjectID or the `victimId` value.
- **Response**: `200 OK` (or `404 Not Found`)
