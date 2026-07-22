import { Router } from 'express';
import {
  createReport,
  getReports,
  getReportById,
  deleteReport
} from '../controllers/reportController';

const router = Router();

// /api/report routes
router.route('/')
  .post(createReport)
  .get(getReports);

router.route('/:id')
  .get(getReportById)
  .delete(deleteReport);

export default router;
