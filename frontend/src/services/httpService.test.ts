import { afterEach, describe, expect, it, vi } from 'vitest';

vi.mock('../config', () => ({
  config: { backendUrl: 'http://localhost:5000' },
}));

import { HttpService } from './httpService';

describe('HttpService', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('monta a URL corretamente para GET', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({ status: 'ok' }),
    } as Response);

    const service = new HttpService('http://localhost');
    const result = await service.get<{ status: string }>('/api/guidelines');

    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost/api/guidelines',
      expect.objectContaining({ method: 'GET' }),
    );
    expect(result.status).toBe('ok');
  });

  it('propaga erro HTTP com mensagem da API', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: false,
      status: 400,
      json: async () => ({ error: 'Missing email_content' }),
    } as Response);

    const service = new HttpService('http://localhost');

    await expect(service.get('/api/classify')).rejects.toThrow('Missing email_content');
  });
});
