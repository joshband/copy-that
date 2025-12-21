import { HarmonyVisualizer } from '../../HarmonyVisualizer'
import type { TabProps } from '../types'

export function HarmonyTab({ color }: TabProps) {
  if (!color.harmony) {
    return (
      <div className="harmony-content">
        <div className="empty-state">
          <p>No harmony classification available for this color</p>
        </div>
      </div>
    )
  }

  return (
    <div className="harmony-content">
      <HarmonyVisualizer harmony={color.harmony} hex={color.hex} />
    </div>
  )
}
