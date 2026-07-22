import { Router, Request, Response } from 'express';
import { generateFraudShieldResponse, calculateRiskScore } from '../services/geminiService';

const router = Router();

router.post('/chat', async (req: Request, res: Response) => {
  try {
    const { message, history } = req.body;
    
    if (!message) {
      return res.status(400).json({ success: false, message: 'Message is required' });
    }

    const aiResponse = await generateFraudShieldResponse(message, history || []);
    
    return res.status(200).json({
      success: true,
      response: aiResponse
    });
  } catch (error) {
    console.error('Chat API Error:', error);
    return res.status(500).json({ success: false, message: 'Internal Server Error' });
  }
});

router.post('/risk-score', async (req: Request, res: Response) => {
  try {
    const { transcript } = req.body;

    if (!transcript) {
      return res.status(400).json({ success: false, message: 'Transcript is required' });
    }

    const riskAnalysis = await calculateRiskScore(transcript);

    return res.status(200).json({
      success: true,
      data: riskAnalysis
    });
  } catch (error) {
    console.error('Risk Score API Error:', error);
    return res.status(500).json({ success: false, message: 'Internal Server Error' });
  }
});

export default router;
