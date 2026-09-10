# TRELLIS + gsplat — Standalone Neural 3D Generation / Rendering Knowledge

Snapshot: 2026-09.

Doel: image/text → 3D asset generation combineren met snelle Gaussian Splatting rendering voor KCD character/world experiments.

## Licentie

- Microsoft TRELLIS repository: MIT License.
- nerfstudio-project/gsplat: Apache License 2.0.
- Losse pretrained modelweights/datasets kunnen aanvullende voorwaarden hebben en moeten afzonderlijk worden gecontroleerd.
- Geen accounttokens, modelweights of credentials worden in deze knowledge core opgeslagen.

## TRELLIS kernidee

TRELLIS gebruikt één structured latent representatie die naar meerdere 3D-representaties kan worden gedecodeerd.

```text
text or image condition
        ↓
structured 3D latent
        ↓
   ┌────┼────────┐
   ↓    ↓        ↓
 mesh  3DGS   radiance field
```

Dit is nuttig omdat downstream taken verschillende representaties nodig hebben:

```text
mesh       → game engines / collision / rigging / GLB
3D Gaussian→ snelle neural rendering / view synthesis
radiance field → view-dependent appearance experiments
```

## Image-conditioned first

De referentie raadt image-conditioned generation aan wanneer detail/creativiteit belangrijk is.

KCD-patroon:

```text
KC-Dee reference art
 ↓
clean canonical image / multi-view references
 ↓
image→3D generator
 ↓
mesh + gaussian representations
```

Text-only kan als concepting-stage dienen, maar character identity krijgt een image reference.

## Canonical 3D generation contract

```text
Generate3DRequest
  reference_images[] optional
  prompt optional
  seed
  output_representations[]: mesh|gaussian|radiance_field
  quality_tier
  simplify_target optional
  texture_size optional

Generate3DResult
  mesh optional
  gaussian_scene optional
  radiance_field optional
  preview_turntable optional
  metadata
  warnings[]
```

## Export pattern

Een goede 3D pipeline kan ten minste:

```text
mesh → GLB/USD
Gaussian → PLY or internal splat format
preview → MP4/image sequence
```

Voor KCD blijft GLB/USD de voorkeursuitwisseling richting traditionele engines; Gaussian data blijft een renderrepresentation, niet onze enige assetwaarheid.

## Hardware lesson

De onderzochte TRELLIS setup noemt Linux + NVIDIA GPU en minimaal ongeveer 16 GB GPU-geheugen voor de officiële pipeline. Zie dit als planningindicatie, niet als eeuwig hardwarecontract.

## gsplat kernidee

gsplat is een CUDA-versnelde differentiable rasterizer voor 3D Gaussians.

Een Gaussian bevat conceptueel:

```text
position
scale/covariance
orientation
opacity
color / spherical-harmonic coefficients
```

Rendering projecteert grote aantallen Gaussians naar beeldtiles en alpha-compositeert hun bijdrage.

## Waarom Gaussian Splatting interessant is

Sterke punten:

```text
very fast novel-view rendering
view-dependent appearance
compact neural scene representation
real-time-ish camera movement
useful for captured environments
```

Voor KCD kan dit vooral werken voor:

```text
realistische vakantielocaties
room/office capture
background worlds
fast camera fly-throughs
hybrid 3D scenes
```

## gsplat 2026 capability lessons

De actuele library heeft onder meer patronen voor:

```text
CUDA rasterization
multiple camera/sensor models
spherical harmonics
multi-GPU paths
sparse rendering
Gaussian ID/count/contributor queries
low-latency inference-only rendering
trajectory / pose operations
```

Belangrijk voor onze architectuur: we kunnen niet alleen RGB renderen, maar ook IDs/depth/extra signals gebruiken voor compositing, masks en AI feedback.

## Canonical GaussianScene

```text
scene_id
positions
scales
rotations
opacities
appearance_coefficients
bounds
coordinate_system
source_provenance
quality_tier
```

## Canonical RenderRequest

```text
scene_id
camera_pose
camera_model
width
height
near/far
render_modes[]: color|depth|id|normal_like optional
quality_profile
```

## Render outputs

```text
color
optional depth
optional entity/gaussian IDs
optional contributor metadata
render_time_ms
warnings[]
```

## Hybrid KCD world

Gebruik niet alles als Gaussian. Verdeel per type:

```text
KC-Dee hero character → mesh/PBR/rig
interactive props      → mesh
captured beach/world   → Gaussian scene
UI/holograms           → native engine/Remotion overlay
```

Dit geeft realistische achtergronden zonder physics/animation van de bot onmogelijk te maken.

## Asset-to-video flow

```text
reference art
 ↓
TRELLIS-like 3D generation
 ↓
mesh + Gaussian preview
 ↓
asset QC
 ↓
scene placement
 ↓
render camera trajectory via gsplat/engine
 ↓
frames/video
 ↓
AI-video enhancement or Remotion composition
```

## Scene reconstruction flow

Voor echte omgevingen:

```text
multi-view photos/video
 ↓
camera calibration / poses
 ↓
Gaussian optimization
 ↓
trained scene
 ↓
free camera trajectory
 ↓
realtime/final render
```

Camera calibration en accurate poses zijn cruciaal; slechte inputposes veroorzaken floaters/blur/geometry artifacts.

## Neural render QC

```text
floaters
holes
blurred geometry
view-dependent popping
edge artifacts
exposure inconsistency
incorrect scale
unstable thin objects
bad camera path
```

## KCD adapter split

Houd generatie en rendering los:

```text
Neural3DGeneratorAdapter
  generate_from_image()
  generate_from_text()
  export_mesh()
  export_gaussians()

GaussianRendererAdapter
  load_scene()
  render_frame()
  render_trajectory()
  render_auxiliary_buffers()
```

Zo kan een betere 3D-generator later TRELLIS vervangen zonder de renderer te herschrijven, en andersom.

## Geen keys profiel

De renderer zelf kan volledig lokaal draaien met lokale scene-data en GPU. Voor pretrained generatorweights geldt: acquire ze apart volgens hun actuele licentie/toegang en laad daarna vanaf lokale disk. Credentials horen nooit in de pipelineconfig of Git.

## Kernles

Voor maximale KCD-realiteit is de sterkste hybride aanpak waarschijnlijk: **mesh/PBR voor KC-Dee en interactieve objecten + Gaussian Splatting voor zeer realistische omgevingen + traditionele compositor/video pipeline voor de final**.
