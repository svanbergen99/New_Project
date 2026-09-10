# Asset Pipeline + RTX Concepts — Standalone Knowledge

Snapshot: 2026-09.

Doel: genoeg algemene 3D-pipelinekennis bewaren om assets zelfstandig te genereren, importeren, valideren en cinematic-ready te maken. Blender dient hier als referentie voor een complete DCC-pipeline; RTX Remix als referentie voor capture/replacement/path-traced relighting-concepten.

## Complete asset lifecycle

```text
source / generated asset
↓
import
↓
geometry validation
↓
scale/orientation normalization
↓
UV/material/texture validation
↓
rig/animation validation indien van toepassing
↓
LOD/optimization
↓
collision generation
↓
engine conversion/import
↓
scene placement
↓
lookdev validation
↓
package/version
```

## Canonical Asset record

```text
asset_id
version
kind: mesh|character|material|texture|animation|environment|fx|audio
source_uri
canonical_uri
format
units
up_axis
forward_axis
bounds
materials[]
textures[]
rig optional
animations[]
collision optional
lods[]
tags[]
license/provenance
created_at
```

## Geometry validation

Check minimaal:

```text
valid vertex/index buffers
no NaN/Inf coordinates
non-zero scale/bounds
normals aanwezig of genereerbaar
tangents wanneer normal mapping vereist
UV0 wanneer textured
non-manifold alleen waar bewust
extreme polygon count gemarkeerd
degenerate triangles gemarkeerd
consistent winding
pivot/origin policy
```

## Coordinate normalization

Engines verschillen in handedness, up-axis en units. Nooit impliciet aannemen.

Intern gebruiken wij een canonical coordinate contract en adapterconversies.

Asset import metadata bewaart altijd:

```text
source_units
source_up
source_forward
conversion_matrix
```

Zo kan dezelfde asset reproduceerbaar opnieuw worden geïmporteerd.

## UV / textures

Validation:

```text
missing UVs
out-of-range UVs indien niet bewust tiled
lightmap UV requirement per target
texture dimensions
color-space semantics
normal orientation
missing files
unsupported compression/format
```

## Characters

Character asset bestaat uit losse concerns:

```text
skeletal mesh
skeleton hierarchy
skin weights
control/rig mapping
animation clips
facial/morph targets optional
physics asset optional
materials
```

AI gebruikt semantic bones/controls via een CharacterAdapter. Geen globale afhankelijkheid van één specifieke rig naming convention.

Canonical semantic controls:

```text
root
pelvis
spine/chest/head
left/right arm/hand
left/right leg/foot
eyes/gaze
jaw/mouth optional
```

Adapter mappt naar echte rig.

## Animation

Canonical clip:

```text
clip_id
duration
fps/sample rate
skeleton_id
tracks
root motion policy
loop flag
events/markers
```

Voor cinematic generation kunnen procedural/AI poses en bestaande clips gecombineerd worden via sequencer/timeline layers.

## Procedural generation

Nieuwe assets/world pieces moeten declaratief worden beschreven:

```text
shape/layout constraints
material family
scale range
style profile
seed
quality budget
collision need
LOD need
```

Sla seed + parameters op zodat generation reproduceerbaar is.

## Blender als offline DCC-referentie

Blender ondersteunt de volledige 3D content pipeline: modeling, rigging, animation, simulation, rendering, compositing en scripting.

Voor ons is het belangrijkste herbruikbare patroon:

```text
headless/offline asset worker
↓
Python automation
↓
import/generate/edit
↓
validate
↓
export canonical format
↓
engine ingest
```

We hoeven Blender-internals niet te kopiëren. Wanneer Blender als tool gekozen wordt, schrijven we een `BlenderAdapter` die via zijn Python API alleen onze asset operations uitvoert.

Minimal BlenderAdapter:

```text
open_scene/new_scene
import_asset
create_mesh/material
set transforms
apply modifiers optional
rig/animate optional
bake textures optional
render preview optional
export asset
validate scene
```

## Asset exchange formats

Voorkeur per doel:

```text
OpenUSD = complexe scene/assembly/interchange
MaterialX = material/look graph interchange
glTF = compacte realtime asset delivery
FBX = legacy/industry interchange waar target vereist
EXR = HDR/final image/render-pass
PNG/JPEG = display textures/images waar geschikt
```

Format is transport, niet onze interne waarheid.

## RTX Remix kernlessen

RTX Remix bestaat conceptueel uit:

```text
legacy scene capture
↓
scene/object identification
↓
asset/material/light replacement
↓
inject replacements tijdens playback
↓
path-traced relighting
↓
upscaling/frame technologies
```

Voor ons nieuwe systeem zijn vooral deze architectuurpatronen waardevol:

### 1. Stable asset identity
Om een object later te vervangen moet het deterministisch herkend worden. Daarom krijgt elk generated/imported object een stable asset/entity identity onafhankelijk van renderer handle.

### 2. Non-destructive replacement
Origineel en replacement blijven logisch gescheiden:

```text
source entity
→ replacement mapping
→ target asset/material/light
```

Dit past direct bij USD layers/variants.

### 3. Relighting als aparte laag
Geometry hoeft niet opnieuw gemaakt te worden om look volledig te veranderen. Houd lighting state onafhankelijk van object assets.

### 4. Path tracing als final profile
Path tracing is een rendering mode, niet een world model. Dezelfde scene moet realtime/rasterized én final/path-traced kunnen draaien als target dit ondersteunt.

### 5. Capture/debug snapshot
Voor complexe realtime bugs is een capture/snapshot van scene state essentieel. Onze engine bridge moet daarom een reproduceerbare world snapshot kunnen maken.

## Replacement system

Canonical mapping:

```json
{
  "source_asset_id": "chair-v1",
  "replacement_asset_id": "chair-cinematic-v4",
  "scope": "world|shot|entity",
  "material_overrides": {},
  "enabled": true
}
```

Gebruik priority/layer rules zodat shot-specific overrides niet globale art direction vernietigen.

## Cinematic asset quality tiers

```text
proxy
  fast iteration, lage detail

realtime
  game-ready topology/textures/LODs

hero
  close-up quality, high texture/material fidelity

final-only
  zeer hoge detail / zware FX / path-traced use
```

AI kiest tier op basis van shot importance en afstand tot camera.

## LOD policy

LOD selecteren op projected screen size/importance, niet alleen world distance.

Hero objecten in focus mogen hogere tier krijgen; background crowd/props lagere.

## Asset provenance

Altijd bewaren:

```text
source
license
creator/provider
version
transformation history
AI-generated flag indien relevant
usage restrictions
```

Geen onbekende internetasset automatisch in productie opnemen.

## Content cache

Pipeline:

```text
asset request
→ resolve version
→ check content-addressed cache
→ download/build indien nodig
→ hash verify
→ use
```

Cache key bij voorkeur content hash + conversion profile.

## Fouten die we voorkomen

```text
geen lokale path als asset identity
geen import zonder unit/axis validation
geen textures zonder semantic color space
geen rig afhankelijk maken van willekeurige bone names
geen path tracing koppelen aan world logic
geen destructive replacement van source asset
geen generated asset zonder seed/version/provenance
geen hero-detail op alles; quality budget per shot
```
