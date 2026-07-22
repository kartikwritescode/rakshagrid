import express, { Application, Request, Response } from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import reportRoutes from './routes/reportRoutes';
import analysisRoutes from './routes/analysisRoutes';
import fraudShieldRoutes from './routes/fraudShieldRoutes';

// Load environment variables
dotenv.config();

const app: Application = express();

// Middlewares
app.use(cors());
app.use(express.json());

// Routes
app.use('/api/report', reportRoutes);
app.use('/api/graph-analysis', analysisRoutes);
app.use('/api/fraud-shield', fraudShieldRoutes);

// Health Check / Welcome route
app.get('/', (_req: Request, res: Response) => {
  res.status(200).json({
    message: 'Welcome to the Fraud Network Graph Intelligence API',
    status: 'healthy',
    timestamp: new Date()
  });
});

// 404 Handler
app.use((req: Request, res: Response) => {
  res.status(404).json({ success: false, message: `Route not found: ${req.method} ${req.originalUrl}` });
});

export default app;
