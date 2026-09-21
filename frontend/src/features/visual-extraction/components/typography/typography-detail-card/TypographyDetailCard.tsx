import { useTypographyTokens } from './hooks'
import { TokenCard } from './TokenCard'

export default function TypographyDetailCard() {
  const tokens = useTypographyTokens()

  if (!tokens.length) {
    return null
  }

  return (
    <div className="typo-detail-cards">
      <div className="typo-detail-title">Typography Details & Metrics</div>
      <div className="typo-detail-grid">
        {tokens.map((token) => (
          <TokenCard key={token.id} token={token} />
        ))}
      </div>
    </div>
  )
}
