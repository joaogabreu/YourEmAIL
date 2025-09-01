import { httpService } from './httpService';
import { getUserKey } from '../utils/userKey';

export interface GuidelinesPayload {
  produtivo_text: string;
  improdutivo_text: string;
  guidelines: string;
}

function userHeaders(): Record<string, string> {
  return { 'X-User-Key': getUserKey() };
}

export const guidelinesService = {
  async fetch(): Promise<GuidelinesPayload> {
    return httpService.get<GuidelinesPayload>('/api/guidelines', userHeaders());
  },

  async save(produtivoText: string, improdutivoText: string): Promise<GuidelinesPayload> {
    return httpService.put<GuidelinesPayload>(
      '/api/guidelines',
      { produtivo_text: produtivoText, improdutivo_text: improdutivoText },
      userHeaders(),
    );
  },
};
