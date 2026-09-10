# Visual Knowledge Core — Master Blueprint

Snapshot: 2026-09.

Doel: vanuit deze repository zelfstandig een nieuwe realtime visual / cinematic / game-engine AI-applicatie kunnen ontwerpen zonder opnieuw afhankelijk te zijn van de onderzochte bronrepositories.

Dit is een kennisbasis, geen kopie van externe broncode. Nieuwe implementaties worden opnieuw geschreven rond de hieronder vastgelegde concepten en contracten.

## Hoofdarchitectuur

```text
User / AI intent
      ↓
Intent parser
      ↓
World Orchestrator
      ↓
Canonical World Model
      ├── Scene graph
      ├── Materials
      ├── Cameras / lighting
      ├── Animation
      ├── Physics
      └── Runtime state
      ↓
Engine Adapter Layer
      ├── UnrealAdapter
      ├── OmniverseAdapter
      ├── USDAdapter
      ├── MaterialAdapter
      └── PhysicsAdapter
      ↓
Realtime Engine / Renderer
      ↓
frames + events + world state
      ↓
AI feedback loop / client
```

## Canonieke interne objecten

Externe engines mogen hun eigen namen/schema's hebben. Intern gebruiken wij altijd dezelfde concepten:

```text
World
Entity
Transform
Geometry
Material
Light
Camera
Animation
PhysicsBody
Constraint
Effect
Shot
RenderJob
WorldEvent
EngineCommand
EngineResult
```

Een adapter vertaalt deze objecten naar Unreal, Omniverse/OpenUSD of een andere toekomstige engine.

## Scheiding van verantwoordelijkheden

### Orchestrator
Beslist wat moet gebeuren. Weet niets van specifieke HTTP-routes of SDK details.

### World Model
Bevat gewenste en waargenomen wereldstatus. Stable IDs zijn verplicht.

### Adapter
Kent één externe engine/API. Verantwoordelijk voor connectie, capability discovery, mapping, timeouts, retries, errors en normalisatie.

### Renderer / Engine
Voert uit. Is nooit de bron van productlogica.

### Collector / Gateway
Ontvangt externe input/events, valideert, normaliseert, beveiligt en routeert.

## Minimale adapter-interface

Iedere engine-adapter implementeert conceptueel:

```text
connect()
healthcheck()
get_capabilities()
create_world()
load_world()
save_world()
create_entity()
update_entity()
delete_entity()
set_transform()
set_material()
set_light()
set_camera()
set_animation()
set_physics()
execute_action()
render_preview()
render_final()
subscribe_events()
get_world_state()
shutdown()
```

Niet iedere engine ondersteunt alles. `get_capabilities()` bepaalt dynamisch wat kan.

## Command contract

Iedere mutatie heeft minimaal:

```json
{
  "command_id": "uuid",
  "world_id": "world-1",
  "entity_id": "entity-optional",
  "operation": "set_transform",
  "payload": {},
  "expected_version": 12,
  "timestamp": "UTC",
  "correlation_id": "uuid"
}
```

Gebruik optimistic versioning om te voorkomen dat AI of meerdere clients elkaar stil overschrijven.

## Result contract

```json
{
  "command_id": "uuid",
  "ok": true,
  "engine": "unreal|omniverse|other",
  "world_version": 13,
  "result": {},
  "error": null,
  "latency_ms": 0
}
```

Fouten worden genormaliseerd naar:

```text
error_code
safe_message
source
retryable
correlation_id
```

## World-state lus

```text
AI maakt plan
   ↓
commands uitvoeren
   ↓
engine events + state teruglezen
   ↓
state normaliseren
   ↓
verschil gewenst ↔ werkelijk bepalen
   ↓
AI corrigeert of vervolgt
   ↺
```

AI mag nooit aannemen dat een engine-opdracht gelukt is zonder resultaat/statebevestiging.

## Renderingstrategie

Gebruik twee kwaliteitslagen:

```text
interactive / realtime
= lage latency, dynamisch, directe feedback

cinematic / final
= hogere samples/kwaliteit, betere motion blur, anti-aliasing,
  ray/path tracing waar beschikbaar, render passes en post-processing
```

Het world model blijft voor beide gelijk; alleen render-profiel verandert.

## Scene interchange

OpenUSD is de voorkeursvorm voor een engine-onafhankelijke scene-laag wanneer de gekozen engines dit ondersteunen.

Principes:
- stage = gecomposeerde wereld
- prim = scene-object
- layer = afzonderlijke authoring/opinion laag
- references/payloads = hergebruik en lazy loading
- variants = alternatieve uitvoeringen zonder object-identiteit te veranderen
- schemas = gestandaardiseerde betekenis voor geometry/camera/light/material/etc.

Gebruik geen geflatte scene als authoring-hoofdbron tenzij export vereist is; compositie en provenance gaan dan verloren.

## Materiaalstrategie

Intern materiaalmodel:

```text
base_color
metallic
roughness
normal
occlusion
emissive
opacity
ior
clearcoat
sheen
subsurface
transmission
custom_graph optional
```

MaterialX is voorkeur voor renderer-onafhankelijke graph-based look-development. Engine-adapters mogen dit compileren/mapppen naar engine-eigen shaders/materials.

## Physicsstrategie

Physics is stateful en tijdsafhankelijk. Houd simulation state apart van artistieke scene state.

```text
scene entity
  ├── visual transform
  └── physics component
       ├── body type
       ├── shapes/colliders
       ├── mass/inertia
       ├── material
       ├── velocity
       ├── constraints
       └── simulation flags
```

Na een physics-step is de engine authoritative voor gesimuleerde transforms. Synchroniseer deze terug naar het world model.

## Cinematic bouwstenen

Iedere shot-definitie bevat minimaal:

```text
shot_id
camera
lens/focal length
sensor/aperture/exposure
camera transform / path
focus target / distance
frame rate
duration
lighting state
animation state
effects state
color/post profile
render profile
```

## AI → visuele wereld

AI genereert nooit direct engine-specifieke willekeurige code als primaire route. Eerst een declaratief plan:

```text
Intent
→ ShotPlan / WorldPlan
→ validated EngineCommands
→ adapter
→ engine
```

Daarmee kunnen we dezelfde AI-logica later met een andere engine gebruiken.

## Security

- echte API keys alleen in secret manager/Railway
- externe engine control nooit onbeveiligd publiek exposen
- allowlist van toegestane operations
- path traversal blokkeren bij assets
- bestandsgrootte/type valideren
- command payloads schema-valideren
- remote engine endpoints achter auth/VPN/private network waar mogelijk
- geen raw engine errors naar eindgebruiker
- nooit automatisch willekeurige scripts uitvoeren die uit model-output komen

## Observability

Per operation meten:

```text
command_id
world_id
engine
operation
success/failure
queue latency
engine latency
total latency
world version
GPU/CPU mode indien relevant
render profile
error_code
```

## Bouwvolgorde nieuw product

```text
1. Kies use-case en engine.
2. Definieer World Model + command schemas.
3. Bouw één minimal engine adapter + healthcheck.
4. Maak entity/camera/light create-update-delete werkend.
5. Voeg material mapping toe.
6. Voeg world-state readback toe.
7. Voeg realtime events toe.
8. Voeg physics toe.
9. Voeg cinematic shot/sequencer-laag toe.
10. Voeg high-quality render path toe.
11. Voeg AI planning/orchestration toe.
12. Voeg style profiles toe.
13. Test deterministische recovery en errors.
14. Pas daarna capabilities uitbreiden.
```

## Definition of Ready

Een nieuwe engine is pas geïntegreerd als wij zonder handmatig editorwerk minstens kunnen:

```text
connect
scene/world openen
object maken
transform aanpassen
materiaal zetten
licht zetten
camera zetten
state uitlezen
preview/render starten
errors veilig ontvangen
```

Voor cinematic-ready komt daar bij:

```text
sequence/timeline besturen
camera/lens/focus animeren
lights/effects animeren
final render job starten
render-status/resultaat ophalen
```
