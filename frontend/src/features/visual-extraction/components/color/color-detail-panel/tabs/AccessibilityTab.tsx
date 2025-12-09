import { AccessibilityVisualizer } from '../../../../../../components/AccessibilityVisualizer'
import type { TabProps } from '../types'

export function AccessibilityTab({ color }: TabProps) {
  return (
    <div className="accessibility-content">
      <AccessibilityVisualizer
        hex={color.hex}
        wcagContrastWhite={color.wcag_contrast_on_white}
        wcagContrastBlack={color.wcag_contrast_on_black}
        wcagAACompliantText={color.wcag_aa_compliant_text}
        wcagAAACompliantText={color.wcag_aaa_compliant_text}
        wcagAACompliantNormal={color.wcag_aa_compliant_normal}
        wcagAAACompliantNormal={color.wcag_aaa_compliant_normal}
        colorblindSafe={color.colorblind_safe}
      />
    </div>
  )
}
