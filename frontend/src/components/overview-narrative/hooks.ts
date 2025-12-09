import { useMemo } from 'react'
import type { ColorToken } from '../../types'
import type {
  TemperatureType,
  SaturationType,
  ArtMovement,
  EmotionalTone,
  DesignEra
} from './types'

export function usePaletteAnalysis(colors: ColorToken[]) {
  return useMemo(() => {
    const analyzeTemperature = (): TemperatureType => {
      if (colors.length === 0) return 'balanced'
      const warmCount = colors.filter(c => c.temperature === 'warm').length
      const coolCount = colors.filter(c => c.temperature === 'cool').length
      const ratio = warmCount / (warmCount + coolCount || 1)
      if (ratio > 0.6) return 'warm'
      if (ratio < 0.4) return 'cool'
      return 'balanced'
    }

    const analyzeSaturation = (): SaturationType => {
      if (colors.length === 0) return 'balanced'
      const highSat = colors.filter(c => c.saturation_level === 'high').length
      const lowSat = colors.filter(
        c => c.saturation_level === 'low' || c.saturation_level === 'desaturated'
      ).length
      const ratio = highSat / (highSat + lowSat || 1)
      if (ratio > 0.6) return 'vivid'
      if (ratio < 0.4) return 'muted'
      return 'balanced'
    }

    const temp = analyzeTemperature()
    const sat = analyzeSaturation()

    return { temp, sat }
  }, [colors])
}

export function useArtMovementClassification(colors: ColorToken[]) {
  const { temp, sat } = usePaletteAnalysis(colors)

  return useMemo((): ArtMovement => {
    const complexity = colors.length

    // Check most specific conditions first (temperature + saturation specific)
    if (sat === 'vivid' && temp === 'warm' && complexity >= 8) return 'Expressionism'
    if (sat === 'vivid' && temp === 'cool') return 'Fauvism'
    // Then check remaining vivid conditions (but exclude cool which already returned)
    if (sat === 'vivid' && complexity >= 12 && temp !== 'cool') return 'Art Deco'
    if (sat === 'vivid' && temp === 'balanced') return 'Postmodernism'
    // Then muted conditions
    if (sat === 'muted' && complexity <= 4) return 'Minimalism'
    if (sat === 'muted' && temp === 'cool') return 'Swiss Modernism'
    if (temp === 'warm' && sat === 'muted') return 'Brutalism'
    // Then balanced conditions
    if (sat === 'balanced' && temp === 'balanced' && complexity >= 6) return 'Contemporary'
    // Finally simplicity-based conditions
    if (complexity <= 3) return 'Neo-Minimalism'
    return 'Modern Design'
  }, [temp, sat, colors.length])
}

export function useEmotionalTone(colors: ColorToken[]): EmotionalTone {
  const { temp, sat } = usePaletteAnalysis(colors)

  return useMemo((): EmotionalTone => {
    if (temp === 'warm' && sat === 'vivid') {
      return {
        emotion: 'energetic & passionate',
        description:
          "This palette doesn't just enter the room—it kicks the door down, does a little dance, and demands everyone's attention. Pure unapologetic warmth and vibrancy, like a sunset that refuses to fade quietly."
      }
    }
    if (temp === 'cool' && sat === 'vivid') {
      return {
        emotion: 'calm & confident',
        description:
          'These colors are the person at the party who stays perfectly composed while everyone else is losing it. Cool, electric, vibrant—but somehow still the most chill presence in the room. Pure future-forward zen.'
      }
    }
    if (sat === 'muted') {
      return {
        emotion: 'sophisticated & refined',
        description:
          "Your palette went to design school in Europe and came back wearing cashmere. These muted tones whisper when they could shout, pause when they could rush. It's giving 'I'm too tasteful to try this hard.'"
      }
    }
    if (temp === 'balanced') {
      return {
        emotion: 'harmonious & accessible',
        description:
          'The Switzerland of color palettes—diplomatically balanced, universally appealing, somehow making everyone feel welcome. Not boring. Strategic. Like a really good playlist that transitions seamlessly between genres.'
      }
    }
    return {
      emotion: 'expressive & dynamic',
      description:
        'This palette has opinions and wants you to know about them. Every color choice tells a micro-story, building toward something larger and more interesting than the sum of its hex codes.'
    }
  }, [temp, sat])
}

export function useDesignEra(colors: ColorToken[]): DesignEra {
  return useMemo((): DesignEra => {
    const complexity = colors.length

    if (complexity <= 2) return 'Monochromatic Focus'
    if (complexity <= 4) return 'Limited Palette Era'
    if (complexity <= 8) return 'Structured Harmony'
    if (complexity <= 12) return 'Rich Ecosystem'
    return 'Comprehensive System'
  }, [colors.length])
}

export function useNarrative(colors: ColorToken[]): string {
  const { temp, sat } = usePaletteAnalysis(colors)

  return useMemo((): string => {
    const count = colors.length

    // Rich, whimsical narratives based on palette characteristics
    if (temp === 'warm' && sat === 'vivid') {
      return `Imagine a sunset crashed into a creative studio and decided to stick around permanently—that's your palette. These ${count} colors aren't here to play it safe; they're here to make people FEEL things before they even process what they're looking at. Every hue pulses with the kind of warmth that makes you want to lean in closer, the kind of vibrancy that photographs beautifully and screenshots even better. This is a palette for brands that get quoted, products that spark joy spirals, and interfaces that users genuinely miss when they're using boring competitors. It's not corporate. It's not safe. It's alive, and it knows exactly what it's doing. If your brand were a person, it would be the one everyone gravitates toward at parties—magnetic, memorable, unapologetically colorful.`
    }
    if (temp === 'cool' && sat === 'vivid') {
      return `Picture standing inside a glacier lit by bioluminescent algae while a synth-wave soundtrack plays in your head—that's the exact vibe these ${count} colors are channeling. They're electric without being aggressive, bold without screaming, innovative without being alienating. This palette speaks fluent "future" but in a way that somehow feels calming, like your most tech-savvy friend explaining blockchain over herbal tea. It's perfect for products that need to convey "we're disrupting everything BUT you're totally safe here"—fintech with emotional intelligence, meditation apps designed by engineers, healthcare technology that actually cares. These colors don't just suggest trust; they architect it pixel by pixel, creating interfaces where people feel both excited about innovation and secure in stability.`
    }
    if (temp === 'warm' && sat === 'muted') {
      return `This palette tastes like artisanal sourdough in a sun-soaked café where every piece of furniture has a story and nothing costs less than three digits. ${count} colors that have been aged like fine wine, weathered like reclaimed barn wood, refined like... well, like someone spent actual time thinking about this instead of just cranking up the saturation slider. These are the tones of things made by hand, touched by humans, valued for craft over flash. Perfect for brands selling $45 notebooks that people genuinely treasure, apps about mindfulness or slow living, anything where "authentic" isn't just marketing speak but an actual design principle. This palette doesn't chase trends—it IS the trend that discerning people discover six months before it hits mainstream. Warm enough to feel welcoming, muted enough to feel exclusive. Chef's kiss.`
    }
    if (temp === 'cool' && sat === 'muted') {
      return `Welcome to the design philosophy of a Scandinavian architect who reads Dieter Rams manifestos for pleasure and owns exactly seven beautifully chosen objects. These ${count} colors have achieved something rare: they're simultaneously restrained AND captivating, minimal AND rich, quiet AND powerful. This is the palette equivalent of a $400 t-shirt that somehow justifies its price the moment you touch it—understated luxury, intelligent simplicity, quality that whispers because it doesn't need to shout. Perfect for products that respect their users' intelligence and attention, interfaces that make complexity feel effortless, brands that understand the difference between "simple" and "simplistic." Think Apple Store meets Japanese stationery meets high-end audio equipment meets that one perfect hotel room you still daydream about. Every color earned its place here through rigorous editing and taste.`
    }
    if (temp === 'balanced' && sat === 'vivid') {
      return `Someone spilled an entire color theory textbook into a kaleidoscope, spun it exactly three times, and miraculously landed on something that WORKS. ${count} colors dancing across the warm-cool spectrum with theatrical confidence, somehow managing to be energetic AND trustworthy, playful AND professional, bold AND approachable all at once. This palette has range—like a Swiss Army knife designed by a graphic designer with great taste. It can shift emotional gears on command: urgent call-to-action here, calming reassurance there, celebratory confetti moment in this corner, focused productivity mode over there. Perfect for platforms juggling multiple moods, products serving diverse audiences, or brands that refuse to be pigeonholed into a single vibe. Eclectic in the best way—like a really good playlist that flows seamlessly from genres you didn't think could coexist.`
    }
    if (temp === 'balanced' && sat === 'muted') {
      return `Picture a five-star hotel lobby at 3:47 AM: impeccably designed, perfectly quiet, bathed in lighting that costs more per fixture than most cars. Every surface whispers "quality" in seventeen different languages of restraint. That's your palette. ${count} colors that have mastered the ancient art of sophisticated understatement—nothing competes, nothing shouts, everything just... works with elegant inevitability. This is color as architecture: structural, intentional, timeless as hell. It's designed for products that want to be discovered rather than announced, for brands valuing longevity over viral moments, for interfaces where the content takes center stage and the design knows exactly when to get out of the way. Mature without feeling dated, restrained without feeling lifeless, expensive-looking without trying. The kind of palette that ages beautifully because it never chased trends in the first place.`
    }
    if (sat === 'muted' && count <= 4) {
      return `Less isn't just more here—it's EVERYTHING, and these ${count} colors know it in their bones. This is minimalism with backbone, restraint with intention, reduction as a power move rather than a limitation. Each color carries the weight of twenty precisely BECAUSE there aren't many, like a haiku poet choosing every syllable with surgical precision. This is the palette equivalent of a perfectly tailored suit where every detail matters because there's nowhere to hide mediocrity: no decoration necessary when the fundamentals are flawless. Works beautifully for tools that respect users' attention spans, products that value craft over decoration, brands that understand silence can be more powerful than noise. It's confident enough to let white space breathe, disciplined enough to kill its darlings, taste-forward enough to make maximalism look desperate by comparison.`
    }
    if (temp === 'warm' && count >= 10) {
      return `A warm, abundant palette that feels like walking into your favorite independent bookstore—the kind where the owner knows your name, remembers what you liked last time, and has already set aside three things you didn't know you needed. ${count} colors creating a rich tapestry of cozy possibilities, enough variety to stay endlessly interesting, enough warmth to make people want to stick around and explore. This is the color system of thoughtfully eclectic brands that curate rather than just collect, platforms that feel personal even at scale, products that celebrate abundance without descending into chaos. It's maximalism done right: intentional complexity, welcoming warmth, the kind of depth that rewards return visits. Users don't just interact with this system—they explore it, discover it, genuinely enjoy spending time inside it.`
    }
    if (temp === 'cool' && count >= 10) {
      return `${count} shades of composed professionalism—but make it interesting. Seriously. This palette is what happens when a tech company hires an art director who actually gives a damn about craft instead of just shipping MVPs. Cool-toned complexity that stays organized, systematic color choices that somehow still feel human-touched, comprehensive coverage that never tips into overwhelming chaos. Perfect for enterprise software that doesn't want to look like enterprise software, dashboards handling complexity with ballet-level grace, products where "professional" doesn't have to mean "soul-crushing monotony." It's the rare achievement of being both comprehensive AND coherent—like a well-designed spreadsheet that you don't hate looking at. Proof that you can serve serious business needs while still respecting aesthetics.`
    }

    // Fallback with personality
    return `Your ${count}-color palette tells a story written in ${temp} temperature and ${sat} saturation—a design language that ${count <= 5 ? 'believes in the power of ruthless editing' : 'embraces complexity with confident intentionality'}. It's the kind of color system that ${temp === 'balanced' ? 'adapts to any context like a design chameleon at the peak of its powers' : temp === 'warm' ? 'makes people feel something in their gut before their brain catches up' : 'projects calm competence in every single pixel'}. This is ${sat === 'vivid' ? 'absolutely not a palette for wallflowers or the timid' : sat === 'muted' ? 'color theory for people with genuinely exquisite taste' : 'the sweet spot between forgettable and overwhelming'}. In other words: someone made thoughtful choices here, and it shows.`
  }, [temp, sat, colors.length])
}

export function useArtMovementDescription(movement: ArtMovement): string {
  const descriptions: Record<ArtMovement, string> = {
    'Expressionism': 'Expressionism—bold, emotional, unapologetically dramatic. Colors with something to prove.',
    'Fauvism': 'Fauvism—wild colors liberated from reality, used with intuitive confidence.',
    'Minimalism': 'Minimalism—intentional reduction to essential elements. Less is literally more.',
    'Swiss Modernism': 'Swiss Modernism—clean, rational, universally legible. Grid-based precision.',
    'Brutalism': 'Brutalism—raw, honest, unapologetically bold. Beauty through function.',
    'Art Deco': 'Art Deco—geometric precision meets visual luxury and theatrical confidence.',
    'Contemporary': 'Contemporary Design—balanced, accessible, forward-thinking without alienating.',
    'Neo-Minimalism': 'Neo-Minimalism—less is more, but with contemporary flair and personality.',
    'Postmodernism': 'Postmodernism—playful, eclectic, breaking rules with thoughtful intention.',
    'Modern Design': 'Modern Design—thoughtful and intentional color strategy with timeless appeal.'
  }
  return descriptions[movement]
}

export function useTemperatureDescription(temp: TemperatureType): string {
  const descriptions: Record<TemperatureType, string> = {
    'warm': 'Warm colors dominate—they naturally draw attention, create immediacy, and make people lean in closer.',
    'cool': 'Cool colors define your system—they suggest calm, build trust, and create visual breathing room.',
    'balanced':
      'Your palette balances warm and cool with diplomatic precision. This versatility adapts to any context.'
  }
  return descriptions[temp]
}

export function useSaturationDescription(sat: SaturationType): string {
  const descriptions: Record<SaturationType, string> = {
    'vivid':
      'Vibrant, saturated colors create energy and visual impact. They demand attention and photograph beautifully.',
    'muted':
      'Muted, desaturated colors convey sophistication and restraint. They whisper when they could shout.',
    'balanced':
      'Balanced saturation creates visual harmony—neither too intense nor too subdued. Goldilocks-level balance.'
  }
  return descriptions[sat]
}

interface DesignInsight {
  title: string
  description: string
}

interface InsightParams {
  colorCount: number
  aliasCount: number
  spacingCount: number
  multiplesCount: number
  typographyCount: number
  temp: TemperatureType
  sat: SaturationType
}

export function useDesignSystemInsights(params: InsightParams): DesignInsight[] {
  const { colorCount, aliasCount, spacingCount, multiplesCount, typographyCount, temp, sat } = params

  return useMemo((): DesignInsight[] => {
    const insights: DesignInsight[] = []

    // Color insight
    if (colorCount > 0) {
      const colorInsight = (): string => {
        if (aliasCount > colorCount * 1.5) {
          return `${aliasCount} semantic aliases give these ${colorCount} colors multiple personalities—like actors playing different roles. Your "primary" color knows when to be a button, a link, or an accent. This is how you scale a palette without descending into chaos.`
        }
        if (aliasCount >= colorCount) {
          return `${aliasCount} color aliases provide semantic meaning on top of your ${colorCount} base colors. This abstraction layer means you can tweak the whole system by changing a few variables—proper design system wizardry.`
        }
        return `${colorCount} colors working with ${aliasCount} aliases. You've got room to add more semantic meaning here—consider mapping these colors to roles like "primary," "success," "warning" so they know their job.`
      }
      insights.push({ title: 'Color Architecture', description: colorInsight() })
    }

    // Spacing insight
    if (spacingCount > 0) {
      const spacingInsight = (): string => {
        if (multiplesCount > spacingCount * 2) {
          return `${multiplesCount} spacing multiples built from ${spacingCount} base tokens create a mathematical rhythm in your layouts. This is how you get that "everything just lines up" feeling without measuring every pixel manually. Pure spatial harmony through multiplication.`
        }
        if (multiplesCount >= spacingCount) {
          return `${spacingCount} spacing tokens generating ${multiplesCount} multiples. Your layout has a mathematical heartbeat—proportional relationships that create visual rhythm. This is why everything feels intentionally placed instead of randomly scattered.`
        }
        return `${spacingCount} spacing tokens with ${multiplesCount} multiples. Consider building more scale variants—2x, 3x, 4x multipliers create consistent breathing room and proportional hierarchy without arbitrary pixel values.`
      }
      insights.push({ title: 'Spatial Logic', description: spacingInsight() })
    }

    // Typography insight
    if (typographyCount > 0) {
      const typeInsight = (): string => {
        if (typographyCount >= 6) {
          return `${typographyCount} type scales give you nuanced hierarchy—from giant hero headlines to tiny footnotes, each with its own personality. This range means you're not forcing the same font size to do every job. Typography that works as hard as your content.`
        }
        if (typographyCount >= 4) {
          return `${typographyCount} typography scales create clear hierarchy from headlines to body text. You've got the fundamentals covered—enough variety to establish visual rhythm without overwhelming readers with options.`
        }
        return `${typographyCount} type scales cover the basics. Consider adding more granular sizes—you want enough variation that content naturally finds its hierarchy without designers having to force it.`
      }
      insights.push({ title: 'Typographic Scale', description: typeInsight() })
    }

    // System cohesion insight
    const cohesionInsight = (): string => {
      const hasAll = colorCount > 0 && spacingCount > 0 && typographyCount > 0
      const hasTwo = [colorCount > 0, spacingCount > 0, typographyCount > 0].filter(Boolean).length === 2

      if (hasAll) {
        if (temp === 'balanced' && sat === 'balanced') {
          return 'Every token in this system speaks the same design language—colors, spacing, and typography working together like a well-rehearsed jazz trio. Balanced, cohesive, versatile. This is the kind of system that makes design decisions feel effortless.'
        }
        if (sat === 'vivid') {
          return 'Your tokens work together as a unified whole—bold color choices supported by confident spacing and clear typography. This system has personality AND structure, like a charismatic leader who actually has their act together.'
        }
        return 'Colors, spacing, and typography forming a complete design language. Every token is interconnected, creating the kind of visual consistency that users might not consciously notice but definitely FEEL.'
      }
      if (hasTwo) {
        return "You've nailed two-thirds of the design system trinity. Add the missing piece—color, spacing, or typography—and you'll have a complete language for building interfaces that feel intentionally designed rather than haphazardly assembled."
      }
      return 'Design systems work best when color, spacing, and typography all speak the same language. Right now you have some pieces—consider building out the others for complete coverage and true systematic thinking.'
    }
    insights.push({ title: 'System Cohesion', description: cohesionInsight() })

    // Bonus whimsical insight based on specific conditions
    if (colorCount >= 10 && spacingCount >= 8 && typographyCount >= 5) {
      insights.push({
        title: 'The Overachiever Award',
        description:
          "This isn't just a design system—it's a comprehensive visual language with opinions about everything. You've built the kind of token set that handles edge cases gracefully, scales to new features without breaking a sweat, and makes other designers jealous. Well done."
      })
    } else if (colorCount <= 4 && spacingCount <= 4 && typographyCount <= 4) {
      insights.push({
        title: 'Minimalist Mastery',
        description:
          'Restraint this disciplined is actually harder than abundance. Every token here earned its place through ruthless editing. This is the design system equivalent of a perfectly packed carry-on bag—nothing unnecessary, nothing missing.'
      })
    } else if (temp === 'warm' && sat === 'vivid') {
      insights.push({
        title: 'Bold Energy',
        description:
          "Your system doesn't just support interfaces—it gives them PERSONALITY. These warm, vivid tokens create experiences people remember, screenshot, and tell their friends about. Not every brand can pull this off, but yours clearly can."
      })
    }

    return insights
  }, [colorCount, aliasCount, spacingCount, multiplesCount, typographyCount, temp, sat])
}
