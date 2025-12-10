import type { ColorToken } from '../../../../../types'

export type { ColorToken }

export type TabType = 'overview' | 'harmony' | 'accessibility' | 'properties' | 'naming_styles' | 'state_variants' | 'diagnostics'

export type Props = {
  color: ColorToken | null
  debugOverlay?: string
  isAlias?: boolean
  aliasTargetId?: string
}

export type TabProps = {
  color: ColorToken
}

export type DiagnosticsTabProps = {
  overlay: string
}
