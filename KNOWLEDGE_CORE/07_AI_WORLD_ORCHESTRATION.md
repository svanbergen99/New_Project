# AI World Orchestration — Standalone Knowledge

Snapshot: 2026-09.

Doel: de laag definiëren waarmee een AI zelfstandig een realtime 3D/cinematic wereld kan plannen, wijzigen, observeren en corrigeren zonder direct engine-specifieke code te produceren.

## Hoofdregel

LLM-output is intent, geen trusted executable code.

```text
natural language intent
↓
structured plan
↓
schema validation
↓
policy/capability validation
↓
commands
↓
engine adapter
↓
readback/events
↓
AI evaluation
```

## World Model

Canonical state:

```text
World
  world_id
  version
  time
  entities{}
  cameras{}
  lights{}
  shots{}
  environment
  physics state summary
  active style profile
  active render profile
```

Entity:

```text
entity_id
asset_id optional
name/tags
transform
visual/material state
animation state
physics state summary
parent/children
semantic role
importance
```

## Semantic roles

AI reasoning wordt beter als de wereld niet alleen objectnamen bevat.

Voorbeelden:

```text
hero_character
supporting_character
primary_prop
background_prop
interactive_object
key_light
practical_light
main_camera
fx_emitter
navigation_obstacle
```

## Intent schema

User kan bijvoorbeeld zeggen:

```text
"Maak deze steeg donkerder en spannender en laat de camera langzaam naar het personage bewegen."
```

Intent parser produceert:

```json
{
  "goal": "increase_tension",
  "scope": "current_shot",
  "constraints": {
    "preserve_character_position": true,
    "style": "cinematic_realism"
  },
  "requested_changes": [
    "lighting",
    "atmosphere",
    "camera_motion"
  ]
}
```

Nog geen engine commands.

## Planning

Planner maakt vervolgens een plan:

```text
1. inspect current shot/world
2. reduce fill exposure
3. cool environment slightly
4. add/widen motivated rim light
5. increase atmospheric depth subtly
6. create slow camera dolly-in
7. preserve focus on hero
8. preview
9. evaluate image/state
10. revise if needed
```

## Command generation

Plan wordt vertaald naar typed operations:

```text
set_light
create_light
set_camera
add_camera_key
set_effect
set_material_parameter
play_animation
set_variant
spawn_entity
remove_entity
apply_force
render_preview
```

Elke command moet vooraf bestaan in onze allowlist/schema registry.

## Capability resolution

Voor command dispatch:

```text
required capability
↓
engine.get_capabilities()
↓
supported?
  yes → execute
  no  → equivalent/fallback?
          yes → adapted plan
          no  → capability error
```

AI mag niet hallucineren dat een target feature beschikbaar is.

## Transaction model

Een multi-command scene edit wordt als transaction behandeld.

```text
begin transaction
→ verify world_version
→ checkpoint
→ commands
→ readback validation
→ commit
```

Bij cruciale fout:

```text
rollback / restore checkpoint
```

Niet elke realtime actie vereist volledige rollback; command type bepaalt transactional policy.

## World versioning

Iedere committed structural wijziging verhoogt world version.

Command bevat `expected_version`.

Als world in tussentijd veranderde:

```text
VERSION_CONFLICT
→ read latest state
→ replan
```

Geen blind last-write-wins voor AI scene authoring.

## Observation

AI hoeft niet iedere raw engineproperty te zien.

Observation reducer maakt compacte semantic state:

```text
hero visible: yes
hero screen coverage: 18%
key/fill contrast: high
camera distance: 4.2 m
focus target: hero
brightest competing object: neon sign
physics alert: none
shot continuity warnings: 1
```

Voor visuele beoordeling kunnen daarnaast preview frames/images naar een vision-capable evaluator.

## Perception loop

```text
world state + preview
↓
evaluator
↓
quality findings
↓
correction plan
↓
commands
↓
new preview
```

Stopcondities:

```text
quality target reached
max iterations
no meaningful improvement
budget exhausted
unsafe/unsupported command
user interruption
```

## Quality scores

Gebruik meerdere assen, niet één subjectief cijfer:

```text
composition
subject readability
lighting coherence
material coherence
style consistency
depth/atmosphere
animation quality
continuity
technical artifacts
performance budget
```

## Cinematic continuity

Tussen shots bewaren:

```text
character screen direction
light direction/temperature continuity
wardrobe/asset variants
world time/weather
prop state
character pose/action state
camera grammar
color script
```

AI krijgt continuity state bij nieuw shot.

## Director roles

Verdeel complexe AI-output intern in rollen zonder aparte modellen verplicht te maken:

```text
World Director
  beslist narrative/world changes

Cinematography Director
  camera/composition/lens

Lighting Director
  lights/exposure/atmosphere

Lookdev Director
  materials/style/color

Animation Director
  blocking/character/FX timing

Technical Supervisor
  capabilities/performance/errors
```

Orchestrator resolveert conflicten volgens user goal + technical constraints.

## Budget system

Iedere operation kan cost hints hebben:

```text
latency_cost
gpu_cost
memory_cost
render_cost
asset_download_cost
```

AI-plan krijgt een budget:

```text
interactive: prioritize < frame/realtime limits
preview: seconds acceptable
final: quality prioritized within explicit time/cost ceiling
```

## Realtime control

Voor runtime actions:

```text
AI decision rate != render frame rate
```

AI stuurt high-level targets/events, engine interpoleert/simuleert op frame/tick rate.

Voorbeeld:

```text
AI: move character to marker B over 2.4 sec
engine: honderden animation/physics/render frames
```

Nooit LLM per frame laten micromanagen.

## NPC/world intelligence

NPC loop:

```text
perception summary
↓
state/goals
↓
action selection
↓
validated gameplay action
↓
engine
↓
events/result
```

Houd navigation, animation blending, IK en physics lokaal in game engine; AI bepaalt intentionele acties.

## Events

Event bus categories:

```text
world
interaction
physics
animation
cinematic
render
system/error
user
```

Event envelope:

```text
event_id
world_id
world_version
source
category/type
entity_ids
payload
timestamp/correlation_id
```

## Memory

Bewaar alleen betekenisvolle persistente facts, niet ieder frame:

```text
world facts
character relationships/state
important user choices
approved style rules
asset provenance
shot history
persistent object state
```

Ephemeral runtime state blijft runtime/checkpoint data.

## Safety / command boundaries

Niet toegestaan vanuit vrije model-output:

```text
shell execution
arbitrary Python eval
arbitrary C++ compilation
filesystem deletion
plugin installation
download+execute unknown binary
unbounded network request
secret access
```

Daarvoor bestaan expliciete trusted tools/workflows met aparte goedkeuring/policy.

## Self-repair

Bij failure:

```text
1. classify error
2. determine retryable
3. retry met bounded policy indien transient
4. target fallback indien equivalent
5. rollback indien partial mutation unsafe
6. collect diagnostic metadata
7. generate revised plan
```

Nooit infinite retry loops.

## AI-ready Definition

Een engine wordt pas autonoom aangestuurd als:

```text
state readback betrouwbaar is
commands typed/validated zijn
capability discovery werkt
transactions/versioning werken
errors normalized zijn
preview/evaluation loop werkt
stopconditions bestaan
manual intervention mogelijk blijft
```
