/**
 * Serviço HTTP base para centralizar configurações e tratamento de erros
 */

import { config } from '../config';

interface RequestConfig {
  method?: string;
  headers?: Record<string, string>;
  body?: string;
}

export class HttpService {
  private baseUrl: string;

  constructor(baseUrl: string = config.backendUrl) {
    this.baseUrl = baseUrl;
  }

  private async makeRequest<T>(endpoint: string, config: RequestConfig = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const defaultHeaders = { 'Content-Type': 'application/json' };
    
    const response = await fetch(url, {
      method: config.method || 'GET',
      headers: { ...defaultHeaders, ...config.headers },
      body: config.body,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `Erro HTTP ${response.status}`);
    }

    return response.json();
  }

  async get<T>(endpoint: string, headers?: Record<string, string>): Promise<T> {
    return this.makeRequest<T>(endpoint, { headers });
  }

  async post<T>(endpoint: string, data?: any, headers?: Record<string, string>): Promise<T> {
    return this.makeRequest<T>(endpoint, {
      method: 'POST',
      headers,
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data?: any, headers?: Record<string, string>): Promise<T> {
    return this.makeRequest<T>(endpoint, {
      method: 'PUT',
      headers,
      body: data ? JSON.stringify(data) : undefined,
    });
  }
}

export const httpService = new HttpService();
