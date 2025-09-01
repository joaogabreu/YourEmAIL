import { useState, useCallback, useEffect } from 'react';
import { guidelinesService } from '../services/guidelinesService';

interface UseGuidelinesReturn {
  guidelines: string;
  produtivoText: string;
  improdutivoText: string;
  setProdutivoText: (text: string) => void;
  setImprodutivoText: (text: string) => void;
  saveGuidelines: () => Promise<void>;
  resetGuidelines: () => Promise<void>;
  isLoading: boolean;
}

export const useGuidelines = (): UseGuidelinesReturn => {
  const [guidelines, setGuidelines] = useState<string>('');
  const [produtivoText, setProdutivoText] = useState<string>('');
  const [improdutivoText, setImprodutivoText] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const data = await guidelinesService.fetch();
        if (!active) return;
        setProdutivoText(data.produtivo_text ?? '');
        setImprodutivoText(data.improdutivo_text ?? '');
        setGuidelines(data.guidelines ?? '');
      } catch (err) {
        console.warn('Não foi possível carregar guidelines do banco:', err);
      } finally {
        if (active) setIsLoading(false);
      }
    })();
    return () => { active = false; };
  }, []);

  const saveGuidelines = useCallback(async () => {
    const saved = await guidelinesService.save(produtivoText, improdutivoText);
    setGuidelines(saved.guidelines ?? '');
    setProdutivoText(saved.produtivo_text ?? '');
    setImprodutivoText(saved.improdutivo_text ?? '');
  }, [produtivoText, improdutivoText]);

  const resetGuidelines = useCallback(async () => {
    const saved = await guidelinesService.save('', '');
    setProdutivoText(saved.produtivo_text ?? '');
    setImprodutivoText(saved.improdutivo_text ?? '');
    setGuidelines(saved.guidelines ?? '');
  }, []);

  return {
    guidelines,
    produtivoText,
    improdutivoText,
    setProdutivoText,
    setImprodutivoText,
    saveGuidelines,
    resetGuidelines,
    isLoading,
  };
};
