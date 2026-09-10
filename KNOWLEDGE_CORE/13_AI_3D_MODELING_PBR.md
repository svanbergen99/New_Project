# AI 3D Modeling + PBR — Standalone Research Knowledge

Snapshot: 2026-09.

Bronfamilie: Hunyuan3D-2.1 als researchreferentie voor image-to-3D shape generation en fysiek gebaseerde texture synthesis.

## Belangrijke licentiegrens

De huidige Tencent Hunyuan3D-2.1 Community License sluit de Europese Unie, het Verenigd Koninkrijk en Zuid-Korea expliciet uit. Vanuit Nederland behandelen we dit model daarom niet als inzetbare KCD-dependency onder de huidige licentie.

Deze module bewaart alleen algemene ontwerpkennis. Geen Tencent-code, weights, checkpoints of credentials.

## Kernidee

Splits AI-3D generatie in twee afzonderlijke stappen:

```text
reference image(s)
   ↓
shape generation
   ↓
clean / validate mesh
   ↓
PBR material generation
   ↓
engine-ready asset
```

Shape en appearance mogen onafhankelijk opnieuw worden gegenereerd. Dat is belangrijk omdat geometry-fouten en texture-fouten andere correcties vereisen.

## Canonical shape stage

Input:

```text
reference_images[]
object_mask optional
scale_hint
symmetry_hint optional
seed
quality_tier
```

Output:

```text
mesh
bounds
vertex/triangle counts
normals
uvs optional
confidence/warnings
```

Validation:

```text
non-zero bounds
no NaN/Inf
valid normals
consistent winding
reasonable topology
no catastrophic self-intersections
degenerate triangles flagged
scale and up-axis known
```

## Canonical PBR paint stage

Gebruik niet één baked RGB texture als volledige waarheid. Maak een fysiek gebaseerd materialpakket.

```text
base_color
roughness
metallic
normal
ambient_occlusion
emissive optional
opacity optional
subsurface/transmission optional
```

Doel: dezelfde asset moet onder verschillende lampen en omgevingen geloofwaardig blijven reageren.

## Waarom PBR voor KC-Dee belangrijk is

KC-Dee heeft duidelijke materiaalzones nodig, bijvoorbeeld:

```text
painted shell
brushed / polished metal
visor glass
emissive cyan eyes / accents
rubber or dark trim
```

Wanneer metallic/roughness/normal apart bestaan kan een beach sunset, donkere KCD-desktop of studioverlichting dezelfde 3D-bot overtuigend belichten.

## Material reconstruction flow

```text
reference views
  ↓
semantic region detection
  ↓
base color estimate
  ↓
surface-property estimate
  - roughness
  - metallic
  - normal/detail
  ↓
view consistency
  ↓
UV projection / texture baking
  ↓
seam repair
  ↓
PBR validation
```

## Multi-view principle

Eén afbeelding bevat verborgen kanten. Voor hero-assets:

```text
front + 3/4 + side + back references
```

zijn beter dan één losse frontafbeelding. Als alleen één afbeelding bestaat, markeer unseen surfaces als inferred en geef ze lagere confidence.

## Quality tiers

```text
proxy
- snelle vorm
- simpele texture
- preview only

realtime
- schone mesh
- normale PBR maps
- LOD-ready

hero
- hoge silhouette fidelity
- micro-normal / roughness variation
- goede close-up textures

final
- hoogste texture resolution
- displacement/detail indien target dit ondersteunt
```

## Resource lesson uit de referentie

Shape generation en PBR texturing hebben verschillende GPU-profielen. In de onderzochte 2025 Hunyuan3D-2.1 setup werd ongeveer 10 GB VRAM genoemd voor shape, 21 GB voor texture en circa 29 GB voor gecombineerd gebruik. Gebruik dit alleen als orde-van-grootte voor planning, niet als universeel hardwarecontract.

## Canonical Model3DAdapter

```text
capabilities()
generate_shape(reference, options)
paint_pbr(mesh, reference, options)
validate_mesh(mesh)
validate_materials(material_set)
make_lods(mesh)
export_glb(asset)
export_usd(asset)
render_turntable(asset)
```

## KCD asset flow

```text
KC-Dee reference art / stickers
 ↓
reference cleanup + silhouette mask
 ↓
shape generator
 ↓
mesh validator / repair
 ↓
PBR painter
 ↓
material validator
 ↓
GLB/USD canonical asset
 ↓
Unreal / Omniverse / WebGPU renderer
 ↓
turntable + lighting QC
```

## Identity preservation

Een 3D-generator mag de karakteridentiteit niet vrij interpreteren. Bewaar expliciete constraints:

```text
head/body proportions
visor shape
eye spacing
cyan accent placement
logo/marking locations
antenna/accessories
primary silhouette
```

Vergelijk renders vanuit vaste camera-hoeken tegen referentiebeelden.

## Output contract

```text
asset_id
mesh_uri
material_set
texture_uris
units
up_axis
forward_axis
bounds
lods[]
source_references[]
seed
quality_tier
validation_report
```

## Niet opslaan

- Tencent source code
- Tencent modelweights/checkpoints
- Hugging Face/accounttokens
- vendor credentials

## Kernles

Voor KCD moet AI modeling een **twee-stage systeem** blijven: eerst geometry, daarna PBR look-development. Hierdoor kunnen we vorm, materiaal en belichting afzonderlijk verbeteren en dezelfde KC-Dee asset in meerdere renderengines gebruiken.
