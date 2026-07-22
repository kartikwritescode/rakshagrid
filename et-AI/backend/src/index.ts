import app from './app';
import { connectDB } from './config/db';

const PORT = process.env.PORT || 5000;

const startServer = async () => {
  // Connect to Database
  await connectDB();

  // Listen to requests
  app.listen(PORT, () => {
    console.log(`[server]: Server is running in ${process.env.NODE_ENV || 'development'} mode on port ${PORT}`);
  });
};

startServer().catch((error) => {
  console.error(`Failed to start server: ${(error as Error).message}`);
});
