import { HarmonyVisualizer } from '../../HarmonyVisualizer'
import type { TabProps } from '../../types'

export function HarmonyTab({ color }: TabProps) {
  return (
    <div className="harmony-content">
      <HarmonyVisualizer harmony={color.harmony ?? ''} hex={color.hex} />
    </div>
  )
}
