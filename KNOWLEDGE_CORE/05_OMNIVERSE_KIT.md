# NVIDIA Omniverse / Kit — Standalone Knowledge

Snapshot: 2026-09 public Kit App Template architecture.

Doel: zelfstandig een OmniverseAdapter en Kit-gebaseerde applicatie ontwerpen zonder opnieuw de onderzochte repositorystructuur te hoeven bestuderen.

## Mental model

Omniverse Kit is extension-driven. Een applicatie is in de praktijk een configuratie van extensions plus settings.

```text
Kit Application (.kit)
  ├── dependencies/extensions
  ├── settings
  ├── UI/layout optional
  ├── USD stage/services
  ├── rendering
  └── streaming layer optional
```

Ontwerp daarom features als losse extensions, niet als één monolithische app.

## Templatekeuzes

### Kit Service
Headless/minimale Kit SDK service. Geschikt voor server-side USD/scene processing zonder volledige editor-UI.

### Base Editor
Minimale GUI voor OpenUSD laden, manipuleren en renderen.

### USD Composer
Voor rijke scene-authoring/configurator workflows: layout, materials, lighting, rendering, variants.

### USD Explorer
Voor grote scenes en collaboration/exploration.

### USD Viewer
Viewport-first app; geschikt voor remote/browser streaming en interaction.

Keuzeregel:

```text
headless backend → Kit Service
AI scene authoring → Base Editor/Composer of headless service + custom UI
browser digital twin/viewer → USD Viewer + streaming
configurator → USD Composer authoring + USD Viewer delivery
```

## Extension types

Basisvormen:

```text
Python Extension
Python UI Extension
C++ Extension
C++ Extension + Python bindings
```

Gebruik Python voor orchestration/tooling en snelle iteration. Gebruik C++ waar runtime/latency/native integration dit vereist.

## App composition

Een `.kit` bestand definieert de app en dependencies. Permanente capability = dependency opnemen in app config. Tijdelijk testen kan via extension manager/dev tooling.

Onze architectuur houdt app-config declaratief:

```text
base app
+ scene extension
+ AI bridge extension
+ material extension
+ physics extension
+ streaming layer
```

## Build / launch / test / package lifecycle

Canonical workflow:

```text
template/scaffold
↓
build
↓
test
↓
launch
↓
package
↓
container/deployment indien nodig
```

Tests moeten minimaal controleren dat app/extension start, belangrijke commands uitvoert en schoon afsluit.

## OpenUSD als kern

Kit-apps gebruiken OpenUSD als scene foundation. Daarom geldt `01_OPENUSD_SCENE_SYSTEM.md` als engine-onafhankelijke truth.

OmniverseAdapter mappt canonical world operations naar:
- active USD stage;
- Kit/Omni USD services;
- extension events;
- renderer/viewport;
- optional Fabric/optimized scene access.

## Custom AI bridge extension

Bouw één narrow bridge extension:

```text
External Orchestrator
↓ authenticated private protocol
AI Bridge Extension
↓
Command Validator
↓
Scene/Rendering/Physics Services
↓
USD Stage
↓
Result + events terug
```

Bridge responsibilities:

```text
connect/session
command IDs
schema validation
allowlist
world version
stage mutation
readback
normalized errors
event emission
health/capabilities
```

Niet doen:
- raw Python eval;
- arbitrary extension enabling vanuit LLM-output;
- directe filesystem writes vanuit untrusted command;
- secrets in stage metadata.

## Application streaming

Kit supports streaming-ready applications via application layers.

Belangrijk patroon:

```text
base_app.kit
      +
streaming_layer.kit
      ↓
streaming-ready app
```

Zo blijft base app schoon en kan dezelfde app lokaal, self-managed streamed of NVIDIA-cloud gericht worden verpakt.

### Self-managed streaming
De template gebruikt een WebRTC-gebaseerde livestream extension voor browser delivery.

### NVIDIA-managed/cloud streaming
NVCF/DGX Cloud-gerichte streaming gebruikt aparte session/health configuration.

Belangrijk: deployment/config verschillen per streaming target; behandel streaming als deployment layer, niet als business logic.

## Browser interaction architecture

```text
browser
  ├── video/audio stream
  └── input/events
        ↓
streaming/session gateway
        ↓
Kit Viewer/App
        ↓
AI Bridge + USD stage
```

AI-control en user-interaction moeten dezelfde world-version/eventbus gebruiken om race conditions te voorkomen.

## Scene authoring

Canonical Omniverse commands:

```text
open_stage
new_stage
create_prim
set_transform
assign_material
create_light
create_camera
set_variant
reference_asset
load/unload payload
save/checkpoint
render/view
```

Voor grotere scenes:
- payloads;
- instancing;
- optimized scene delegate/Fabric waar passend;
- niet per frame volledige USD traversal.

## Renderer / RTX

Omniverse is sterk voor RTX-viewport/path-traced/physically based workflows. Houd renderer selection als profile:

```text
interactive RTX profile
final/path-traced profile
```

World/material data blijft gelijk. Render profile bepaalt sampling, denoising, resolution, effects en performance budgets.

## Materials

Gebruik OpenUSD/UsdShade + MaterialX voor portable look. NVIDIA-specifieke material/MDL capabilities mogen als target specialization worden toegevoegd, niet als enige master wanneer portability vereist is.

Material pipeline:

```text
canonical/MaterialX
↓
Omniverse material adapter
↓
USD material network / supported target material
↓
binding
↓
viewport validation
```

## Physics

Omniverse/PhysX-koppeling behandelt physics schemas als scene-authored config en simulation runtime als stateful engine.

```text
USD prim
+ physics schema
↓
PhysX simulation
↓
runtime transform/events
↓
semantic state terug
```

Zie `03_PHYSICS_SIMULATION.md`.

## Messaging / events

Canonical events:

```text
stage_opened
stage_saved
prim_created
prim_changed
prim_deleted
selection_changed optional
simulation_started/stopped
time_changed
render_started/completed/failed
stream_connected/disconnected
engine_error
```

Throttle/coalesce high-frequency scene changes voordat ze naar externe AI gaan.

## Headless service pattern

Voor een backend zonder UI:

```text
Kit Service
↓
AI Bridge/service extension
↓
OpenUSD stage operations
↓
render/convert/simulate jobs
↓
object storage + job results
```

Geschikt voor batch generation, conversion, validation en render workers.

## Container/deployment

Streaming/container packaging is Linux-oriented in de huidige template tooling. GPU-capabilities en drivers zijn harde deploymentvoorwaarden.

Per deployment vastleggen:

```text
Kit version
GPU type
NVIDIA driver compatibility
render profile
container image digest
app .kit config
extension versions
streaming layer
asset resolver endpoints
```

## OmniverseAdapter API

```text
connect()
healthcheck()
get_capabilities()
open_stage(uri)
create_stage(uri)
create_entity(desc)
update_entity(id, changes)
delete_entity(id)
set_material(id, material)
set_camera(camera)
set_light(light)
set_variant(id, set, value)
execute_simulation(command)
render_preview(profile)
render_final(profile)
get_world_state()
subscribe_events()
checkpoint()
shutdown()
```

## Health fields

```text
kit_version
app_name/app_version
stage URI
renderer
GPU
active extensions required by us
streaming enabled
stream clients
physics available
material capabilities
USD read/write
last command latency
```

## Recovery

- stage checkpoint vóór grote batch;
- own AI edit layer;
- idempotent command IDs;
- after-write readback;
- reconnect na stream/session loss;
- render jobs persist buiten process memory;
- extension startup failures expliciet rapporteren.

## Belangrijk licentiepunt

De Kit App Template repository gebruikt NVIDIA-licentievoorwaarden, geen simpele permissive OSS-licentie voor alles. Daarom bewaren wij hier concepten en interfacekennis, niet hun template/source als onze eigen publieke code. Bij daadwerkelijke Kit-distributie moeten de dan geldende NVIDIA terms opnieuw operationeel worden nageleefd.

## Definition of Omniverse-ready

Zonder handmatig editorwerk:

```text
Kit app/service starten
stage openen/maken
prim maken/wijzigen
assets referencen
materials/lights/camera zetten
physics capability gebruiken
preview renderen
streaming session openen indien gewenst
state/events uitlezen
stage/checkpoint bewaren
veilige fout teruggeven
```
