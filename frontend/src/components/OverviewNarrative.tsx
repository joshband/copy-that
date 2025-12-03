import React from 'react'
import './OverviewNarrative.css'
import type { ColorToken } from '../types'

interface OverviewNarrativeProps {
  colors: ColorToken[]
  colorCount: number
  aliasCount: number
  spacingCount: number
  multiplesCount: number
  typographyCount: number
}

export function OverviewNarrative({
  colors,
  colorCount,
  aliasCount,
  spacingCount,
  multiplesCount,
  typographyCount
}: OverviewNarrativeProps) {
  // Analyze the palette characteristics
  const analyzeTemperature = () => {
    if (colors.length === 0) return 'balanced'
    const warmCount = colors.filter(c => c.temperature === 'warm').length
    const coolCount = colors.filter(c => c.temperature === 'cool').length
    const ratio = warmCount / (warmCount + coolCount || 1)
    if (ratio > 0.6) return 'warm'
    if (ratio < 0.4) return 'cool'
    return 'balanced'
  }

  const analyzeSaturation = () => {
    if (colors.length === 0) return 'medium'
    const highSat = colors.filter(c => c.saturation_level === 'high').length
    const lowSat = colors.filter(c => c.saturation_level === 'low' || c.saturation_level === 'desaturated').length
    const ratio = highSat / (highSat + lowSat || 1)
    if (ratio > 0.6) return 'vivid'
    if (ratio < 0.4) return 'muted'
    return 'balanced'
  }

  const classifyArtMovement = () => {
    const temp = analyzeTemperature()
    const sat = analyzeSaturation()
    const complexity = colors.length

    // Art movement classification based on palette characteristics
    if (sat === 'vivid' && temp === 'warm' && complexity >= 8) return 'Expressionism'
    if (sat === 'vivid' && temp === 'cool' && complexity >= 8) return 'Fauvism'
    if (sat === 'muted' && complexity <= 4) return 'Minimalism'
    if (sat === 'muted' && temp === 'cool') return 'Swiss Modernism'
    if (sat === 'vivid' && complexity >= 12) return 'Art Deco'
    if (temp === 'warm' && sat === 'muted') return 'Brutalism'
    if (sat === 'balanced' && temp === 'balanced' && complexity >= 6) return 'Contemporary'
    if (complexity <= 3) return 'Neo-Minimalism'
    if (sat === 'vivid' && temp === 'balanced') return 'Postmodernism'
    return 'Modern Design'
  }

  const getEmotionalTone = () => {
    const temp = analyzeTemperature()
    const sat = analyzeSaturation()

    if (temp === 'warm' && sat === 'vivid') {
      return {
        emotion: 'energetic & passionate',
        description: 'This palette radiates warmth and intensity. It commands attention and evokes excitement, creativity, and enthusiasm.'
      }
    }
    if (temp === 'cool' && sat === 'vivid') {
      return {
        emotion: 'calm & confident',
        description: 'This palette conveys trust and serenity. The vibrant cool tones suggest innovation and forward-thinking without overwhelming.'
      }
    }
    if (sat === 'muted') {
      return {
        emotion: 'sophisticated & refined',
        description: 'This palette whispers rather than shouts. Muted tones suggest maturity, elegance, and thoughtful restraint.'
      }
    }
    if (temp === 'balanced') {
      return {
        emotion: 'harmonious & accessible',
        description: 'This palette achieves equilibrium. Balanced colors suggest inclusivity, versatility, and universal appeal.'
      }
    }
    return {
      emotion: 'expressive & dynamic',
      description: 'This palette tells a story through color harmony and intentional contrast.'
    }
  }

  const getDesignEra = () => {
    const complexity = colors.length

    if (complexity <= 2) return 'Monochromatic Focus'
    if (complexity <= 4) return 'Limited Palette Era'
    if (complexity <= 8) return 'Structured Harmony'
    if (complexity <= 12) return 'Rich Ecosystem'
    return 'Comprehensive System'
  }

  const generateNarrative = () => {
    const temp = analyzeTemperature()
    const colorDiversity = colors.length > 8 ? 'diverse and carefully curated' : colors.length > 4 ? 'focused and intentional' : 'minimal and precise'

    if (temp === 'warm') {
      return `Your design language speaks in warm tones—inviting and approachable. This palette naturally encourages engagement and connection, making it ideal for experiences where warmth and approachability matter.`
    }
    if (temp === 'cool') {
      return `Your design language speaks in cool tones—calm and trustworthy. This palette naturally supports clarity and focus, making it ideal for experiences where reliability and professionalism matter.`
    }
    return `Your design language balances warmth and coolness. This versatile palette adapts to multiple contexts, supporting both energetic moments and calming ones with equal grace.`
  }

  const movement = classifyArtMovement()
  const emotional = getEmotionalTone()
  const era = getDesignEra()
  const temperature = analyzeTemperature()
  const saturation = analyzeSaturation()

  return (
    <div className="overview-narrative">
      <div className="narrative-intro">
        <h2>Your Design Palette</h2>
        <p className="intro-text">
          A system of <strong>{colorCount} colors</strong>, <strong>{spacingCount} spacing tokens</strong>, and{' '}
          <strong>{typographyCount} typography scales</strong> that work together to define your visual language.
        </p>
      </div>

      <div className="narrative-grid">
        {/* Art Movement */}
        <div className="narrative-card movement">
          <div className="card-icon">🎨</div>
          <h3>Art Movement</h3>
          <p className="movement-name">{movement}</p>
          <p className="movement-description">
            Your palette aligns with{' '}
            {movement === 'Expressionism'
              ? 'Expressionism—bold, emotional, and unafraid to make a statement.'
              : movement === 'Fauvism'
                ? 'Fauvism—wild colors used in a liberated, intuitive way.'
                : movement === 'Minimalism'
                  ? 'Minimalism—intentional reduction to essential elements.'
                  : movement === 'Swiss Modernism'
                    ? 'Swiss Modernism—clean, rational, and universally legible.'
                    : movement === 'Brutalism'
                      ? 'Brutalism—raw, honest, and unapologetically bold.'
                      : movement === 'Art Deco'
                        ? 'Art Deco—geometric precision meets visual luxury.'
                        : movement === 'Contemporary'
                          ? 'Contemporary Design—balanced, accessible, forward-thinking.'
                          : movement === 'Neo-Minimalism'
                            ? 'Neo-Minimalism—less is more, but with contemporary flair.'
                            : 'Modern Design—thoughtful and intentional color strategy.'}
          </p>
        </div>

        {/* Emotional Tone */}
        <div className="narrative-card emotional">
          <div className="card-icon">💭</div>
          <h3>Emotional Tone</h3>
          <p className="emotion-label">{emotional.emotion}</p>
          <p className="emotion-description">{emotional.description}</p>
        </div>

        {/* Design Era */}
        <div className="narrative-card era">
          <div className="card-icon">⏱️</div>
          <h3>Design Complexity</h3>
          <p className="era-name">{era}</p>
          <p className="era-description">
            With {colors.length} colors working in concert, you've created a {colorCount <= 4 ? 'lean' : 'comprehensive'} visual
            system that {colorCount <= 4 ? 'maximizes impact through restraint' : 'handles multiple design scenarios'}.
          </p>
        </div>

        {/* Temperature Profile */}
        <div className="narrative-card temperature">
          <div className="card-icon">🌡️</div>
          <h3>Temperature Profile</h3>
          <p className="temp-label">{temperature.charAt(0).toUpperCase() + temperature.slice(1)}</p>
          <p className="temp-description">
            {temperature === 'warm'
              ? 'Warm colors dominate your palette. They naturally draw attention and create a sense of immediacy and warmth.'
              : temperature === 'cool'
                ? 'Cool colors define your palette. They suggest calm, trust, and create visual breathing room.'
                : 'Your palette balances warm and cool equally. This versatility makes it adaptable to diverse contexts.'}
          </p>
        </div>

        {/* Saturation Profile */}
        <div className="narrative-card saturation">
          <div className="card-icon">✨</div>
          <h3>Saturation Character</h3>
          <p className="sat-label">{saturation.charAt(0).toUpperCase() + saturation.slice(1)}</p>
          <p className="sat-description">
            {saturation === 'vivid'
              ? 'Vibrant and saturated colors create energy and visual impact. They demand attention and work well for primary actions and key moments.'
              : saturation === 'muted'
                ? 'Muted, desaturated colors convey sophistication and calm. They provide visual rest and work beautifully for supporting elements.'
                : 'Balanced saturation creates visual harmony. Neither too intense nor too subdued, these colors adapt naturally to their context.'}
          </p>
        </div>

        {/* System Health */}
        <div className="narrative-card health">
          <div className="card-icon">💪</div>
          <h3>System Health</h3>
          <p className="health-metric">
            {colorCount + spacingCount + typographyCount} total tokens across all categories
          </p>
          <p className="health-description">
            {colorCount > 0 && spacingCount > 0 && typographyCount > 0
              ? 'Your system is well-rounded, covering color, spacing, and typography comprehensively.'
              : colorCount > 0 && spacingCount > 0
                ? 'Your system has colors and spacing defined. Consider adding typography tokens for complete coverage.'
                : 'Your color palette is defined. Complement it with spacing and typography scales for a complete system.'}
          </p>
        </div>
      </div>

      <div className="narrative-story">
        <h3>Your Design Story</h3>
        <p>{generateNarrative()}</p>

        {colors.length > 0 && (
          <div className="color-palette-preview">
            <h4>Palette at a Glance</h4>
            <div className="color-swatches">
              {colors.slice(0, 10).map((color, idx) => {
                const semanticLabel = typeof color.semantic_names === 'string' ? color.semantic_names : typeof color.semantic_names === 'object' && color.semantic_names ? Object.values(color.semantic_names)[0] : null
                return (
                  <div key={idx} className="swatch-item" title={String(semanticLabel) || color.hex}>
                    <div
                      className="swatch"
                      style={{
                        backgroundColor: color.hex,
                        border:
                          color.hex.toLowerCase() === '#ffffff' || color.hex.toLowerCase() === '#fff'
                            ? '1px solid #ddd'
                            : 'none'
                      }}
                    />
                    <span className="swatch-label">{String(semanticLabel).split('_')[0] || color.hex.slice(1, 4).toUpperCase()}</span>
                  </div>
                )
              })}
              {colors.length > 10 && (
                <div className="swatch-item more">
                  <div className="swatch">+{colors.length - 10}</div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <div className="narrative-insight">
        <h3>Design System Insight</h3>
        <ul>
          <li>
            <strong>Color Foundation:</strong> {aliasCount} color aliases provide semantic meaning and consistency across your
            application.
          </li>
          <li>
            <strong>Spacing Logic:</strong> {multiplesCount} spacing multiples create rhythm and proportional relationships in your
            layouts.
          </li>
          <li>
            <strong>Visual Hierarchy:</strong> Your system supports multiple scales of typography, from headlines to body text to
            fine print.
          </li>
          <li>
            <strong>Cohesion Strategy:</strong> Every token in this system is interconnected—colors, spacing, and type scales work
            together as a unified whole.
          </li>
        </ul>
      </div>

      <div className="narrative-cta">
        <p>Explore individual tokens in the sections below to dive deeper into each element of your design system.</p>
      </div>
    </div>
  )
}
