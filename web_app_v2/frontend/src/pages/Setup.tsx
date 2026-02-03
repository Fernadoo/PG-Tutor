import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Brain, Key, Settings, BookOpen, ChevronRight, Loader2 } from 'lucide-react';
import { useStore } from '@/store';
import { sessionApi, configApi } from '@/api/client';
import type { AvailableModel } from '@/types';

export default function Setup() {
  const navigate = useNavigate();
  const { setSession, setApiConfig, setMode, mode, apiConfig } = useStore();
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [apiKey, setApiKey] = useState(apiConfig?.api_key || '');
  const [baseUrl, setBaseUrl] = useState(apiConfig?.base_url || 'https://api.openai.com/v1');
  const [model, setModel] = useState(apiConfig?.model || 'gpt-3.5-turbo');
  const [targetQuestions, setTargetQuestions] = useState(10);
  const [availableModels, setAvailableModels] = useState<AvailableModel[]>([]);
  const [modelsLoading, setModelsLoading] = useState(false);

  useEffect(() => {
    if (mode === 'llm') {
      loadModels();
    }
  }, [mode]);

  const loadModels = async () => {
    setModelsLoading(true);
    try {
      const { models } = await configApi.getModels();
      setAvailableModels(models);
    } catch {
      setAvailableModels([
        { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo' },
        { id: 'gpt-4', name: 'GPT-4' },
        { id: 'gpt-4-turbo', name: 'GPT-4 Turbo' },
      ]);
    } finally {
      setModelsLoading(false);
    }
  };

  const handleStart = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const config = mode === 'llm' ? {
        api_key: apiKey,
        base_url: baseUrl,
        model,
      } : undefined;

      const session = await sessionApi.create({
        mode,
        config,
        target_questions: targetQuestions,
      });

      setSession(session);
      if (config) {
        setApiConfig(config);
      }
      navigate('/lesson');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create session');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-100 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-600 rounded-2xl mb-4 shadow-lg">
            <Brain className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">AI Tutor</h1>
          <p className="text-lg text-gray-600">Interactive Bayesian Learning System</p>
        </div>

        <div className="card space-y-6">
          <div className="flex gap-4 p-1 bg-gray-100 rounded-lg">
            <button
              onClick={() => setMode('simple')}
              className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-md font-medium transition-all ${
                mode === 'simple'
                  ? 'bg-white text-primary-700 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <BookOpen className="w-4 h-4" />
              Simple Mode
            </button>
            <button
              onClick={() => setMode('llm')}
              className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-md font-medium transition-all ${
                mode === 'llm'
                  ? 'bg-white text-primary-700 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Brain className="w-4 h-4" />
              LLM Mode
            </button>
          </div>

          {mode === 'llm' && (
            <div className="space-y-4 border-t border-gray-200 pt-6">
              <div className="flex items-center gap-2 text-gray-900 font-medium">
                <Key className="w-5 h-5 text-primary-600" />
                <span>API Configuration</span>
              </div>
              
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    API Key
                  </label>
                  <input
                    type="password"
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    placeholder="sk-..."
                    className="input-field"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Base URL
                    </label>
                    <input
                      type="text"
                      value={baseUrl}
                      onChange={(e) => setBaseUrl(e.target.value)}
                      placeholder="https://api.openai.com/v1"
                      className="input-field"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Model
                    </label>
                    <select
                      value={model}
                      onChange={(e) => setModel(e.target.value)}
                      className="input-field"
                      disabled={modelsLoading}
                    >
                      {availableModels.map((m) => (
                        <option key={m.id} value={m.id}>
                          {m.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div className="border-t border-gray-200 pt-6">
            <div className="flex items-center gap-2 text-gray-900 font-medium mb-3">
              <Settings className="w-5 h-5 text-primary-600" />
              <span>Session Settings</span>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Target Questions: {targetQuestions}
              </label>
              <input
                type="range"
                min="5"
                max="50"
                value={targetQuestions}
                onChange={(e) => setTargetQuestions(Number(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>5</span>
                <span>50</span>
              </div>
            </div>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm">
              {error}
            </div>
          )}

          <button
            onClick={handleStart}
            disabled={isLoading || (mode === 'llm' && !apiKey)}
            className="w-full btn-primary flex items-center justify-center gap-2 text-lg py-3"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Starting Session...
              </>
            ) : (
              <>
                Start Learning
                <ChevronRight className="w-5 h-5" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
