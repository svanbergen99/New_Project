# Unreal Engine Control — Standalone Knowledge

Snapshot: Unreal Engine 5.8-era public API/documentation, captured 2026-09.

Doel: zelfstandig een UnrealAdapter bouwen die Unreal vanuit een externe AI/orchestrator kan besturen zonder afhankelijk te zijn van handmatig editorwerk.

## Toegangslagen

Unreal heeft meerdere bruikbare automatiseringslagen. Kies per taak de juiste:

```text
External AI / backend
   ├── HTTP Remote Control
   ├── WebSocket Remote Control
   └── custom bridge/plugin
             ↓
Unreal Editor / Runtime
   ├── Python Editor API
   ├── Blueprints
   └── C++ API
```

### Python Editor API
Gebruik voor editor-automation, asset creation/import, actors/levels, sequencer, rigging en batch pipelines.

Belangrijk:
- alles zit in de `unreal` Python module;
- veel C++/Blueprint-exposed functionality wordt naar Python gereflecteerd;
- beschikbare Python surface kan veranderen wanneer plugins aan/uit staan;
- behandel Python API als editor-oriented tenzij specifieke runtime support bewezen is.

### Remote Control HTTP
Gebruik voor externe request/response control van exposed objects/properties/functions.

Default HTTP port in de 5.8 docs: `30010`.

`GET /remote/info` kan beschikbare routes beschrijven.

Remote Control is een Beta-feature: niet onbeveiligd als publieke productie-API exposen.

### Remote Control WebSocket
Gebruik voor persistent realtime control/events.

Default WebSocket port in de 5.8 docs: `30020`.

Bouw extern altijd een authenticated gateway vóór deze endpoint; niet direct internet-facing.

### Custom C++ plugin/bridge
Gebruik wanneer:
- Remote Control onvoldoende low-level capabilities biedt;
- runtime performance belangrijk is;
- custom transport/protocol nodig is;
- specifieke engine callbacks nodig zijn.

## UnrealAdapter architectuur

```text
World Orchestrator
↓
UnrealAdapter
  ├── UnrealRemoteClient (HTTP/WS)
  ├── UnrealCommandMapper
  ├── UnrealStateReader
  ├── UnrealAssetManager
  ├── UnrealCinematicManager
  └── UnrealRenderManager
↓
Unreal
```

Adapter moet intern altijd capability discovery doen en plugin requirements rapporteren.

## Editor subsystems

Belangrijke concepten/classes uit de reflected Python API:

```text
EditorActorSubsystem
EditorAssetSubsystem / EditorAssetLibrary
LevelEditorSubsystem
AssetTools / AssetToolsHelpers
SequencerTools
Movie Pipeline / Movie Render Queue APIs
Control Rig scripting APIs
```

Gebruik subsystem-based APIs boven verouderde convenience libraries wanneer beide bestaan.

## World/level operations

Minimale capabilities:

```text
open level/map
save level
spawn actor
find actor by tag/path/id
destroy actor
set actor transform
set visibility/tags
create folders/groups
read selected/current world state
```

Onze IDs mogen niet alleen Unreal object paths zijn. Sla een eigen stable `entity_id` op in tag/metadata/component waar praktisch.

## Asset operations

Canonical flow:

```text
asset URI
↓
download/resolve safely
↓
validate type/size
↓
import task
↓
asset created
↓
post-process/configure
↓
save asset
↓
return canonical asset_id + Unreal path
```

Capabilities:

```text
import mesh/texture/audio/animation
create material instance
set asset metadata
rename/move/duplicate
save/load
check existence
resolve dependencies
```

Nooit user/model-output rechtstreeks als filesystem path vertrouwen.

## Materials

Mapping canonical material → Unreal:

```text
Canonical Material
↓
Material master / graph template
↓
Material Instance
↓
parameters/textures
↓
assign to mesh slot
```

Gebruik een kleine set goed ontworpen master materials en parameterized material instances waar mogelijk. Dat is robuuster en goedkoper dan per AI-opdracht een compleet nieuwe shadergraph genereren.

Voor gespecialiseerde style effects kunnen aparte masters bestaan:

```text
PBR Realistic
Stylized PBR
Toon/graphic
Glass/transmission
Skin/subsurface
FX/unlit
```

## Cinematics: Sequencer

Sequencer is de kern voor cinematics. Een Level Sequence bevat tracks, bindings, cameras, keys en animations; een Level Sequence Actor koppelt deze data aan een level.

Canonical shot mapping:

```text
Shot
↓
Level Sequence
  ├── Camera Cuts
  ├── Cine Camera track
  ├── Actor transform tracks
  ├── Light/property tracks
  ├── Animation tracks
  ├── Control Rig tracks
  ├── Niagara lifecycle tracks
  └── Event tracks
```

UnrealAdapter moet minimaal:

```text
create/load sequence
set playback range
create/bind cine camera
add transform/property keys
set camera cut
add actor binding
add animation/control rig linkage
save sequence
```

## Cine Camera

Canonical Camera mapping:

```text
transform
focal length
filmback/sensor
aperture f-stop
focus mode/distance/target
shutter/exposure afhankelijk rendering setup
```

AI shot planner denkt in composition/lens intent, adapter vertaalt naar concrete CineCameraComponent properties.

## Control Rig

Control Rig laat characters in-engine riggen en animeren en kan met Sequencer/Python worden bestuurd.

Gebruik voor:
- procedural poses
- AI-directed body motion
- camera-ready character adjustments
- constraints/space switching

Houd high-level animation intent los van rig control names:

```text
"look at target"
"raise right hand"
"lean forward 10°"
```

→ CharacterRigAdapter
→ specifieke Control Rig controls.

## Niagara

Niagara = realtime VFX/particles.

Voor cinematics:
- system actor/component in world;
- Sequencer Niagara life-cycle track voor timing;
- simulation caching waar reproduceerbaarheid/final render vereist is;
- MRQ-support plugin waar nodig.

AI gebruikt semantic FX commands:

```text
spawn_rain
increase_dust
trigger_explosion
set_fire_intensity
```

niet raw emitter parameter names buiten adapter.

## Rendering features

Voor desktop deferred (capability afhankelijk hardware/render path) zijn belangrijke cinematic features:

```text
Lumen GI/reflections
Nanite virtualized geometry
Virtual Shadow Maps
Temporal Super Resolution
hardware ray tracing
Path Tracer
post processing
```

Niet elke rendering path ondersteunt alles. Adapter moet project/render-path capabilities inspecteren voordat een profile wordt toegepast.

## Preview render profile

```text
realtime viewport/game render
Lumen indien beschikbaar
Nanite/VSM indien passend
TSR/dynamic resolution waar nodig
moderate effects
low latency
```

## Final cinematic profile

Movie Render Pipeline / Movie Render Queue gebruiken voor hoogwaardige output.

Voordelen:
- hogere quality/sample settings;
- betere motion blur/AA mogelijkheden;
- high-quality Lumen/ray-tracing configuration;
- render formats/passes;
- presets;
- offline render los van interactive framerate.

Canonical RenderJob:

```text
sequence
map/world
frame range
fps
resolution
output format/path
render profile
anti-aliasing/sample config
color config
render passes
status
```

## Render passes

Voor compositing ondersteunen we waar beschikbaar:

```text
beauty/final
object IDs
extra engine-supported passes
```

Niet aannemen dat deferred renderer elke klassieke offline AOV kan reconstrueren.

## Remote control security

Remote Control biedt externe HTTP/WS-mogelijkheden en moet daarom achter onze gateway.

```text
Internet/client
X--> Unreal ports direct

Internet/client
→ authenticated KCD gateway
→ command validation/allowlist
→ private/local Unreal Remote Control
```

Allowlist operations. Geen willekeurige UObject path/function execution vanuit raw LLM-output.

## Runtime vs Editor

Belangrijke scheiding:

```text
Editor automation
= asset authoring, imports, sequencer editing, tooling

Runtime control
= gameplay/world state tijdens draaiende executable
```

Ontwerp geen productie-runtime die alleen werkt doordat Editor-only Python classes toevallig aanwezig zijn.

Voor runtime-heavy product:
- Blueprints/C++ runtime components;
- custom service/plugin;
- Remote Control alleen wanneer supported/geschikt;
- external orchestrator via eigen narrow protocol.

## External Unreal protocol

Onze gateway exposeert bijvoorbeeld:

```text
POST /worlds/{id}/entities
PATCH /worlds/{id}/entities/{id}
POST /worlds/{id}/shots
POST /worlds/{id}/actions
POST /worlds/{id}/renders
GET  /worlds/{id}/state
WS   /worlds/{id}/events
```

Unreal-specifieke details blijven achter UnrealAdapter.

## Healthcheck

UnrealAdapter health bevat:

```text
connected
editor/runtime mode
engine version
project name
current map
remote HTTP available
remote WS available
required plugins enabled
render capabilities
GPU/render path
sequence capability
MRQ capability
```

## Recovery

- command IDs idempotent maken waar mogelijk;
- save/checkpoint vóór grote destructive batch;
- world version controleren;
- na mutation readback;
- editor crash/restart detecteren;
- pending render jobs opnieuw reconciliëren;
- asset import partial failure expliciet afhandelen.

## Definition of Unreal-ready

Zonder handmatig klikken kunnen wij:

```text
connect
map openen
actor maken/verplaatsen/verwijderen
asset importeren
materiaal toewijzen
licht en CineCamera plaatsen
Level Sequence maken
keys/shot instellen
Niagara/animation timing koppelen
preview bekijken
MRQ render starten
status/resultaat terugkrijgen
world state lezen
```

Als deze lijst werkt, kan AI er veilig bovenop worden gezet.
