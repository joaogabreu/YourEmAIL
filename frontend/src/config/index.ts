/**
 * Configurações centralizadas da aplicação
 */

declare global {
  interface Window {
    __RUNTIME_CONFIG__?: {
      backendUrl?: string;
    };
  }
}

const runtimeUrl = window.__RUNTIME_CONFIG__?.backendUrl;
const buildTimeUrl = import.meta.env.VITE_BACKEND_URL as string | undefined;

export const config = {
  backendUrl:
    runtimeUrl !== undefined
      ? runtimeUrl
      : buildTimeUrl || (import.meta.env.PROD ? '' : 'http://localhost:5000'),
  
  // Google APIs
  google: {
    clientId: import.meta.env.VITE_GOOGLE_CLIENT_ID,
    apiKey: import.meta.env.VITE_GOOGLE_API_KEY,
    scopes: 'https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.modify',
    discoveryDocs: ['https://www.googleapis.com/discovery/v1/apis/gmail/v1/rest'],
  },
  
  // Scripts externos
  scripts: {
    gapi: 'https://apis.google.com/js/api.js',
  },
  
  // Configurações padrão
  defaults: {
    maxEmailResults: 20,
  },
} as const;
