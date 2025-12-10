import React from 'react'
import { Check, Loader2, AlertCircle } from 'lucide-react'

export interface PipelineStage {
  phase: number
  name: string
  status: 'pending' | 'active' | 'complete' | 'failed'
  description?: string
  duration?: number
}

interface PipelineStageIndicatorProps {
  stages: PipelineStage[]
  compact?: boolean
  showTimings?: boolean
}

export const PipelineStageIndicator: React.FC<PipelineStageIndicatorProps> = ({
  stages,
  compact = false,
  showTimings = true,
}) => {
  const getStageIcon = (stage: PipelineStage) => {
    switch (stage.status) {
      case 'complete':
        return <Check className="w-5 h-5 text-green-500" />
      case 'active':
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
      case 'failed':
        return <AlertCircle className="w-5 h-5 text-red-500" />
      default:
        return <div className="w-5 h-5 rounded-full border-2 border-gray-300" />
    }
  }

  const getStageColor = (stage: PipelineStage) => {
    switch (stage.status) {
      case 'complete':
        return 'bg-green-50 border-green-200'
      case 'active':
        return 'bg-blue-50 border-blue-200'
      case 'failed':
        return 'bg-red-50 border-red-200'
      default:
        return 'bg-gray-50 border-gray-200'
    }
  }

  const getTextColor = (stage: PipelineStage) => {
    switch (stage.status) {
      case 'complete':
        return 'text-green-700'
      case 'active':
        return 'text-blue-700'
      case 'failed':
        return 'text-red-700'
      default:
        return 'text-gray-700'
    }
  }

  if (compact) {
    return (
      <div className="flex items-center gap-2">
        {stages.map((stage, idx) => (
          <div key={stage.phase} className="flex items-center gap-2">
            <div
              className={`flex items-center justify-center w-8 h-8 rounded-full border-2 ${
                stage.status === 'complete'
                  ? 'bg-green-100 border-green-300'
                  : stage.status === 'active'
                    ? 'bg-blue-100 border-blue-300'
                    : stage.status === 'failed'
                      ? 'bg-red-100 border-red-300'
                      : 'bg-gray-100 border-gray-300'
              }`}
            >
              {getStageIcon(stage)}
            </div>
            {idx < stages.length - 1 && (
              <div className="w-8 h-0.5 bg-gray-300 mx-1" />
            )}
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {stages.map((stage, idx) => (
        <div key={stage.phase}>
          <div className={`p-3 rounded-lg border ${getStageColor(stage)}`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {getStageIcon(stage)}
                <div>
                  <div className={`font-semibold ${getTextColor(stage)}`}>
                    Phase {stage.phase}: {stage.name}
                  </div>
                  {stage.description && (
                    <div className="text-sm text-gray-600">
                      {stage.description}
                    </div>
                  )}
                </div>
              </div>
              {showTimings && stage.duration && (
                <div className="text-sm text-gray-500">
                  {stage.duration.toFixed(2)}s
                </div>
              )}
            </div>
          </div>

          {idx < stages.length - 1 && (
            <div className="flex justify-center py-1">
              <div className="w-0.5 h-3 bg-gray-300" />
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

export default PipelineStageIndicator
