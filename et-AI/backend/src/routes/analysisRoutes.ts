import { Router } from 'express';
import { getGraphAnalysis } from '../controllers/analysisController';

const router = Router();

// GET /api/graph-analysis
router.get('/', getGraphAnalysis);

export default router;
