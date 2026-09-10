# Sources, Licenses & Version Boundaries

Snapshot captured: 2026-09.

Doel: vastleggen welke publieke technologieën de kennisbasis hebben geïnformeerd, wat we ervan gebruiken, en waar juridische/versiegrenzen zitten. Deze repository bevat geen overgenomen externe broncode.

## Pixar OpenUSD

Source family:
- `PixarAnimationStudios/OpenUSD`
- official OpenUSD API/tutorial documentation

Gebruikte kennis:

```text
Stage / Prim / Property mental model
layers + EditTarget
composition
references / payloads
variants
instancing
UsdGeom
UsdShade material/binding concepts
camera / scene interchange
flattening cautions
```

License note:
De huidige OpenUSD repository vermeldt de Tomorrow Open Source Technology License 1.0 voor OpenUSD, met daarnaast bundled components onder hun eigen licenties. Behandel licentie per daadwerkelijk gebruikte component/version; deze knowledge files kopiëren geen implementation source.

## Academy Software Foundation MaterialX

Source:
- `AcademySoftwareFoundation/MaterialX`
- MaterialX specification/developer guide

Gebruikte kennis:

```text
platform-independent material/look graphs
NodeDef / Node / NodeGraph / Inputs / Outputs
shader generation targets
material portability
renderer specialization
```

License note:
MaterialX is Apache License 2.0.

## Google Filament

Source:
- `google/filament`
- official Filament PBR and Materials documentation

Gebruikte kennis:

```text
practical PBR architecture
metallic/roughness workflow
material layering concepts
image-based lighting
physically based camera/light thinking
HDR/linear rendering
realtime vs quality tradeoffs
```

License note:
Filament is Apache License 2.0.

## NVIDIA PhysX

Source:
- `NVIDIA-Omniverse/PhysX`
- official PhysX documentation

Gebruikte kennis:

```text
physics scene/body/shape architecture
fixed simulation loop
rigid bodies
constraints
collision filtering
callbacks/events
GPU dynamics/broadphase concepts
CPU/GPU fallback thinking
```

License note:
PhysX repository is BSD 3-Clause.

## NVIDIA Warp

Source:
- `NVIDIA/warp`
- official Warp documentation

Gebruikte kennis:

```text
Python-hosted JIT GPU kernels
typed device arrays
CPU/CUDA execution
geometry queries
parallel simulation/compute architecture
minimize host-device synchronization
```

License note:
Warp itself is Apache License 2.0. Some downloaded/linked third-party pieces can have separate terms, including NVIDIA-licensed components. Controleer dependency licenses bij daadwerkelijke packaging.

## NVIDIA Omniverse Kit App Template

Source:
- `NVIDIA-Omniverse/kit-app-template`
- official Omniverse/Kit documentation

Gebruikte kennis:

```text
extension-driven app architecture
Kit Service / Base Editor / USD Composer / USD Explorer / USD Viewer roles
.kit application configuration
build/test/launch/package workflow
application streaming layers
WebRTC-oriented self-managed streaming concept
NVCF/DGX cloud deployment separation
```

License note:
De Kit App Template valt onder NVIDIA software license terms en is niet te behandelen alsof alles permissive OSS is. Daarom is hier alleen architectuurkennis vastgelegd. Bij daadwerkelijk gebruik/distributie van Kit/Omniverse moet de op dat moment geldende NVIDIA license/product-specific terms worden gecontroleerd.

## NVIDIA RTX Remix

Sources:
- `NVIDIAGameWorks/rtx-remix`
- `NVIDIAGameWorks/toolkit-remix`
- related runtime concepts

Gebruikte kennis:

```text
capture → identify → replace → relight architecture
stable asset identity
non-destructive replacement
path tracing as render profile
scene capture as reproducibility/debug tool
```

License note:
De gecombineerde RTX Remix repo toont een MIT license; individuele subrepositories/components kunnen hun eigen license hebben. Onze knowledge base neemt alleen algemene architectuurprincipes over.

## Blender

Source:
- official `blender/blender` mirror
- Blender Python/API/documentation concepts

Gebruikte kennis:

```text
full DCC asset pipeline
headless/offline scripting worker pattern
model/rig/animation/simulation/render/export workflow
```

License note:
Blender als geheel is GPLv3, met individuele bestanden mogelijk onder compatibele andere licenties. We kopiëren geen Blender source. Een los extern Blender automation proces via de officiële API moet juridisch/packaging-technisch gescheiden worden behandeld van proprietary eigen code waar relevant.

## Epic Unreal Engine

Sources:
- Epic Developer Community documentation, Unreal Engine 5.8-era
- Unreal Python API documentation
- Remote Control HTTP/WebSocket documentation
- Sequencer / Control Rig / Niagara / Movie Render Pipeline documentation

Gebruikte kennis:

```text
Python Editor scripting
reflected `unreal` API mental model
Editor subsystems
Remote Control HTTP / WebSocket architecture
Sequencer cinematics
Cine Camera
Control Rig
Niagara timing
Movie Render Queue/Pipeline
Lumen/Nanite/Path Tracer capability awareness
```

License/access note:
Volledige Unreal Engine source is niet gewoon anoniem permissive-public source; Epic-account/GitHub access en Unreal EULA zijn relevant. Deze knowledge base gebruikt publieke documentatie en algemene API-concepten, geen Unreal sourcecode.

## Version rule

Deze kennisbasis is voldoende om een nieuwe implementation tegen de **2026-era concepts** te ontwerpen. Het is niet correct om te stellen dat version-specific method names, plugin names, ports of exact capabilities voor altijd onveranderd blijven.

Daarom geldt:

```text
stable architectural concept
→ mag als langdurige basis worden gebruikt

version-specific API symbol / plugin / config
→ eerst runtime capability discovery
→ bij onbekende toekomstige major version: compatibility check
```

## Dependency policy voor nieuw project

Iedere dependency krijgt in onze eigen projectmanifestatie:

```text
name
version/range
source
license
why_needed
runtime/build-only
distribution implications
security update policy
```

Geen dependency toevoegen puur omdat een referentieproject hem gebruikt.

## Copyright rule

Nieuwe code wordt zelf geschreven op basis van de vastgelegde interfaces en concepten. We kopiëren geen grote stukken code, shader implementations, templates, documentation of assets uit deze bronnen naar onze eigen repository.

## Re-check triggers

Normaal hoeven we de bronrepositories niet opnieuw te lezen om een nieuw ontwerp te maken. Wel opnieuw officiële documentatie/licenties controleren wanneer één van deze situaties optreedt:

```text
nieuwe major engine/SDK version
API symbol ontbreekt tijdens integration
capability verschilt van snapshot
product wordt commercieel gedistribueerd met externe runtime/SDK
license/product terms veranderen
security advisory raakt dependency
nieuw hardware/rendering backend vereist andere feature path
```

Dat is compatibility maintenance, niet opnieuw kennis vanaf nul opbouwen.
