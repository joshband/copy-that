import type { TokenRow } from './types'

interface Props {
  filter: string
  filteredCount: number
  totalCount: number
  onFilterChange: (value: string) => void
  onDownloadJson: () => void
}

export function FilterBar({
  filter,
  filteredCount,
  totalCount,
  onFilterChange,
  onDownloadJson,
}: Props) {
  return (
    <div className="ti-header">
      <div>
        <p className="eyebrow">Token Inspector</p>
        <h3>Review extracted elements</h3>
        <p className="diagnostics-subtitle">
          Hover rows to highlight on the overlay. Click to persist selection. Filter by type to focus a subset.
        </p>
      </div>
      <div className="ti-actions">
        <input
          type="text"
          placeholder="Filter by type or id…"
          value={filter}
          onChange={(e) => onFilterChange(e.target.value)}
          title={`Showing ${filteredCount} of ${totalCount} tokens`}
        />
        <button className="ghost-btn" onClick={onDownloadJson}>
          Download JSON
        </button>
      </div>
    </div>
  )
}
