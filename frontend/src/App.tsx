import { useState } from 'react';
import ImageUploader from './components/ImageUploader';
import AnalysisResults from './components/AnalysisResults';
import ComponentLibraryBrowser from './components/ComponentLibraryBrowser';
import PrototypeBuilder from './components/PrototypeBuilder';
import api from './api/client';
import { SparklesIcon, ArrowPathIcon, CheckCircleIcon } from '@heroicons/react/24/outline';

type WorkflowStep = 'upload' | 'analyze' | 'generate' | 'build';

function App() {
  const [currentStep, setCurrentStep] = useState<WorkflowStep>('upload');
  const [projectId, setProjectId] = useState<string | null>(null);
  const [projectName, setProjectName] = useState('My Design System');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Analysis state
  const [visualDNA, setVisualDNA] = useState<any>(null);
  const [aiAnalysis, setAIAnalysis] = useState<any>(null);

  // Component library state
  const [componentLibrary, setComponentLibrary] = useState<any>(null);

  const handleImagesUploaded = async (files: File[]) => {
    setIsLoading(true);
    setError(null);

    try {
      // Create project if needed
      let pid = projectId;
      if (!pid) {
        const { project_id } = await api.createProject(projectName, true);
        pid = project_id;
        setProjectId(pid);
      }

      // Upload images
      await api.uploadImages(pid, files);

      // Move to analyze step
      setCurrentStep('analyze');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnalyze = async () => {
    if (!projectId) return;

    setIsLoading(true);
    setError(null);

    try {
      const result = await api.analyzeProject(projectId);
      setVisualDNA(result.visual_dna);
      setAIAnalysis(result.ai_analysis);
      setCurrentStep('generate');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerate = async () => {
    if (!projectId) return;

    setIsLoading(true);
    setError(null);

    try {
      const result = await api.generateDesignSystem(projectId, {
        export_formats: ['css', 'json', 'tailwind'],
      });

      setComponentLibrary(result.component_library);
      setCurrentStep('build');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Generation failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleExportSystem = async () => {
    if (!projectId) return;

    try {
      const blob = await api.exportDesignSystem(projectId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${projectName}-design-system.zip`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Export failed');
    }
  };

  const resetWorkflow = () => {
    setCurrentStep('upload');
    setProjectId(null);
    setVisualDNA(null);
    setAIAnalysis(null);
    setComponentLibrary(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Copy That
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                Generative UI Design System Builder
              </p>
            </div>

            {projectId && (
              <button
                onClick={resetWorkflow}
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowPathIcon className="h-4 w-4" />
                Start Over
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Progress Steps */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            {[
              { key: 'upload', label: 'Upload Images', icon: '📤' },
              { key: 'analyze', label: 'Analyze Style', icon: '🔍' },
              { key: 'generate', label: 'Generate Components', icon: '🎨' },
              { key: 'build', label: 'Build Prototype', icon: '🏗️' },
            ].map((step, index) => (
              <div key={step.key} className="flex items-center flex-1">
                <div className="flex items-center gap-3">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center text-lg ${
                      currentStep === step.key
                        ? 'bg-blue-600 text-white'
                        : index < ['upload', 'analyze', 'generate', 'build'].indexOf(currentStep)
                        ? 'bg-green-600 text-white'
                        : 'bg-gray-200 text-gray-600'
                    }`}
                  >
                    {index < ['upload', 'analyze', 'generate', 'build'].indexOf(currentStep) ? (
                      <CheckCircleIcon className="h-6 w-6" />
                    ) : (
                      step.icon
                    )}
                  </div>
                  <span
                    className={`text-sm font-medium ${
                      currentStep === step.key ? 'text-blue-600' : 'text-gray-600'
                    }`}
                  >
                    {step.label}
                  </span>
                </div>

                {index < 3 && (
                  <div className="flex-1 h-0.5 bg-gray-200 mx-4">
                    <div
                      className={`h-full transition-all ${
                        index < ['upload', 'analyze', 'generate', 'build'].indexOf(currentStep)
                          ? 'bg-green-600'
                          : 'bg-gray-200'
                      }`}
                      style={{
                        width:
                          index < ['upload', 'analyze', 'generate', 'build'].indexOf(currentStep)
                            ? '100%'
                            : '0%',
                      }}
                    />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800 font-medium">Error: {error}</p>
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="mb-6 p-6 bg-white rounded-lg shadow-md">
            <div className="flex items-center gap-3">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600" />
              <span className="text-gray-700 font-medium">Processing...</span>
            </div>
          </div>
        )}

        {/* Step: Upload */}
        {currentStep === 'upload' && (
          <ImageUploader onImagesReady={handleImagesUploaded} />
        )}

        {/* Step: Analyze */}
        {currentStep === 'analyze' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-md p-8 text-center">
              <SparklesIcon className="h-16 w-16 text-blue-600 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Ready to Analyze
              </h2>
              <p className="text-gray-600 mb-6">
                We'll extract the visual DNA from your reference images
              </p>
              <button
                onClick={handleAnalyze}
                disabled={isLoading}
                className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Start Analysis
              </button>
            </div>

            {visualDNA && <AnalysisResults visualDNA={visualDNA} aiAnalysis={aiAnalysis} />}
          </div>
        )}

        {/* Step: Generate */}
        {currentStep === 'generate' && (
          <div className="space-y-6">
            {visualDNA && <AnalysisResults visualDNA={visualDNA} aiAnalysis={aiAnalysis} />}

            <div className="bg-white rounded-lg shadow-md p-8 text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Generate Design System
              </h2>
              <p className="text-gray-600 mb-6">
                Create a complete UI component library based on the extracted style
              </p>
              <button
                onClick={handleGenerate}
                disabled={isLoading}
                className="px-8 py-3 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Generate Components
              </button>
            </div>
          </div>
        )}

        {/* Step: Build */}
        {currentStep === 'build' && componentLibrary && (
          <div className="space-y-6">
            {/* Export Options */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Export Design System
              </h3>
              <div className="flex gap-3">
                <button
                  onClick={handleExportSystem}
                  className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
                >
                  Download Complete System
                </button>
                <button
                  onClick={() => window.open(`/api/projects/${projectId}/tokens?format=css`, '_blank')}
                  className="px-6 py-3 border-2 border-gray-300 hover:border-gray-400 text-gray-700 font-medium rounded-lg transition-colors"
                >
                  View CSS Tokens
                </button>
                <button
                  onClick={() => window.open(`/api/projects/${projectId}/tokens?format=json`, '_blank')}
                  className="px-6 py-3 border-2 border-gray-300 hover:border-gray-400 text-gray-700 font-medium rounded-lg transition-colors"
                >
                  View JSON Tokens
                </button>
              </div>
            </div>

            {/* Component Library */}
            <ComponentLibraryBrowser
              projectId={projectId || ''}
              components={componentLibrary.components}
            />

            {/* Prototype Builder */}
            <PrototypeBuilder projectName={projectName} />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-6 py-6 text-center text-sm text-gray-600">
          <p>
            Copy That - Generative UI Design System Builder • Built with React,
            FastAPI, and Computer Vision
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
