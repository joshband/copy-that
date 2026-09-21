import type { ColorToken } from '../../../types/index'

interface Props {
  selectedColor: ColorToken
}

export function PickerTab({ selectedColor }: Props) {
  return (
    <div className="picker-content">
      <h4>Color Sampler</h4>
      <p className="picker-info">Build custom palettes by sampling colors from your image.</p>
      <div className="picker-tools">
        <button className="tool-btn">📌 Pin this color</button>
        <button className="tool-btn">🎯 Find similar</button>
        <button className="tool-btn">🔄 Get complementary</button>
      </div>
      <div className="pinned-colors">
        <h5>Pinned</h5>
        <div className="pinned-list">
          <div className="pinned-item" style={{ backgroundColor: selectedColor.hex }} />
        </div>
      </div>
    </div>
  )
}
