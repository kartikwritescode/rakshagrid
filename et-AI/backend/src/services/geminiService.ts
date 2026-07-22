import { GoogleGenAI } from '@google/genai';
import dotenv from 'dotenv';

dotenv.config();

// Initialize the Gemini client. Ensure process.env.GEMINI_API_KEY is set in .env
const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

// Mock Advisory Database for RAG
const advisories = [
  {
    id: 'ADV-001',
    topic: 'Digital Arrest / Fake CBI',
    content: 'Official I4C Advisory: Law enforcement agencies like CBI, Police, or Customs DO NOT conduct "Digital Arrests" over Skype or WhatsApp video calls. They DO NOT ask you to transfer money to "safe accounts" or buy gift cards to avoid arrest. If someone claiming to be an officer demands money to clear your name in a money laundering case linked to your Aadhar or parcel, it is a scam. Disconnect immediately and report to 1930.',
    keywords: ['cbi', 'digital arrest', 'skype', 'safe account', 'money laundering', 'aadhar', 'customs', 'parcel']
  },
  {
    id: 'ADV-002',
    topic: 'Investment Fraud',
    content: 'MHA Advisory: Beware of high-return investment schemes promoted on Telegram or WhatsApp groups. Legitimate trading platforms are registered with SEBI. Scammers often show fake profits on a spoofed website or app and prevent withdrawals until you pay "taxes" or "fees".',
    keywords: ['investment', 'telegram', 'whatsapp', 'sebi', 'high return', 'trading', 'profit', 'withdrawal', 'tax']
  },
  {
    id: 'ADV-003',
    topic: 'Payment Switch / KYC Update',
    content: 'Bank Advisory: Never share OTP, UPI PIN, or click on unverified links sent via SMS for "KYC Update" or "Account Blocked". Your bank will never ask for your UPI PIN to receive money or update KYC. Entering a PIN always deducts money from your account.',
    keywords: ['kyc', 'otp', 'upi pin', 'account blocked', 'sms', 'link']
  }
];

// Simple mock vector retrieval (keyword matching instead of embeddings for this prototype phase)
export const retrieveAdvisories = (query: string) => {
  const lowercaseQuery = query.toLowerCase();
  
  // Find advisories that match keywords
  const matched = advisories.filter(adv => 
    adv.keywords.some(keyword => lowercaseQuery.includes(keyword))
  );

  // If no match, return a general advisory or empty
  if (matched.length === 0) return advisories; // return all as fallback for LLM to decide

  return matched;
};

export const generateFraudShieldResponse = async (userMessage: string, contextHistory: {role: string, content: string}[]) => {
  try {
    // 1. Retrieve relevant advisories
    const relevantAdvisories = retrieveAdvisories(userMessage);
    const advisoryContext = relevantAdvisories.map(a => `[${a.topic}]: ${a.content}`).join('\n\n');

    // 2. Format history for the LLM
    const formattedHistory = contextHistory.map(msg => `${msg.role === 'user' ? 'User' : 'Assistant'}: ${msg.content}`).join('\n');

    // 3. Construct System Prompt with RAG context
    const systemInstruction = `You are "Citizen Fraud Shield", an official AI assistant by the Raksha Grid project (I4C/MHA).
Your goal is to assess a citizen's situation, provide calm and authoritative guidance, and protect them from scams.
Use the provided official advisories to ground your response. Do not invent new legal procedures.
Keep your response concise, empathetic, and action-oriented.

ABSOLUTE STRICT GUARDRAIL: You are restricted EXCLUSIVELY to topics regarding cyber frauds, scams, digital safety, and official advisories. If the user asks ANY question outside this scope (e.g., general knowledge, recipes, coding, casual chat, facts about countries or people), YOU MUST REFUSE TO ANSWER IT. Do NOT provide the answer and then warn them. You MUST ONLY output the following exact warning:
"I am the Citizen Fraud Shield AI. Please kindly ask questions related to cyber frauds, scams, or digital safety, so I can use my intelligence to assist you."

Official Advisories:
${advisoryContext}

Previous Conversation:
${formattedHistory}
`;

    // 4. Call Gemini
    try {
      const response = await ai.models.generateContent({
        model: 'gemini-3.6-flash', // fast model suitable for chat
        contents: userMessage,
        config: {
          systemInstruction,
          temperature: 0.3, // keep it grounded
        }
      });
      return response.text;
    } catch (apiError) {
      console.warn('Gemini API failed, falling back to mock response', apiError);
      if (relevantAdvisories.length > 0) {
        return `[MOCK RESPONSE (API Quota Exceeded)]\n\nBased on official advisories:\n${relevantAdvisories[0].content}\n\nPlease stay calm and do not share any details.`;
      }
      return "[MOCK RESPONSE (API Quota Exceeded)]\n\nI'm sorry, I am currently facing network issues but please do not share any personal information or transfer money to unknown entities. Contact 1930 immediately.";
    }
  } catch (error) {
    console.error('Error generating Fraud Shield response:', error);
    throw new Error('Failed to generate response from AI');
  }
};

export const calculateRiskScore = async (transcript: string) => {
  try {
    const prompt = `You are a scam detection module. Analyze the following conversation transcript between a citizen and a potential scammer (or the citizen describing a situation).
Output ONLY a valid JSON object with the following structure:
{
  "score": <number between 0 and 100, where 100 is definite fraud>,
  "level": <"Safe", "Low Risk", "Medium Risk", "High Risk", or "Critical">,
  "flaggedFeatures": [<array of short strings identifying scam tactics, e.g. "Urgency", "Payment Switch", "Authority Impersonation">],
  "reasoning": <"A short one sentence explanation">
}

Transcript:
${transcript}`;

    const response = await ai.models.generateContent({
      model: 'gemini-3.6-flash',
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        temperature: 0.1
      }
    });

    const text = response.text || "{}";
    return JSON.parse(text);
  } catch (error) {
    console.error('Error calculating risk score:', error);
    // Fallback safe response
    return {
      score: 50,
      level: "Medium Risk",
      flaggedFeatures: ["Analysis Error"],
      reasoning: "Unable to complete risk analysis."
    };
  }
};
