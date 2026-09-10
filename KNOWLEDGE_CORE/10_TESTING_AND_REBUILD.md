# Testing + Rebuild Playbook

Doel: vanaf lege infra gecontroleerd opnieuw bouwen en aantonen dat het systeem echt werkt voordat AI-autonomie wordt toegevoegd.

## Rebuild vanaf nul

```text
1. Maak nieuwe repo/service.
2. Kies engine target: Unreal, Omniverse of andere.
3. Leg engine/SDK version vast.
4. Maak canonical schemas uit 09_ENGINE_ADAPTER_CONTRACTS.
5. Bouw adapter skeleton + healthcheck.
6. Koppel secrets alleen via environment/secret manager.
7. Maak minimale test-world.
8. Implementeer create/read/update/delete entity.
9. Voeg camera en light toe.
10. Voeg material toe.
11. Voeg asset pipeline toe.
12. Voeg event/readback toe.
13. Voeg physics toe indien nodig.
14. Voeg cinematic timeline/shot control toe.
15. Voeg preview render toe.
16. Voeg final render toe.
17. Voeg AI orchestrator pas daarna toe.
18. Voeg self-evaluation/correction loop toe.
```

## Testworld

Iedere engine adapter moet dezelfde abstracte testscene kunnen maken:

```text
World
├── Floor
├── HeroCube / test hero mesh
├── DynamicSphere
├── KeyLight
├── FillLight
├── MainCamera
└── TestMaterial
```

Hiermee testen we geometry, transforms, material, light, camera en physics zonder complexe assets.

## Adapter contract tests

### Connection

```text
healthcheck returns connected
engine version known
mode known
capabilities non-empty
```

### Entity CRUD

```text
create entity
read it back
change transform
read changed transform
remove entity
confirm absent
```

### Material

```text
create/map PBR material
assign to entity
read/verify binding
change roughness/base color
verify engine accepted
```

### Camera

```text
create camera
set focal length
set transform
set focus distance if supported
render preview
```

### Lighting

```text
create key light
change intensity/color
verify scene changed/state accepted
```

### Physics

```text
create static floor
create dynamic sphere above floor
step simulation
sphere moves downward
contact event occurs
sphere settles or state remains stable
```

### Events

```text
subscribe
mutate entity
receive normalized event
correlation/world IDs correct
```

## Cinematic tests

```text
create 3-second shot
camera key at start/end
actor animation/transform key
light property key
render preview
verify expected frame range
```

Final render test:

```text
submit RenderJob
status queued/running/completed
output exists
output dimensions/frame count valid
no silent fallback from requested profile without warning
```

## Visual regression

Maak een kleine vaste set golden reference scenes, niet per se pixel-perfect tussen engines.

Meet:

```text
camera composition bounds
object visibility
average exposure/luminance ranges
color probes
silhouette occupancy
shadow presence
material response probes
frame dimensions
```

Voor dezelfde engine/version kan optioneel perceptual image diff worden gebruikt.

## Style validation

### Cinematic Immersion

Check:

```text
clear focal subject
intentional value grouping
foreground/midground/background separation
controlled palette
consistent stylization
atmospheric depth
camera/lens intent
no distracting material noise
```

### Cinematic Realism

Check:

```text
physical scale coherent
materials plausible
roughness/specular behavior coherent
lighting motivated
exposure plausible
lens/focus coherent
shadows/reflections stable
no obvious temporal/render artifacts
```

## Performance tests

Realtime profile meet:

```text
command latency
state readback latency
render frame time
GPU memory
CPU frame time
physics step time
event backlog
network/stream latency
```

Final profile meet:

```text
render startup time
seconds/frame
peak GPU memory
failure/retry rate
output size
```

Geen performance claim doen zonder concrete target hardware/profile.

## Failure injection

Test bewust:

```text
engine offline
engine restart tijdens command
invalid entity id
version conflict
unsupported capability
bad asset URI
missing texture
shader compile failure
GPU unavailable
render job failure
physics invalid values
WebSocket disconnect
timeout
rate limit indien externe API
```

Iedere fout moet:
- genormaliseerd worden;
- safe_message geven;
- retryable correct zetten;
- geen secret/raw stack naar client lekken;
- systeem in consistente state laten.

## Security tests

```text
unauthenticated remote command rejected
invalid schema rejected
path traversal rejected
unknown operation rejected
oversized payload rejected
secret values absent from logs
raw arbitrary Python/shell command impossible
engine Remote Control niet direct publiek bereikbaar
```

## Recovery test

```text
checkpoint world
perform batch edits
force failure halverwege
restore/reconcile
world consistent
world_version correct
retry command idempotent waar vereist
```

## AI autonomy gates

AI krijgt pas write access wanneer onderliggende adapter alle bovenstaande tests doorstaat.

Fase 1:
```text
AI read-only world understanding
```

Fase 2:
```text
AI generates plan, human/validator executes
```

Fase 3:
```text
AI executes allowlisted reversible edits
```

Fase 4:
```text
AI multi-step autonomous world/cinematic creation met budget/stopconditions
```

Nooit autonomie gebruiken als vervanging voor ontbrekende adaptervalidatie.

## Release checklist

```text
[ ] engine version pinned/known
[ ] dependency licenses recorded
[ ] secrets outside repo
[ ] health/capability endpoint green
[ ] CRUD tests green
[ ] materials/camera/light green
[ ] events/readback green
[ ] physics green indien gebruikt
[ ] cinematic sequence green indien gebruikt
[ ] preview render green
[ ] final render green indien gebruikt
[ ] failure injection green
[ ] security tests green
[ ] rollback/recovery green
[ ] observability live
[ ] user kill-switch/manual override aanwezig
```

## Wanneer externe docs opnieuw nodig zijn

Niet voor normaal ontwerp of opnieuw bouwen op basis van deze snapshot.

Wel voor compatibility wanneer:

```text
engine major version verandert
API method/plugin in runtime ontbreekt
official license terms veranderen
nieuw render backend/hardware target gekozen wordt
security advisory actuele dependency raakt
```
