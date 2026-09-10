# ComfyUI — Standalone Offline Orchestration Knowledge

Snapshot: 2026-09.

Doel: ComfyUI gebruiken als lokale/modulaire workflow-engine voor image, video, audio en 3D zonder dat KCD afhankelijk wordt van een cloud-API of secrets.

## Licentie / offline status

- ComfyUI core is GPLv3.
- De core kan volledig lokaal/offline draaien.
- Optionele API/partner nodes kunnen externe diensten gebruiken; voor een strikt offline profiel moeten die worden uitgeschakeld/niet gebruikt.
- De licenties van losse modellen en custom nodes moeten afzonderlijk worden gecontroleerd.

## Kernarchitectuur

ComfyUI is in essentie een uitvoerbare DAG/node graph.

```text
workflow JSON
   ↓
node graph
   ↓
queue
   ↓
node execution
   ↓
partial cache / selective re-execution
   ↓
media outputs
```

Sterk punt: elke stap kan apart worden vervangen, herhaald of gecachet zonder de hele pipeline opnieuw uit te voeren.

## Workflow als data

Voor KCD bewaren we workflows als versioned JSON-assets en niet als handmatig ingestelde UI-status.

Canonical metadata:

```text
workflow_id
version
purpose
required_models[]
required_custom_nodes[]
inputs schema
outputs schema
quality_profile
seed_policy
license_notes
```

## Lokale API-pattern

Een headless KCD-worker kan ComfyUI lokaal aanroepen via HTTP + WebSocket.

Belangrijke patronen uit de officiële API-example:

```text
POST /prompt
  → queue workflow JSON with client_id/prompt_id

WS /ws?clientId=<id>
  → execution progress/events
  → completion when execution finishes

GET /history/<prompt_id>
  → output metadata

GET /view?... 
  → retrieve generated media
```

KCD-regel: de ComfyUI-server blijft intern/private; alleen onze eigen adapter praat ermee.

## KCD ComfyAdapter

```text
capabilities()
submit_workflow(workflow_id, inputs)
wait_for_completion(job_id)
stream_progress(job_id)
get_outputs(job_id)
cancel(job_id)
validate_dependencies(workflow_id)
```

## Input substitution

Een workflow-template bevat vaste nodeverbindingen. KCD verandert alleen toegestane velden:

```text
prompt
negative prompt
seed
resolution
frames
fps
reference image/video/audio
quality parameters
output name
```

Geen willekeurige client mag arbitrary nodes of filesystem paths injecteren.

## Reproducibility

Altijd opslaan:

```text
workflow version
model identifiers
custom-node versions
seed
input hashes
important sampler/settings
output hashes
```

Daarmee kan een succesvolle generation later opnieuw worden gemaakt.

## Cache-principe

ComfyUI kan delen van de graph opnieuw gebruiken wanneer inputs upstream niet veranderen.

KCD benut dit expliciet:

```text
identity/reference preprocessing  → cache
text embeddings                  → cache indien prompt gelijk
3D asset                         → cache per asset/version
final render                     → alleen opnieuw bij gewijzigde shotinput
```

## VRAM/RAM strategie

ComfyUI ondersteunt slimme model loading/offloading en quantized modellen. Onze scheduler moet daarom per workflow weten:

```text
estimated_vram
estimated_ram
model_load_cost
supports_offload
supports_quantized
expected_runtime
```

Nooit twee zware modellen tegelijk laden als één GPU daardoor gaat OOM'en; queue ze of split workers.

## Offline production profile

```text
ComfyUI core
+ lokaal opgeslagen modellen
+ alleen goedgekeurde custom nodes
+ --disable-api-nodes
+ geen partner/cloud nodes
+ intern netwerk
+ immutable workflow versions
```

Hierdoor zijn geen API-keys nodig tijdens generatie.

## Security

```text
geen publieke ComfyUI admin/UI endpoint
geen arbitrary file path vanuit gebruikersinput
geen arbitrary custom-node install vanuit runtime
allowlist workflow IDs
allowlist model IDs
outputdirectory isoleren
job size/duration limieten
sanitize filenames
```

Custom nodes zijn uitvoerbare code en moeten dus hetzelfde security-reviewniveau krijgen als dependencies.

## Model router

ComfyUI zelf is niet het model; het orkestreert modellen.

```text
KCD intent
 ↓
WorkflowRouter
 ├─ image generation workflow
 ├─ image→video workflow
 ├─ avatar workflow
 ├─ depth/segmentation workflow
 ├─ upscaling workflow
 ├─ 3D generation workflow
 └─ audio workflow
 ↓
ComfyUI worker
```

## Video pipeline use

```text
script / storyboard
 ↓
reference generation
 ↓
video generation nodes
 ↓
frame interpolation / upscale
 ↓
artifact output
 ↓
KCD Video service FFprobe/QC
 ↓
Remotion/FFmpeg final edit
```

## Output contract

```text
job_id
workflow_id
status
progress
outputs[]
output_type
seed
runtime_ms
model_metadata
warnings[]
```

## Niet opslaan

- external API keys
- partner service credentials
- user account cookies
- model weights in Git
- unreviewed custom-node source copies

## Kernles

ComfyUI is voor KCD vooral een **offline visual-compute orchestrator**. Het laat ons verschillende lokale AI-modellen via één workflowcontract gebruiken, terwijl onze eigen KCD-engine verantwoordelijk blijft voor planning, security, queueing, storage en QC.
