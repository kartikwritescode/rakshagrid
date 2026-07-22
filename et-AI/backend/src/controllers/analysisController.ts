import { Request, Response } from 'express';
import { exec } from 'child_process';
import path from 'path';
import fs from 'fs';
import { Report } from '../models/Report';

/**
 * @desc    Execute Python graph analysis engine and retrieve results
 * @route   GET /api/graph-analysis
 * @access  Public
 */
export const getGraphAnalysis = async (_req: Request, res: Response): Promise<void> => {
  let tempFilePath = '';
  try {
    // 1. Fetch live reports from MongoDB
    const reports = await Report.find({});
    
    // Resolve absolute path to the Python scripts inside backend/src/graph
    const graphDir = path.join(__dirname, '..', '..', 'src', 'graph');
    const pythonScriptPath = path.join(graphDir, 'analysis.py');
    
    let analysisFile = '';
    
    if (reports.length > 0) {
      // Dump database contents to a unique temporary file
      const tempFileName = `temp_reports_${Date.now()}_${Math.random().toString(36).substring(7)}.json`;
      tempFilePath = path.join(graphDir, tempFileName);
      
      fs.writeFileSync(tempFilePath, JSON.stringify(reports, null, 2));
      analysisFile = tempFilePath;
    } else {
      // Fallback to pre-generated synthetic reports if database is empty
      analysisFile = path.join(graphDir, 'synthetic_reports.json');
    }
    
    // Determine the Python command (defaults to python)
    const pythonCmd = process.env.PYTHON_CMD || 'python';
    
    // Resolve absolute path to the Next.js public directory to export the HTML graph
    const frontendPublicDir = path.join(__dirname, '..', '..', '..', 'frontend', 'public');
    const htmlOutPath = path.join(frontendPublicDir, 'graph.html');
    
    // Ensure the frontend public directory exists (failsafe)
    if (!fs.existsSync(frontendPublicDir)) {
      fs.mkdirSync(frontendPublicDir, { recursive: true });
    }

    // Prepare shell execution command with HTML export flag
    const command = `"${pythonCmd}" "${pythonScriptPath}" --file "${analysisFile}" --html_out "${htmlOutPath}"`;
    
    // Spawn Python script as a child process
    exec(command, (error, stdout, stderr) => {
      // Remove temporary file immediately
      if (tempFilePath && fs.existsSync(tempFilePath)) {
        try {
          fs.unlinkSync(tempFilePath);
        } catch (cleanupError) {
          console.error('[cleanup]: Failed to delete temporary reports file:', cleanupError);
        }
      }
      
      if (error) {
        console.error('[exec]: Graph analysis process error:', error.message);
        res.status(500).json({
          success: false,
          message: 'Graph analysis engine execution failed',
          error: error.message,
          details: stderr
        });
        return;
      }
      
      try {
        const parsedResult = JSON.parse(stdout);
        
        // Return exactly communities, centrality, graph stats, and confidence scores
        res.status(200).json({
          success: true,
          data: {
            communities: parsedResult.communities || [],
            centrality: parsedResult.centrality || {},
            "graph stats": parsedResult["graph stats"] || {},
            "confidence scores": parsedResult["confidence scores"] || {}
          }
        });
      } catch (parseError) {
        console.error('[parse]: Failed to parse Python stdout JSON:', parseError);
        res.status(500).json({
          success: false,
          message: 'Failed to parse graph engine analysis output',
          error: (parseError as Error).message,
          rawOutput: stdout
        });
      }
    });
    
  } catch (error) {
    // Cleanup temporary file in case of exception before exec
    if (tempFilePath && fs.existsSync(tempFilePath)) {
      try {
        fs.unlinkSync(tempFilePath);
      } catch (cleanupError) {
        console.error('[cleanup]: Failed to delete temporary file on error catch:', cleanupError);
      }
    }
    
    res.status(500).json({
      success: false,
      message: 'Failed to start graph analysis process',
      error: (error as Error).message
    });
  }
};
