import { useState } from 'react';
import { CheckCircleIcon, SparklesIcon } from '@heroicons/react/24/outline';

interface AnalysisResultsProps {
  visualDNA: any;
  aiAnalysis?: any;
}

export default function AnalysisResults({ visualDNA, aiAnalysis }: AnalysisResultsProps) {
  const [activeTab, setActiveTab] = useState<'visual-dna' | 'ai'>('visual-dna');

  if (!visualDNA) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4">
        <div className="flex items-center gap-2 text-white">
          <CheckCircleIcon className="h-6 w-6" />
          <h2 className="text-xl font-semibold">Analysis Complete</h2>
        </div>
        <p className="text-blue-100 text-sm mt-1">
          Visual DNA extracted successfully
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <div className="flex">
          <button
            onClick={() => setActiveTab('visual-dna')}
            className={`px-6 py-3 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'visual-dna'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-800'
            }`}
          >
            Visual DNA
          </button>
          {aiAnalysis && (
            <button
              onClick={() => setActiveTab('ai')}
              className={`px-6 py-3 font-medium text-sm border-b-2 transition-colors flex items-center gap-2 ${
                activeTab === 'ai'
                  ? 'border-purple-600 text-purple-600'
                  : 'border-transparent text-gray-600 hover:text-gray-800'
              }`}
            >
              <SparklesIcon className="h-4 w-4" />
              AI Insights
            </button>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        {activeTab === 'visual-dna' && (
          <div className="space-y-6">
            {/* Color Genome */}
            <Section title="Color Palette">
              <div className="flex flex-wrap gap-3">
                {visualDNA.color_genome?.palette?.slice(0, 8).map((color: any, idx: number) => (
                  <div key={idx} className="flex flex-col items-center">
                    <div
                      className="w-16 h-16 rounded-lg shadow-md border border-gray-200"
                      style={{ backgroundColor: color.hex }}
                      title={color.hex}
                    />
                    <span className="text-xs text-gray-600 mt-2">{color.hex}</span>
                    <span className="text-xs text-gray-500">
                      {color.percentage.toFixed(1)}%
                    </span>
                  </div>
                ))}
              </div>
            </Section>

            {/* Corner Style */}
            <Section title="Corner Style">
              <div className="flex items-center gap-4">
                <div className="text-sm">
                  <span className="font-semibold">Style:</span>{' '}
                  <span className="capitalize">
                    {visualDNA.corner_style?.corner_style?.replace('_', ' ')}
                  </span>
                </div>
                <div className="text-sm">
                  <span className="font-semibold">Radius:</span>{' '}
                  {visualDNA.corner_style?.estimated_radius}px
                </div>
              </div>
            </Section>

            {/* Elevation */}
            <Section title="Elevation & Shadows">
              <div className="flex items-center gap-4">
                <div className="text-sm">
                  <span className="font-semibold">Style:</span>{' '}
                  <span className="capitalize">
                    {visualDNA.elevation_model?.elevation_style}
                  </span>
                </div>
                <div className="text-sm">
                  <span className="font-semibold">Shadow Coverage:</span>{' '}
                  {visualDNA.elevation_model?.shadow_coverage?.toFixed(1)}%
                </div>
              </div>
            </Section>

            {/* Spacing */}
            <Section title="Spacing & Grid">
              <div className="flex items-center gap-4">
                <div className="text-sm">
                  <span className="font-semibold">Base Unit:</span>{' '}
                  {visualDNA.spatial_rhythm?.base_unit}px
                </div>
                <div className="text-sm">
                  <span className="font-semibold">Grid Type:</span>{' '}
                  <span className="capitalize">
                    {visualDNA.spatial_rhythm?.grid_type?.replace('_', ' ')}
                  </span>
                </div>
              </div>
            </Section>

            {/* Shape Language */}
            <Section title="Shape Language">
              <div className="flex items-center gap-4">
                <div className="text-sm">
                  <span className="font-semibold">Style:</span>{' '}
                  <span className="capitalize">
                    {visualDNA.shape_language?.geometric_style?.replace('_', ' ')}
                  </span>
                </div>
                <div className="text-sm">
                  <span className="font-semibold">Preference:</span>{' '}
                  <span className="capitalize">
                    {visualDNA.shape_language?.shape_preference}
                  </span>
                </div>
              </div>
            </Section>
          </div>
        )}

        {activeTab === 'ai' && aiAnalysis && (
          <div className="space-y-6">
            {aiAnalysis.style_analysis && (
              <Section title="Design Style Analysis">
                <pre className="text-sm bg-gray-50 p-4 rounded overflow-auto max-h-64">
                  {JSON.stringify(aiAnalysis.style_analysis, null, 2)}
                </pre>
              </Section>
            )}

            {aiAnalysis.components && (
              <Section title="Components Detected">
                <pre className="text-sm bg-gray-50 p-4 rounded overflow-auto max-h-64">
                  {JSON.stringify(aiAnalysis.components, null, 2)}
                </pre>
              </Section>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h3 className="text-sm font-semibold text-gray-900 mb-3">{title}</h3>
      {children}
    </div>
  );
}
