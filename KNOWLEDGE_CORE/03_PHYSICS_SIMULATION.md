# Physics + Simulation — Standalone Knowledge

Snapshot: 2026-09.

Doel: herbruikbare physicsarchitectuur gebaseerd op PhysX- en Warp-principes, zonder afhankelijk te zijn van hun broncode.

## Physics world

Canonical world config:

```text
gravity
fixed_dt
substeps
solver iterations
broadphase mode
CPU/GPU mode
collision layers/masks
scene bounds optional
continuous collision flags
sleep thresholds
```

Gebruik voor gameplay/realtime bij voorkeur een fixed timestep. Rendering mag interpoleren tussen physics states.

## Body model

```text
PhysicsBody
  id
  type: static|dynamic|kinematic
  transform
  linear_velocity
  angular_velocity
  mass
  center_of_mass
  inertia
  damping
  gravity_enabled
  continuous_collision
  sleep state
  shapes[]
```

### Static
Beweegt niet door simulation; geschikt voor world geometry.

### Dynamic
Volledig door physics bestuurd.

### Kinematic
Transform wordt door applicatie/animatie bestuurd maar kan interactie veroorzaken. Gebruik dit niet als goedkope dynamic-body-vervanger wanneer fysieke reactie nodig is.

## Shapes / colliders

Canonical shapes:

```text
box
sphere
capsule
convex
triangle mesh
heightfield
SDF indien engine ondersteunt
```

Per shape:

```text
local transform
geometry parameters
physics material
collision group/mask
trigger flag
contact offset
rest offset
```

Regels:
- complexe triangle meshes liever static dan dynamic;
- dynamische objecten waar mogelijk convex/primitive colliders;
- collider hoeft niet exact render mesh te zijn;
- schaal/conversie expliciet valideren.

## Physics materials

```text
static_friction
dynamic_friction
restitution
combine modes indien engine ondersteunt
```

Houd physics material gescheiden van visueel material.

## Dynamics

Dynamic state:

```text
position/orientation
linear velocity
angular velocity
forces/torques
mass/inertia
constraints/contact response
```

Applicatie kan impulses/forces geven, maar moet na simulation de engine-state als authoritative behandelen.

## Constraints / joints

Canonical:

```text
fixed
hinge/revolute
prismatic
spherical
D6/general
```

Per constraint:

```text
body A/B
local frames
limits
drives/motors
break thresholds
collision between connected bodies
```

## Simulation step

```text
input commands
↓
apply forces/kinematic targets
↓
broadphase
↓
narrowphase/contact generation
↓
constraint solve
↓
integrate
↓
sleep/wake
↓
events
↓
state readback
```

Bij GPU simulation kunnen broadphase, contact generation, body management en solver versneld worden. GPU mode is een scene-configuratiekeuze en moet capability-checked worden.

## Events

Normaliseer physics events:

```text
contact_begin
contact_persist
contact_end
trigger_enter
trigger_exit
constraint_break
wake
sleep
advance/state
```

Iedere event:

```json
{
  "event_id": "uuid",
  "world_id": "world",
  "type": "contact_begin",
  "a": "entity-a",
  "b": "entity-b",
  "point": [0,0,0],
  "normal": [0,1,0],
  "impulse": 0.0,
  "sim_time": 0.0
}
```

Niet alle engines leveren elk veld; adapter vult alleen betrouwbare data.

## Filters

Gebruik collision matrix/layers, bijvoorbeeld:

```text
World
Character
Vehicle
Projectile
Trigger
FX
Debris
```

Filter vroeg. Onnodige collision pairs kosten veel performance.

## Character / vehicles

Character movement en voertuigen zijn gespecialiseerde systemen bovenop rigid-body collision/dynamics. Houd ze als aparte capability in adapter, niet als generieke body flags.

## Soft bodies / particles / fluids

Behandel als aanvullende simulation domains:

```text
soft body / FEM
cloth
aero/particles
PBD particles
fluid/smoke/fire
```

Data kan orders groter zijn dan rigid-body state. Stream daarom events/summaries naar AI, niet elke particle per frame.

## Warp-achtig compute model

Voor custom GPU-simulation houden we dit patroon aan:

```text
Python host/orchestrator
↓
typed device arrays
↓
JIT compiled parallel kernel
↓
CPU/CUDA device
↓
synchronization/readback alleen waar nodig
```

Canonical custom kernel interface:

```text
kernel_name
input arrays
output arrays
dimensions/device
constants
launch
sync policy
```

Gebruik GPU kernels voor zeer parallel werk:
- particles
- mesh queries
- procedural deformation
- spatial transforms
- optimization
- custom simulation

Gebruik ze niet voor kleine control-flow-heavy taken waar launch/sync overhead domineert.

## Geometry queries

Ondersteun engine-onafhankelijk:

```text
raycast
sweep
shape overlap
closest point
mesh query
scene query
```

Query result:

```text
hit
entity_id
position
normal
distance
face/index optional
material/tag optional
```

## AI en physics

AI krijgt geen raw full simulation dump. Maak semantic state:

```text
"crate is falling"
"hero touching ground"
"vehicle speed 18 m/s"
"door joint at 72% open"
```

Pipeline:

```text
physics state/events
↓
semantic reducer
↓
WorldEvent / WorldState
↓
AI
↓
high-level action
↓
validated physics commands
```

## Determinisme en replay

Voor reproduceerbare acties opslaan:

```text
initial state/checkpoint
fixed dt
engine/version
random seeds
input commands ordered by tick
configuration
```

Exact bitwise determinisme tussen CPU/GPU/hardware of verschillende engineversies niet aannemen. Gebruik replay vooral functioneel en test toleranties.

## State synchronization

Per physics tick niet alles naar database schrijven.

```text
runtime simulation
→ memory
→ selected events
→ periodic checkpoints
→ final state / significant state changes
```

## Performance

- fixed timestep budget bewaken
- object sleeping gebruiken
- collision filtering
- eenvoudige colliders
- batch queries
- minimale CPU↔GPU readbacks
- object pooling voor veel tijdelijke bodies/effects
- avoid create/destroy per frame
- profile broadphase, solver, contact count en GPU transfers apart

## Stability checks

```text
invalid mass/inertia
extreme scale mismatch
NaN transform/velocity
penetration explosion
constraint divergence
unbounded velocity
unsupported GPU shape
excessive substeps
simulation falling behind realtime
```

## Physics Adapter API

```text
create_scene(config)
create_body(entity_id, body_desc)
update_body(entity_id, changes)
delete_body(entity_id)
add_force(entity_id, force, mode)
set_kinematic_target(entity_id, transform)
create_constraint(desc)
delete_constraint(id)
raycast(query)
overlap(query)
step(dt)
get_body_state(id)
get_events(since_tick)
checkpoint()
restore(checkpoint)
```

## Fouten die we voorkomen

```text
geen variable-dt chaos zonder substep policy
geen render-mesh automatisch als dynamic collider
geen physics material verwarren met visual material
geen AI die per-frame transforms blind overschrijft op dynamic bodies
geen volledige particle-state naar LLM sturen
geen CPU/GPU determinisme aannemen
geen GPU mode activeren zonder capability/fallback
```
