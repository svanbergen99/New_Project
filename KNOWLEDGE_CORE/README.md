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

11_LTX_AUDIO_VIDEO_GENERATION.md
  Joint audio-video generation, Distilled/DFR, keyframes, audio-to-video, retake, HDR en KCD adaptercontract.

12_AVATAR_ANIMATION_RESEARCH.md
  Vendor-neutrale audio-driven avatararchitectuur: identity injection, prosody/emotion en speaker-specific face conditioning. Tencent-model zelf is research-only voor onze EU-context onder de huidige licentie.

13_AI_3D_MODELING_PBR.md
  Twee-stage image→shape→PBR asset generation, quality tiers, identity validation en engine-ready export. Tencent-model zelf is research-only voor onze EU-context onder de huidige licentie.

14_VIDEO_FOLEY_SOUND.md
  Video/text→sound-event architectuur, temporele sync, 48 kHz masterprincipes, stems/mixing en FoleyAdapter. Tencent-model zelf is research-only voor onze EU-context onder de huidige licentie.

15_COMFYUI_OFFLINE_ORCHESTRATION.md
  Offline/local node-graph orchestration, workflow JSON, queue/WebSocket/history API-patroon, caching, VRAM scheduling en security.

16_REMOTION_PROGRAMMATIC_VIDEO.md
  Deterministische React/timeline-composition, server-side renderflow, tracks/captions/motion graphics en final assembly.

17_TRELLIS_GSPLAT_NEURAL_3D_RENDERING.md
  Image/text→mesh/Gaussian/radiance-field generatie, Gaussian Splatting rendering, hybride mesh+neural worlds en renderadaptercontracten.
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
6. Kies voor AI-video/3D/audio waar nodig uit 11–17.
7. Bouw/test adapters volgens 10.
8. Voeg daarna AI orchestration uit 07 toe.
```

Voor een AI-video pipeline:

```text
script / storyboard
   ↓
Voice Engine
   ↓
11 audio-video generation + 12 avatar concepts
   ↓
13/17 3D assets or neural environments waar nodig
   ↓
14 Foley / sound-event layer
   ↓
15 offline workflow orchestration
   ↓
16 deterministic final composition
   ↓
Video service FFmpeg/FFprobe QC
```

## Kernregel

Onze AI-logica, world model en media-contracten zijn nooit eigendom van Unreal, Omniverse of een andere provider.

```text
OUR CORE
  World Model
  Commands
  Style
  AI Orchestration
  Validation
  Media Contracts
        ↓
ENGINE / MODEL ADAPTER
        ↓
Unreal / Omniverse / local AI models / toekomstige engines
```

Daardoor kunnen engines en modellen vervangen, gecombineerd of parallel gebruikt worden zonder de intelligentielaag opnieuw te ontwerpen.

## Juridische regel

Een publieke repository betekent niet automatisch dat het model vrij inzetbaar is.

Voor iedere externe dependency controleren we afzonderlijk:

```text
code license
model-weight license
territory restrictions
commercial thresholds
redistribution conditions
dataset/asset provenance
```

De 2025 Tencent Hunyuan-licenties die voor probes 12–14 zijn onderzocht sluiten de Europese Unie expliciet uit. Daarom bewaren die modules alleen algemene research/architectuurkennis en mogen die specifieke model/code-dependencies niet automatisch in een Nederlandse/EU KCD-deployment worden opgenomen.

## Wat hier bewust niet staat

```text
externe broncode
vendor templates
modelweights/checkpoints
gebruikersdata
media-output
secrets/API keys
tokens/cookies/logininformatie
oude projectspecifieke services
historische tijdelijke configuraties
```

## Snapshotgrens

Dit core-pakket bewaart de kennis die nodig is om zelfstandig opnieuw te ontwerpen en bouwen op basis van de 2026-era APIs/concepten. Voor toekomstige major engine/modelversies kunnen specifieke method names, licenties, hardware-eisen en plugins veranderen; gebruik dan capability discovery en alleen indien nodig een gerichte compatibility/licentiecheck. De architectuur hoeft daardoor niet opnieuw geleerd of ontworpen te worden.
