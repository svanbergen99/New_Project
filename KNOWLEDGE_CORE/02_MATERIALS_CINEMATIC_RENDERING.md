# Materials + Cinematic Rendering — Standalone Knowledge

Snapshot: 2026-09.

Bronprincipes: MaterialX voor renderer-onafhankelijke look-development en Filament voor een compacte, praktisch bewezen PBR/realtime renderingarchitectuur.

## Materiaalmodel

Gebruik een renderer-onafhankelijk material description als waarheid.

Canonical material:

```text
id
name
shading_model
base_color
metallic
roughness
normal
ambient_occlusion
emissive
opacity
ior
clearcoat
clearcoat_roughness
sheen
anisotropy
subsurface
transmission
textures[]
custom_graph optional
```

## PBR basis

Voor standaard oppervlakken:

```text
final lighting = diffuse response + specular response
```

Belangrijkste artistieke controls:
- base color
- metallic
- roughness
- normal
- ambient occlusion
- emissive

Principes:
- metallic is doorgaans conceptueel 0 of 1; tussenwaarden vooral voor blends/lagen.
- roughness bestuurt highlight/reflection spread.
- non-metals hebben een dielectric specular response; metals gebruiken gekleurde specular en vrijwel geen diffuse component.
- alle lightingberekeningen in lineaire kleur; display transform/tone mapping pas later.

## MaterialX mental model

MaterialX beschrijft look als graph van typed nodes.

```text
inputs/textures
      ↓
math/pattern nodes
      ↓
BSDF/surface nodes
      ↓
material output
```

Belangrijke concepten:

```text
Document
NodeDef
Node
NodeGraph
Input
Output
Material
Implementation
Target / ShaderGenerator
```

Een graph moet engine-onafhankelijk blijven. Shader generation vertaalt dezelfde graph naar een target/shading language. De gegenereerde shader source moet vervolgens door de target compiler worden gecompileerd.

## Material adapter pipeline

```text
Canonical Material / MaterialX
         ↓
validate graph + textures + color spaces
         ↓
resolve target capabilities
         ↓
map nodes / generate target representation
         ↓
compile target shader/material
         ↓
create engine material instance
         ↓
bind to entity
```

Wanneer target een node niet ondersteunt:
1. exact mapping;
2. mathematische equivalent;
3. baked texture;
4. safe visual approximation;
5. capability error als de look essentieel is.

## Texture contract

Per texture:

```text
uri
semantic: baseColor|normal|roughness|metallic|ao|emissive|mask|height|custom
color_space: srgb|linear|data
uv_set
wrap_u/v
filter
scale/offset/rotation
channel mapping
```

Regels:
- normal/roughness/metallic/AO/masks zijn data, niet sRGB kleur.
- baseColor/emissive zijn doorgaans kleurdata en vereisen correcte transfer/color-management.
- normal-map conventie (Y+/Y-) expliciet vastleggen per adapter.

## Material layering

Voor cinematic richness ondersteunen we conceptueel lagen:

```text
base diffuse/specular
secondary specular
sheen
clearcoat
surface dirt/wetness
micro-normal
```

Gebruik geen onbegrensde shadercomplexiteit. Bepaal per renderprofiel budget.

## Fysieke camera

Canonical camera exposure model:

```text
focal length
sensor/aperture dimensions
f-stop
shutter time/angle
ISO/sensitivity
focus distance
near/far clip
```

Cinematic look komt niet alleen van post-processing. Camera framing, lenskeuze en focus zijn primaire ontwerpvariabelen.

Lensgedrag in presets:

```text
wide 18–28 mm: ruimtelijkheid, snelheid, sterke perspectiefwerking
normal 35–55 mm: natuurlijke nabijheid
portrait 70–105 mm: compressie, isolatie, karakterfocus
tele >105 mm: afstand/compressie/grafische lagen
```

Dit zijn artistieke richtlijnen; sensor size beïnvloedt daadwerkelijke field of view.

## Fysieke verlichting

Waar engine het ondersteunt gebruiken we fysieke units en consistente schaal.

Canonical light properties:

```text
type
intensity
exposure compensation optional
color or temperature
size/shape
position/orientation
cone parameters
IES profile optional
shadow quality
volumetric contribution
```

Cinematic licht wordt ontworpen in functies:
- key: primaire modellering/attention
- fill: contrast controleren
- rim/back: silhouet en separation
- practicals: zichtbare gemotiveerde bronnen
- environment: wereldkleur/reflection baseline

## Image Based Lighting

Voor geloofwaardige realtime materialen is environment lighting belangrijk:

```text
HDR environment
→ diffuse irradiance
→ specular prefiltered reflections
→ BRDF integration
```

Gebruik environment niet als vervanging voor doelgerichte key lighting.

## Tone mapping en color

Render intern HDR/linear. Daarna:

```text
scene linear
→ exposure
→ bloom/optical effects
→ tone map
→ color grade / display transform
→ output color space
```

Vermijd effecten in verkeerde kleurspace.

## Stylized / Cinematic Immersion

Doel: emotionele, grafisch bewuste wereld die niet fotorealistisch hoeft te zijn maar wel ruimtelijk en filmisch voelt.

Style knobs:

```text
shape language
silhouette clarity
controlled palette
value grouping
selective texture detail
exaggerated proportions
purposeful light falloff
atmosphere/fog depth
camera movement with intent
animation timing/anticipation
selective depth of field
controlled bloom
color-script per scene
```

Regel: stylization moet consistent zijn over geometry, material, lighting, animation en post. Alleen een toonshader bovenop realistische assets is meestal onvoldoende.

## Stylized / Cinematic Realism

Doel: fysiek geloofwaardige basis met bewust gestileerde art direction.

```text
real scale + plausible materials + plausible light transport
                     ↓
controlled exaggeration
- cleaner silhouettes
- curated roughness
- selective saturation
- intentional fog
- controlled lensing
- designed contrast
```

Dit geeft een geloofwaardige wereld zonder documentaire neutraliteit.

## Twee style profielen

### Profile A — Cinematic Immersion

```text
PBR fidelity: medium/high
shape exaggeration: high
palette discipline: high
surface noise: low/medium
lighting realism: medium
lighting drama: high
DOF: selective
fog/atmosphere: medium/high
camera motion: authored
post grade: strong but controlled
```

### Profile B — Cinematic Realism

```text
PBR fidelity: high
physical scale: strict
shape exaggeration: low/medium
texture fidelity: high
roughness variation: high but plausible
lighting realism: high
lighting drama: medium/high
ray/path tracing: preferred for final
DOF/motion blur: physically motivated
post grade: filmic, restrained
```

## Shot-quality checklist

Per shot beoordelen:

```text
1. Is onderwerp direct leesbaar?
2. Is silhouet duidelijk?
3. Heeft beeld foreground/midground/background?
4. Is licht gemotiveerd?
5. Is materiaalreactie consistent met scene-licht?
6. Is focal length bewust gekozen?
7. Heeft camera beweging een verhaalreden?
8. Is focus/DOF functioneel in plaats van decoratief?
9. Zijn hooglichten niet onbedoeld clipped?
10. Is zwartdetail nog leesbaar waar nodig?
11. Werkt shot zonder color grade ook al overtuigend?
12. Houdt de style stand tussen verschillende shots?
```

## Realtime vs final render

### Preview
Prioriteit:
- latency
- stable temporal output
- voldoende shading om keuzes te beoordelen

### Final
Prioriteit:
- anti-aliasing/sample quality
- accurate shadows/reflections/GI
- motion blur
- depth of field
- high precision output
- render passes wanneer compositing nodig is

AI mag een preview nooit als final-quality certificeren zonder het renderprofiel te kennen.

## Material quality validation

Automatische checks:

```text
missing textures
incorrect color spaces
invalid UV sets
roughness outside expected range
unsupported graph nodes
normal map convention mismatch
transparent material sorting risk
shader compile failure
material fallback used
```

## Fouten die we voorkomen

```text
geen gamma-space lighting
geen sRGB normal maps
geen onverklaarde magic exposure
geen style alleen via post-effect
geen engine-specific shader als enige master
geen materiaal zonder fallback/capability check
geen final render zonder expliciet quality profile
```
