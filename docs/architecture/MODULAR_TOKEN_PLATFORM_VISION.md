# Modular Token Platform: Universal Creative Language

**Document Version:** 1.0
**Date:** 2025-11-19
**Status:** Strategic Vision
**Related:** [strategic_vision_and_architecture.md](strategic_vision_and_architecture.md)

---

## 🎯 Core Vision

**Copy That is a modular token platform** where design tokens serve as a **universal creative language** bridging ANY input modality to ANY output system.

**Key Principle:** Loose coupling through tokens as an intermediate representation (IR).

---

## 🏗️ Architecture Philosophy

### The Token as Universal Language

Similar to how:
- **LLVM IR** enables multiple languages → IR → multiple platforms
- **MIDI** enables any instrument → standard representation → any synthesizer
- **OpenAI Jukebox** enables image → latent space → music

**Copy That uses tokens as the universal creative IR:**

```
┌────────────────────────────────────────────────────────────┐
│                   INPUT ADAPTERS (Modular)                  │
│                  Any Modality → Tokens                      │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Image      │  │    Video     │  │    Audio     │    │
│  │  Analysis    │  │   Analysis   │  │   Analysis   │    │
│  │  (Phase 1)   │  │   (Future)   │  │   (Future)   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│         ↓                 ↓                 ↓              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │    Text      │  │  Multimodal  │  │   Custom     │    │
│  │  Analysis    │  │   Fusion     │  │   Adapter    │    │
│  │  (Future)    │  │   (Future)   │  │ (Extensible) │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
└────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────┐
│                   TOKEN PLATFORM (Core)                     │
│              Universal Token Representation                 │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  • W3C Design Tokens (Standard Base)                       │
│  • Token Graph (Relationships & Dependencies)              │
│  • Multi-Modal Extensions ($extensions)                    │
│  • Cross-Modal Mappings (Image → Audio, etc.)             │
│  • Ontology Registry (Taxonomies for all modalities)      │
│  • Validation & Type Safety (Pydantic schemas)            │
│                                                             │
└────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────┐
│                OUTPUT GENERATORS (Modular)                  │
│                 Tokens → Any Output                         │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Generative  │  │    Audio     │  │   Desktop    │    │
│  │     UI       │  │   Plugins    │  │    Apps      │    │
│  │ (Web/Mobile) │  │  (JUCE/VST)  │  │ (Electron/Qt)│    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│         ↓                 ↓                 ↓              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ MIDI/Music   │  │    Video     │  │   Custom     │    │
│  │ Generation   │  │   Effects    │  │  Generator   │    │
│  │  (Creative)  │  │(After Effects)│ │ (Extensible) │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

---

## 🎨 Multi-Modal Token System

### Token Categories (Expandable)

#### Phase 1: Visual Design Tokens (Current)
- **Color** - Palette, scales, semantic roles
- **Typography** - Font families, scales, weights
- **Spacing** - Grid systems, padding, margins
- **Layout** - Component positioning, breakpoints
- **Shadow** - Depth, elevation, blur
- **Border** - Radius, stroke, style
- **Opacity** - Transparency levels
- **Animation** - Transitions, durations, easing

#### Phase 2: Temporal Tokens (Video/Animation)
- **Motion** - Velocity, acceleration, trajectories
- **Transition** - Cut patterns, dissolves, wipes
- **Timing** - BPM, rhythm, sync points
- **Keyframe** - Position, scale, rotation over time
- **Camera** - Movement, focus, field of view
- **Scene** - Shot composition, framing

#### Phase 3: Audio Tokens (Sound Design)
- **Pitch** - Frequency ranges, harmonics
- **Rhythm** - Tempo, time signatures, patterns
- **Timbre** - Instrument characteristics, ADSR envelopes
- **Dynamics** - Volume curves, compression, limiting
- **Spatial** - Panning, reverb, room acoustics
- **Harmony** - Chord progressions, scales, modes

#### Phase 4: Semantic Tokens (Text/NLP)
- **Tone** - Formal, casual, technical, emotional
- **Voice** - Brand voice, personality, style
- **Structure** - Headings, hierarchy, flow
- **Lexicon** - Vocabulary, terminology, jargon
- **Sentiment** - Positive, neutral, negative
- **Intent** - Purpose, call-to-action, information

#### Phase 5: Cross-Modal Tokens (Synesthesia)
- **Mood** - Emotional mapping across modalities
- **Energy** - Intensity mapping (color saturation ↔ audio volume)
- **Rhythm** - Visual rhythm ↔ Audio tempo
- **Harmony** - Color harmony ↔ Musical harmony
- **Texture** - Visual texture ↔ Sonic texture

---

## 🔌 Input Adapter Architecture

### Adapter Interface (Extensible)

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class InputAdapter(ABC):
    """Base class for all input adapters (Image, Video, Audio, Text)"""

    @property
    @abstractmethod
    def modality(self) -> str:
        """Input modality: image, video, audio, text, multimodal"""
        pass

    @property
    @abstractmethod
    def supported_token_types(self) -> List[str]:
        """Token types this adapter can extract"""
        pass

    @abstractmethod
    async def extract_tokens(
        self,
        input_data: Any,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract tokens from input data.

        Args:
            input_data: Input (file, URL, buffer, etc.)
            options: Extraction configuration

        Returns:
            Dict mapping token_type → List[token_dict]

        Example:
            {
                "color": [{"hex": "#FF5733", "confidence": 0.95}, ...],
                "spacing": [{"value": "16px", "semantic": "medium"}, ...],
                "rhythm": [{"bpm": 120, "time_signature": "4/4"}, ...]
            }
        """
        pass

    @abstractmethod
    def validate_input(self, input_data: Any) -> bool:
        """Validate input data format"""
        pass

    async def preprocess(self, input_data: Any) -> Any:
        """Optional preprocessing step"""
        return input_data

    async def postprocess(self, tokens: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """Optional postprocessing step"""
        return tokens
```

---

### Example: Image Adapter (Current)

```python
class ImageInputAdapter(InputAdapter):
    """Extract design tokens from images"""

    modality = "image"
    supported_token_types = [
        "color", "spacing", "typography", "shadow",
        "border", "opacity", "layout", "component"
    ]

    async def extract_tokens(
        self,
        image_file: UploadFile,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        # Use existing extractors (AI + CV)
        color_extractor = AIColorExtractor()
        spacing_extractor = SpacingExtractor()
        # ... etc

        return {
            "color": await color_extractor.extract(image_file),
            "spacing": await spacing_extractor.extract(image_file),
            # ... etc
        }
```

---

### Example: Audio Adapter (Future)

```python
class AudioInputAdapter(InputAdapter):
    """Extract audio tokens from audio files"""

    modality = "audio"
    supported_token_types = [
        "pitch", "rhythm", "timbre", "dynamics",
        "spatial", "harmony", "tempo", "key"
    ]

    async def extract_tokens(
        self,
        audio_file: UploadFile,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        # Use audio analysis libraries (librosa, essentia, etc.)
        return {
            "pitch": await self._extract_pitch(audio_file),
            "rhythm": await self._extract_rhythm(audio_file),
            "timbre": await self._extract_timbre(audio_file),
            # ... etc
        }

    async def _extract_pitch(self, audio_file) -> List[Dict]:
        """Extract pitch information using librosa"""
        import librosa
        y, sr = librosa.load(audio_file)
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        # Convert to token format
        return [
            {
                "frequency": float(freq),
                "note": librosa.hz_to_note(freq),
                "magnitude": float(mag),
                "timestamp": t
            }
            for t, freq, mag in self._extract_dominant_pitches(pitches, magnitudes)
        ]
```

---

### Example: Video Adapter (Future)

```python
class VideoInputAdapter(InputAdapter):
    """Extract temporal + visual tokens from video"""

    modality = "video"
    supported_token_types = [
        "color", "motion", "transition", "timing",
        "keyframe", "camera", "scene", "audio"
    ]

    async def extract_tokens(
        self,
        video_file: UploadFile,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        # Extract visual tokens from frames
        frames = await self._extract_frames(video_file)
        visual_tokens = await self._analyze_frames(frames)

        # Extract motion/temporal tokens
        motion_tokens = await self._analyze_motion(video_file)

        # Extract audio tokens if present
        audio_tokens = await self._extract_audio_track(video_file)

        return {
            **visual_tokens,
            **motion_tokens,
            **audio_tokens
        }
```

---

## 🎯 Token Platform Core

### W3C Design Tokens + Multi-Modal Extensions

**Base W3C Format:**
```json
{
  "color": {
    "primary": {
      "$type": "color",
      "$value": "#0066CC",
      "$description": "Primary brand color"
    }
  }
}
```

**Multi-Modal Extension:**
```json
{
  "color": {
    "primary": {
      "$type": "color",
      "$value": "#0066CC",
      "$description": "Primary brand color",
      "$extensions": {
        "copy-this": {
          "source_modality": "image",
          "confidence": 0.95,
          "semantic_name": "vibrant-blue",
          "cross_modal": {
            "audio_mapping": {
              "pitch": 440,
              "note": "A4",
              "timbre": "bright"
            },
            "emotion": "confident",
            "energy": 0.85
          }
        }
      }
    }
  },
  "rhythm": {
    "base": {
      "$type": "rhythm",
      "$value": {
        "bpm": 120,
        "time_signature": "4/4"
      },
      "$description": "Base rhythm derived from visual tempo",
      "$extensions": {
        "copy-this": {
          "source_modality": "image",
          "derived_from": "color.primary.saturation",
          "cross_modal": {
            "visual_mapping": {
              "animation_duration": "500ms",
              "easing": "cubic-bezier(0.4, 0, 0.2, 1)"
            }
          }
        }
      }
    }
  }
}
```

---

### Token Graph with Cross-Modal Relationships

```python
from typing import Dict, List, Any, Optional
import networkx as nx

class MultiModalTokenGraph:
    """Manage tokens from multiple modalities with cross-modal relationships"""

    def __init__(self):
        self.graph = nx.MultiDiGraph()  # Multi-edge for different relationship types

    def add_token(
        self,
        path: str,
        token: Dict[str, Any],
        modality: str
    ):
        """Add token with modality metadata"""
        self.graph.add_node(
            path,
            token=token,
            modality=modality
        )

    def add_cross_modal_link(
        self,
        source_path: str,
        target_path: str,
        relationship_type: str,
        mapping: Optional[Dict[str, Any]] = None
    ):
        """
        Link tokens across modalities.

        Examples:
            - color.primary → pitch.A4 (synesthesia)
            - spacing.rhythm → tempo.120bpm (visual rhythm)
            - motion.velocity → dynamics.crescendo (energy)
        """
        self.graph.add_edge(
            source_path,
            target_path,
            type=relationship_type,
            mapping=mapping
        )

    def get_cross_modal_mappings(
        self,
        token_path: str
    ) -> Dict[str, List[str]]:
        """Get all cross-modal mappings for a token"""
        mappings = {}
        for _, target, data in self.graph.out_edges(token_path, data=True):
            rel_type = data.get('type')
            if rel_type not in mappings:
                mappings[rel_type] = []
            mappings[rel_type].append(target)
        return mappings

    def query_by_modality(self, modality: str) -> List[str]:
        """Get all tokens from a specific modality"""
        return [
            path for path, data in self.graph.nodes(data=True)
            if data.get('modality') == modality
        ]

    def find_synesthetic_pairs(self) -> List[tuple]:
        """Find color ↔ audio mappings"""
        pairs = []
        for edge in self.graph.edges(data=True):
            if edge[2].get('type') == 'synesthesia':
                pairs.append((edge[0], edge[1], edge[2].get('mapping')))
        return pairs
```

---

## 🚀 Output Generator Architecture

### Generator Interface (Extensible)

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class OutputGenerator(ABC):
    """Base class for all output generators"""

    @property
    @abstractmethod
    def output_type(self) -> str:
        """Output type: ui, audio_plugin, desktop_app, midi, video, custom"""
        pass

    @property
    @abstractmethod
    def supported_token_types(self) -> List[str]:
        """Token types this generator can consume"""
        pass

    @abstractmethod
    async def generate(
        self,
        tokens: Dict[str, List[Dict[str, Any]]],
        options: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Generate output from tokens.

        Args:
            tokens: Token dictionary from platform
            options: Generation configuration

        Returns:
            Generated output (code, files, data, etc.)
        """
        pass

    @abstractmethod
    def validate_tokens(self, tokens: Dict[str, List[Dict]]) -> bool:
        """Validate tokens before generation"""
        pass

    async def preprocess_tokens(self, tokens: Dict) -> Dict:
        """Optional token preprocessing"""
        return tokens

    async def postprocess_output(self, output: Any) -> Any:
        """Optional output postprocessing"""
        return output
```

---

### Example: Generative UI Generator (Current)

```python
class GenerativeUIGenerator(OutputGenerator):
    """Generate UI components from visual tokens"""

    output_type = "ui"
    supported_token_types = [
        "color", "typography", "spacing", "layout",
        "shadow", "border", "opacity", "component"
    ]

    async def generate(
        self,
        tokens: Dict[str, List[Dict[str, Any]]],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """Generate React/Flutter/SwiftUI components"""

        platform = options.get("platform", "react")

        if platform == "react":
            return await self._generate_react(tokens, options)
        elif platform == "flutter":
            return await self._generate_flutter(tokens, options)
        # ... etc

    async def _generate_react(self, tokens, options) -> Dict[str, str]:
        """Generate React component code"""
        return {
            "Button.tsx": self._generate_button_component(tokens),
            "Button.css": self._generate_button_styles(tokens),
            "tokens.css": self._generate_css_variables(tokens),
        }
```

---

### Example: Audio Plugin Generator (JUCE)

```python
class AudioPluginGenerator(OutputGenerator):
    """Generate audio plugin code from audio + visual tokens"""

    output_type = "audio_plugin"
    supported_token_types = [
        "color", "spacing", "pitch", "rhythm", "timbre", "dynamics"
    ]

    async def generate(
        self,
        tokens: Dict[str, List[Dict[str, Any]]],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """Generate JUCE C++ audio plugin"""

        return {
            # UI from visual tokens
            "PluginEditor.h": self._generate_editor_header(tokens["color"], tokens["spacing"]),
            "PluginEditor.cpp": self._generate_editor_impl(tokens),

            # Audio processing from audio tokens
            "PluginProcessor.h": self._generate_processor_header(tokens["pitch"], tokens["timbre"]),
            "PluginProcessor.cpp": self._generate_processor_impl(tokens),

            # Parameters from cross-modal mappings
            "Parameters.h": self._generate_parameters(tokens),
        }

    def _generate_editor_impl(self, tokens) -> str:
        """Generate JUCE editor with colors from tokens"""
        colors = tokens.get("color", [])
        primary_color = colors[0] if colors else {"hex": "#0066CC"}

        return f'''
        void PluginEditor::paint(juce::Graphics& g)
        {{
            // Background from extracted color tokens
            g.fillAll(juce::Colour::fromString("{primary_color['hex']}"));

            // ... more UI code
        }}
        '''
```

---

### Example: MIDI Generator (Creative Cross-Modal)

```python
class MIDIGenerator(OutputGenerator):
    """Generate MIDI/music from image tokens (synesthesia)"""

    output_type = "midi"
    supported_token_types = [
        "color",  # Color → Pitch/Timbre
        "spacing",  # Spacing → Rhythm
        "motion",  # Motion → Dynamics
    ]

    async def generate(
        self,
        tokens: Dict[str, List[Dict[str, Any]]],
        options: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """Generate MIDI file from visual tokens"""

        # Map colors to pitches using synesthesia
        colors = tokens.get("color", [])
        pitches = [self._color_to_pitch(c) for c in colors]

        # Map spacing to rhythm
        spacing = tokens.get("spacing", [])
        rhythm = self._spacing_to_rhythm(spacing)

        # Map motion to dynamics
        motion = tokens.get("motion", [])
        dynamics = self._motion_to_dynamics(motion)

        # Generate MIDI
        return await self._create_midi_file(pitches, rhythm, dynamics)

    def _color_to_pitch(self, color: Dict) -> int:
        """
        Map color to MIDI pitch using synesthetic mapping.

        Hue → Pitch:
        - Red (0°) → C (60)
        - Orange (30°) → D (62)
        - Yellow (60°) → E (64)
        - Green (120°) → G (67)
        - Blue (240°) → C (72)
        - Purple (270°) → D (74)

        Saturation → Octave:
        - High saturation → Higher octave
        - Low saturation → Lower octave

        Lightness → Velocity:
        - Bright → Loud (velocity 100+)
        - Dark → Soft (velocity 40-)
        """
        from colorsys import rgb_to_hsv

        # Parse hex color
        hex_color = color["hex"].lstrip("#")
        r, g, b = tuple(int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4))
        h, s, v = rgb_to_hsv(r, g, b)

        # Hue → Base pitch (C major scale)
        c_major_scale = [0, 2, 4, 5, 7, 9, 11]  # MIDI intervals
        hue_index = int(h * len(c_major_scale))
        base_pitch = 60 + c_major_scale[hue_index]  # Middle C + interval

        # Saturation → Octave adjustment
        octave_shift = int(s * 2) * 12  # 0-2 octaves up

        # Final MIDI note
        midi_note = base_pitch + octave_shift

        return midi_note
```

---

## 🔄 Cross-Modal Creativity Examples

### 1. Image → MIDI Song Generation

**Input:** Design system image (colors, spacing, layout)

**Process:**
1. Extract color tokens (primary, secondary, accent, etc.)
2. Map colors to pitches using synesthesia
3. Extract spacing rhythm (regular vs. irregular)
4. Map spacing to musical rhythm (quarter notes, eighth notes, etc.)
5. Detect visual harmony (complementary, analogous, etc.)
6. Map to musical harmony (chord progressions)
7. Generate MIDI file

**Output:** MIDI file that "sounds like" the visual design

**Use Case:** Brand sonification, audio branding, creative tools

---

### 2. Audio → UI Generation

**Input:** Music track or audio sample

**Process:**
1. Extract pitch/harmony tokens
2. Map dominant frequencies to color palette (inverse synesthesia)
3. Extract rhythm/tempo tokens
4. Map to animation timing and transitions
5. Extract dynamics (loud/soft patterns)
6. Map to visual hierarchy (prominent vs. subtle)
7. Generate UI components

**Output:** UI theme that "looks like" the music

**Use Case:** Music player interfaces, audio branding, creative tools

---

### 3. Video → Interactive Animation

**Input:** Video clip

**Process:**
1. Extract motion tokens (velocity, acceleration, trajectories)
2. Map to UI animation parameters (duration, easing, transform)
3. Extract scene transitions (cuts, dissolves, etc.)
4. Map to page transitions and navigation
5. Extract camera movement
6. Map to parallax scrolling and viewport effects
7. Generate interactive animation code

**Output:** Web/mobile animations matching video motion

**Use Case:** Motion design systems, animation libraries, creative tools

---

### 4. Text → Mood-Based Design System

**Input:** Brand copy, marketing text, documentation

**Process:**
1. Extract sentiment tokens (positive, neutral, negative)
2. Map to color temperature (warm, cool, neutral)
3. Extract tone tokens (formal, casual, technical)
4. Map to typography style (serif, sans-serif, monospace)
5. Extract energy level
6. Map to spacing density (tight, standard, loose)
7. Generate design system

**Output:** Design system matching text tone/mood

**Use Case:** Content-driven design, marketing automation, personalization

---

## 🛠️ Implementation Strategy

### Phase 1: Foundation (Current - Week 6)
**Focus:** Image input → Visual tokens → UI output

- ✅ Image input adapter (working)
- ✅ Visual token extraction (color, spacing, typography)
- ✅ React/Flutter UI generators (working)
- 🔄 W3C token schema with extensions

**Goal:** Solidify current image → UI pipeline

---

### Phase 2: Modular Refactor (Weeks 7-10)
**Focus:** Loose coupling and plugin architecture

**Tasks:**
1. **Extract Input Adapter Interface** (Week 7)
   - Create `InputAdapter` base class
   - Refactor existing image extraction to `ImageInputAdapter`
   - Add adapter registry with runtime discovery

2. **Token Platform Core** (Week 8)
   - Implement `MultiModalTokenGraph`
   - Add W3C schema with multi-modal extensions
   - Create token validation/transformation layer

3. **Extract Output Generator Interface** (Week 9)
   - Create `OutputGenerator` base class
   - Refactor existing generators to plugin system
   - Add generator registry with runtime discovery

4. **Testing & Documentation** (Week 10)
   - Unit tests for each adapter/generator
   - Integration tests for end-to-end flows
   - API documentation and examples

**Outcome:** Modular, extensible architecture ready for new modalities

---

### Phase 3: Audio Modality (Weeks 11-16)
**Focus:** Add audio input and audio plugin output

**Input Side:**
1. **Audio Input Adapter** (Weeks 11-12)
   - Use librosa/essentia for audio analysis
   - Extract pitch, rhythm, timbre, dynamics tokens
   - Validate with music samples

2. **Cross-Modal Mapping: Audio ↔ Visual** (Week 13)
   - Implement synesthetic mappings (pitch ↔ color)
   - Add to MultiModalTokenGraph
   - Create mapping visualization in frontend

**Output Side:**
3. **Audio Plugin Generator (JUCE)** (Weeks 14-15)
   - Generate JUCE C++ code
   - UI from visual tokens
   - Audio processing from audio tokens
   - Test with real plugin build

4. **MIDI Generator** (Week 16)
   - Image → MIDI synesthetic mapping
   - Audio → MIDI transcription
   - Test with DAW integration

**Outcome:** Image → Audio plugin, Image → MIDI, Audio → UI

---

### Phase 4: Video Modality (Weeks 17-22)
**Focus:** Add video input and animation output

**Input Side:**
1. **Video Input Adapter** (Weeks 17-18)
   - Frame extraction and analysis
   - Motion detection and tracking
   - Scene segmentation
   - Camera movement analysis

2. **Temporal Token Extraction** (Week 19)
   - Motion, timing, keyframe tokens
   - Transition pattern detection
   - Tempo/rhythm from video

**Output Side:**
3. **Animation Generator** (Weeks 20-21)
   - CSS/JS animation generation
   - Lottie/After Effects export
   - Motion design system generation

4. **Video Effects Generator** (Week 22)
   - After Effects scripts
   - DaVinci Resolve plugins
   - LUT generation from color tokens

**Outcome:** Video → Animation code, Video → After Effects project

---

### Phase 5: Semantic Modality (Weeks 23-26)
**Focus:** Add text/NLP input

**Input Side:**
1. **Text Input Adapter** (Weeks 23-24)
   - Sentiment analysis
   - Tone detection
   - Brand voice extraction
   - Content structure analysis

2. **Semantic Token Extraction** (Week 25)
   - Tone, voice, structure, lexicon tokens
   - Emotional mapping to design tokens

**Output Side:**
3. **Content-Driven Design Generator** (Week 26)
   - Design systems from brand copy
   - Mood-based theme generation
   - Personalized UI from user content

**Outcome:** Text → Design system, Mood → UI theme

---

### Phase 6: Multimodal Fusion (Weeks 27-30)
**Focus:** Combine multiple inputs for richer tokens

**Tasks:**
1. **Multimodal Input Adapter** (Week 27-28)
   - Combine image + audio + text
   - Cross-modal validation and fusion
   - Conflict resolution strategies

2. **Advanced Cross-Modal Creativity** (Week 29)
   - Complex mappings (video motion → MIDI + UI animations)
   - Multi-output generation
   - Creative exploration tools

3. **Platform Polish** (Week 30)
   - Performance optimization
   - Production hardening
   - User documentation

**Outcome:** Full multimodal creative platform

---

## 🎯 Modular Architecture Benefits

### 1. Loose Coupling
- Input adapters don't know about output generators
- Tokens are the universal contract
- Add new modalities without changing core platform

### 2. Independent Development
- Image team can work on image extractors
- Audio team can work on audio generators
- No coordination needed across teams

### 3. Mix-and-Match Creativity
- Any input → Any output
- Image → UI (core use case)
- Image → MIDI (creative exploration)
- Audio → UI (audio branding)
- Video → Animation code (motion design)
- Text → Design system (content-driven design)

### 4. Future-Proof
- New input modalities: 3D models, AR/VR, sensor data
- New output formats: Unreal Engine, Unity, Blender
- New creative applications: NFT generation, procedural content

### 5. Commercial Flexibility
- Sell different modules independently
- Image analysis as SaaS
- Audio plugin generator as desktop tool
- MIDI generator as creative tool
- Full platform for enterprises

---

## 📊 Architecture Principles

### 1. Single Responsibility
- **Input Adapters:** Extract tokens, nothing else
- **Token Platform:** Manage relationships, nothing else
- **Output Generators:** Generate output, nothing else

### 2. Open/Closed Principle
- **Open for extension:** New adapters/generators plug in
- **Closed for modification:** Core platform stays stable

### 3. Dependency Inversion
- **High-level:** Token platform doesn't depend on specifics
- **Low-level:** Adapters/generators depend on token interface

### 4. Interface Segregation
- **Specific interfaces:** Image adapter ≠ Audio adapter
- **No bloat:** Generators only implement what they need

### 5. Liskov Substitution
- **Swappable:** Any ImageInputAdapter works the same
- **Polymorphic:** Runtime adapter/generator selection

---

## 🚀 Technology Stack (Updated)

### Input Adapters
- **Image:** OpenCV, SAM, YOLO, Claude Vision
- **Audio:** librosa, essentia, aubio, madmom
- **Video:** OpenCV, PyAV, moviepy, FFmpeg
- **Text:** spaCy, NLTK, transformers, Claude NLP

### Token Platform (Core)
- **Backend:** FastAPI + Python 3.12+
- **Graph:** NetworkX (multi-modal relationships)
- **Schema:** W3C Design Tokens + Pydantic v2
- **Database:** PostgreSQL + Redis (caching)
- **Validation:** JSON Schema + Zod (frontend)

### Output Generators
- **UI:** React, Flutter, SwiftUI, Angular, Vue
- **Audio:** JUCE (C++), VST SDK, AudioKit
- **MIDI:** mido, pretty_midi, music21
- **Animation:** Lottie, CSS animations, GSAP
- **Video:** After Effects scripting, FFmpeg
- **Desktop:** Electron, Qt, Tauri

### Frontend (Dev UI)
- **Framework:** React 18 + Vite + TypeScript
- **Visualization:** D3.js, Cytoscape, Tone.js (audio)
- **State:** Zustand + React Query

---

## 🎨 Example Use Cases

### Use Case 1: Audio Plugin with Brand Colors
**Scenario:** Audio company wants plugin UI matching their brand

**Flow:**
1. Upload brand image (logo, marketing material)
2. Extract color tokens (ImageInputAdapter)
3. Generate JUCE C++ code (AudioPluginGenerator)
4. Compile VST/AU plugin
5. Ship with branded UI

**Benefit:** No manual UI coding needed

---

### Use Case 2: Brand Sonification
**Scenario:** Company wants audio branding from visual identity

**Flow:**
1. Upload brand guidelines (colors, typography, spacing)
2. Extract visual tokens (ImageInputAdapter)
3. Generate MIDI using synesthetic mapping (MIDIGenerator)
4. Compose music based on brand "sound"
5. Use for audio branding, product sounds, notifications

**Benefit:** Consistent multi-modal brand identity

---

### Use Case 3: Motion Design System
**Scenario:** Design team wants animations matching video mood

**Flow:**
1. Upload brand video (product demo, commercial)
2. Extract motion tokens (VideoInputAdapter)
3. Generate animation library (AnimationGenerator)
4. Export CSS animations, Lottie files
5. Use across web/mobile products

**Benefit:** Consistent motion language

---

### Use Case 4: Content-Driven Personalization
**Scenario:** App wants UI adapting to user content mood

**Flow:**
1. Analyze user-written text (journal entry, review, post)
2. Extract sentiment/tone tokens (TextInputAdapter)
3. Generate mood-based theme (GenerativeUIGenerator)
4. Apply personalized UI
5. User sees design matching their emotional state

**Benefit:** Emotional personalization at scale

---

## ✅ Checklist: Modular Architecture Migration

### Phase 2: Weeks 7-10 (Modular Refactor)

**Week 7: Input Adapter Interface**
- [ ] Create `InputAdapter` abstract base class
- [ ] Define adapter interface (modality, supported_tokens, extract, validate)
- [ ] Refactor existing image extraction to `ImageInputAdapter`
- [ ] Create adapter registry with runtime discovery
- [ ] Add adapter plugin loading from config
- [ ] Write adapter unit tests
- [ ] Document adapter interface and examples

**Week 8: Token Platform Core**
- [ ] Implement `MultiModalTokenGraph` with NetworkX
- [ ] Add W3C schema with multi-modal `$extensions`
- [ ] Create token validation layer
- [ ] Add cross-modal relationship types
- [ ] Implement token resolution with dependency tracking
- [ ] Add token query API (by modality, by type, relationships)
- [ ] Write token platform unit tests
- [ ] Document token schema and API

**Week 9: Output Generator Interface**
- [ ] Create `OutputGenerator` abstract base class
- [ ] Define generator interface (output_type, supported_tokens, generate, validate)
- [ ] Refactor existing React generator to plugin
- [ ] Refactor existing Flutter generator to plugin
- [ ] Create generator registry with runtime discovery
- [ ] Add generator plugin loading from config
- [ ] Write generator unit tests
- [ ] Document generator interface and examples

**Week 10: Testing & Documentation**
- [ ] Integration tests for adapter → platform → generator
- [ ] End-to-end tests for image → UI flow
- [ ] Performance benchmarks (latency, throughput)
- [ ] API documentation (OpenAPI/Swagger)
- [ ] Architecture diagrams (mermaid)
- [ ] Developer guide (how to add adapters/generators)
- [ ] Example plugins for reference

---

## 📚 Related Documentation

### Architecture
- [strategic_vision_and_architecture.md](strategic_vision_and_architecture.md) - Platform vision
- [existing_capabilities_inventory.md](existing_capabilities_inventory.md) - Current capabilities

### Planning
- [workflows/color_integration_roadmap.md](../planning/workflows/color_integration_roadmap.md) - Phase 4 Day 5 integration
- [ops/implementation_strategy.md](../planning/ops/implementation_strategy.md) - Phase 4 roadmap

---

**Document Purpose:** Define modular, extensible architecture enabling multi-modal token platform for creative applications across image, video, audio, and text.

**Key Principle:** Loose coupling through tokens as universal creative IR.

**Next Steps:**
1. **TODAY:** Complete Phase 4 Day 5 (image → UI solidification)
2. **Weeks 7-10:** Modular refactor (adapter/generator plugin system)
3. **Weeks 11+:** Add audio, video, text modalities incrementally
