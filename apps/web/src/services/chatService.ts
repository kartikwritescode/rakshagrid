// apps/web/src/services/chatService.ts
/**
 * Frontend Service for Citizen FraudShield AI Chat Advisor.
 */

import { apiClient } from '../api/client';
import { API_ENDPOINTS } from '../constants/apiEndpoints';
import { ChatRequest, ChatResponse } from '../types/apiTypes';

export const chatService = {
  async sendMessage(payload: ChatRequest): Promise<ChatResponse> {
    return apiClient<ChatResponse>(API_ENDPOINTS.CHAT, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
};
