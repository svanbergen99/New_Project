# Video-to-Foley / Sound Design — Standalone Research Knowledge

Snapshot: 2026-09.

Bronfamilie: HunyuanVideo-Foley als researchreferentie voor video- en tekstgestuurde sound-effectgeneratie.

## Belangrijke licentiegrens

De huidige Tencent HunyuanVideo-Foley Community License sluit de Europese Unie, het Verenigd Koninkrijk en Zuid-Korea expliciet uit. Vanuit Nederland gebruiken we dit model daarom niet als directe KCD-dependency onder de huidige licentie.

Deze module bewaart alleen algemene architectuur- en workflowkennis. Geen Tencent-code, weights, checkpoints of credentials.

## Kernprobleem

Van een stille of incompleet gemixte video automatisch een geluidsspoor maken dat:

```text
semantisch klopt met wat zichtbaar is
+ temporeel synchroon loopt
+ ruimte en intensiteit volgt
+ niet botst met dialoog/voice
```

## Canonical input

```text
video_path
scene_description optional
shot_metadata optional
voice_track optional
music_track optional
desired_sound_profile
sample_rate target
```

## Canonical output

```text
foley_track
optional stems[]
event_timeline[]
confidence/warnings
sample_rate
loudness metadata
```

## Architectuurpatroon

```text
video frames ──→ visual encoder ─┐
                                 ├→ multimodal fusion → audio latent generation → audio decoder
scene text ────→ text encoder ───┤
                                 │
time position / sync features ───┘
```

Een bruikbare engine moet zowel **wat** er gebeurt als **wanneer** het gebeurt modelleren.

## Twee niveaus van timing

### Semantische timing
Voorbeeld:

```text
wave hits beach → wave sound
bird crosses frame → wing / call sound
object lands → impact sound
```

### Microtiming
Voor realisme moet de transient dichtbij het visuele contactmoment vallen. Daarom moet de pipeline frame-/event-level timing bewaren en niet alleen één audioclip per scène genereren.

## Event abstraction

KCD bewaart een neutrale eventlaag:

```text
SoundEvent
  id
  start_time
  end_time optional
  class
  intensity
  position optional
  distance optional
  material optional
  environment optional
  priority
  duck_under_dialogue bool
```

Voorbeelden:

```text
ocean_wave
footstep_sand
palm_rustle
gull_call
UI_whoosh
robot_servo
notification_chime
```

## Stemmen en Foley scheiden

Voice is geen Foley.

```text
KC-Dee Voice Engine  → dialogue stem
Foley engine         → physical / environmental sounds
Music engine         → score
Mixer                → final soundtrack
```

Zo kunnen we voice altijd verstaanbaar houden en de rest eromheen bouwen.

## Mixprioriteit

```text
1. dialogue intelligibility
2. story-critical sound events
3. ambience
4. music
5. decorative effects
```

Voor dialoogmomenten:
- ambience licht ducking
- harde effecten vermijden rond consonants/woorden
- music sidechain/ducking indien nodig

## 48 kHz lesson

De onderzochte Foley-referentie richt zich op 48 kHz output, wat goed aansluit bij standaard video/postproductie. Voor KCD gebruiken we 48 kHz als voorkeursmaster wanneer alle stages het ondersteunen.

## Scene sound layers

```text
BED
- wind
- sea
- room tone

EVENTS
- footsteps
- impacts
- UI interactions

CHARACTER
- servo
- cloth/body movement
- breath-like synthetic detail if stylistically wanted

TRANSITIONS
- whoosh
- riser
- impact
```

## Canonical FoleyAdapter

```text
capabilities()
analyze_video(video)
detect_sound_events(video, optional_text)
generate_foley(video, events, profile)
generate_ambience(scene, duration)
render_stems(events)
validate_sync(video, audio)
```

## Automatic QC

```text
no unexpected silence
no clipping
no extreme loudness jumps
transients near expected visual event
voice remains intelligible
no audible loop seam
no hallucinated dominant sound without visible/story cause
correct duration
correct sample rate
```

## KCD vacation-video use

```text
final picture lock
 ↓
visual event extraction
 ↓
foley events
  ocean
  breeze
  birds
  KC-Dee movement
  UI transitions
 ↓
generated/curated sound layers
 ↓
voice + music ducking
 ↓
48 kHz master mix
 ↓
FFmpeg mux
```

## Niet opslaan

- Tencent source code
- Tencent modelweights
- credentials/API keys
- copyrighted audio samples

## Kernles

Een goede AI-videopipeline moet sound design behandelen als een **tijdlijn van semantische events**, niet als een willekeurige ambiance-track. Daardoor kunnen latere engines worden vervangen zonder dat de KCD soundtracklogica verandert.
