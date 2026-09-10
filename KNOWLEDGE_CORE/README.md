# Visual Knowledge Core

Dit is de zelfstandige kennisbasis voor het opnieuw bouwen van een nieuwe AI-gestuurde realtime visual / cinematic / game-engine stack.

## Bestanden

```text
00_MASTER_BLUEPRINT.md
  Hoofdarchitectuur, world model, adapters, scene/material/physics/cinematic principes.

01_OPENUSD_SCENE_SYSTEM.md
  OpenUSD Stage/Prim/Layers/composition, assets, transforms, cameras, lights, UsdShade en authoringregels.

02_MATERIALS_CINEMATIC_RENDERING.md
  MaterialX/PBR-principes, fysieke camera/licht, realtime/final rendering en styleprofielen.

03_PHYSICS_SIMULATION.md
  PhysX/Warp-geïnspireerde rigid-body, events, GPU simulation, geometry queries en custom compute.

04_UNREAL_ENGINE_CONTROL.md
  Unreal Python Editor API, Remote Control HTTP/WS, assets, Sequencer, CineCamera, Control Rig, Niagara en Movie Render Pipeline.

05_OMNIVERSE_KIT.md
  Omniverse Kit app/extension architecture, OpenUSD workflows, headless services en browser/cloud streaming.

06_ASSET_PIPELINE_AND_RTX.md
  Volledige 3D asset pipeline, Blender automation pattern, asset identity/replacement en RTX/path-tracing lessen.

07_AI_WORLD_ORCHESTRATION.md
  AI intent → plan → validated commands → engine → observation → correction loop.

08_SOURCES_LICENSES_AND_VERSION_LIMITS.md
  Bronfamilies, licentiegrenzen en wanneer compatibility re-checks noodzakelijk zijn.

09_ENGINE_ADAPTER_CONTRACTS.md
  Vaste interne schemas voor Entities, Materials, Camera, Physics, Shots, Commands, Results en Events.

10_TESTING_AND_REBUILD.md
  Vanaf-nul rebuild, contracttests, cinematic/physics tests, failure injection, security en autonomy gates.
```

Daarnaast blijven in de root:

```text
REBUILD_CORE.md
LESSONS_LEARNED.md
```

`REBUILD_CORE.md` bevat de minimale algemene systeem-bouwprincipes. `LESSONS_LEARNED.md` bewaart fouten/patronen uit eerder Voice/Text werk die we niet opnieuw willen maken.

## Hoe deze kennis te gebruiken

Voor een nieuw project:

```text
1. Lees 00_MASTER_BLUEPRINT.
2. Kies target engine(s).
3. Gebruik 09 als intern API-contract.
4. Gebruik het relevante enginebestand 04 en/of 05.
5. Voeg 01/02/03/06 toe voor scene, rendering, physics en assets.
6. Bouw/test eerst adapter volgens 10.
7. Voeg daarna AI orchestration uit 07 toe.
```

## Kernregel

Onze AI-logica en world model zijn nooit eigendom van Unreal, Omniverse of een andere provider.

```text
OUR CORE
  World Model
  Commands
  Style
  AI Orchestration
  Validation
        ↓
ENGINE ADAPTER
        ↓
Unreal / Omniverse / toekomstige engine
```

Daardoor kunnen engines vervangen, gecombineerd of parallel gebruikt worden zonder de intelligentielaag opnieuw te ontwerpen.

## Wat hier bewust niet staat

```text
externe broncode
vendor templates
gebruikersdata
media-output
secrets/API keys
oude projectspecifieke services
historische tijdelijke configuraties
```

## Snapshotgrens

Dit core-pakket bewaart de kennis die nodig is om zelfstandig opnieuw te ontwerpen en bouwen op basis van de 2026-era APIs/concepten. Voor toekomstige major engineversies kunnen specifieke method names/plugins veranderen; gebruik dan capability discovery en alleen indien nodig een gerichte compatibility check. De architectuur hoeft daardoor niet opnieuw geleerd of ontworpen te worden.
