import { generateFraudShieldResponse, calculateRiskScore } from "./src/services/geminiService";
import dotenv from "dotenv";
dotenv.config();

async function runTest() {
  try {
    const chatRes = await generateFraudShieldResponse("Someone claiming to be from CBI says my Aadhar is linked to money laundering", []);
    console.log("Chat Response:", chatRes);

    const riskRes = await calculateRiskScore("Someone claiming to be from CBI says my Aadhar is linked to money laundering");
    console.log("Risk Score:", riskRes);
  } catch (err) {
    console.error("Test Error:", err);
  }
}
runTest();
