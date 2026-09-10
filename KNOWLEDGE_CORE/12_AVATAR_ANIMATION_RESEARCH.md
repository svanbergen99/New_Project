# Audio-Driven Avatar Animation — Standalone Research Knowledge

Snapshot: 2026-09.

Bronfamilie: HunyuanVideo-Avatar als researchreferentie voor high-fidelity audio-driven character animation.

## Belangrijke licentiegrens

De huidige Tencent HunyuanVideo-Avatar Community License sluit de Europese Unie, het Verenigd Koninkrijk en Zuid-Korea expliciet uit. Voor een KCD-deployment vanuit Nederland behandelen we dit model daarom NIET als een inzetbare dependency onder de huidige licentie.

Deze module bewaart uitsluitend algemene architectuur- en ontwerpkennis. Geen Tencent-code, modelweights, checkpoints of credentials worden opgeslagen.

## Probleem dat een avatar-engine moet oplossen

Input:

```text
character reference image(s)
voice/audio
optional emotion reference
optional pose/motion guidance
scene/background context
```

Output:

```text
video with:
- stable character identity
- speech-synchronous mouth/face motion
- emotion aligned to audio
- plausible head/body motion
- stable foreground/background
```

## Drie nuttige architectuurpatronen

### 1. Strong character-image injection

Een avatarreferentie moet niet slechts als zwakke globale embedding worden toegevoegd. Character identity moet op meerdere relevante lagen/feature-resoluties beschikbaar blijven zodat het gezicht, silhouet en kenmerkende details niet per frame wegdriften.

KCD-regel:

```text
KC-Dee identity conditioning = persistent
scene/style conditioning      = variable
```

Dus scene, kledingaccessoires of achtergrond mogen veranderen zonder dat KC-Dee zelf van identiteit verandert.

### 2. Audio-emotion extraction

Niet alleen fonemen/mondbewegingen uit audio halen. Ook prosodie gebruiken:

```text
pitch
energy
speech rate
pauses
stress
emotion embedding
```

Daaruit kunnen worden afgeleid:

```text
eye expression
brow movement
mouth intensity
head movement
body emphasis
```

Voor KC-Dee kan onze bestaande emotion-tagging `[HAPPY]`, `[THINKING]`, enz. als extra expliciete condition worden gebruikt naast de stem.

### 3. Face-aware audio conditioning

Audio-informatie moet vooral de character-regio beïnvloeden die spreekt. Bij meerdere karakters moet per speaker duidelijk zijn welke face/character-mask de audio ontvangt.

Canonical multi-character mapping:

```text
speaker_id
→ audio track
→ character_id
→ face/body mask
→ animation condition
```

Dit voorkomt dat meerdere gezichten tegelijk dezelfde spraakbeweging krijgen.

## Canonical AvatarRequest

```text
character_id
reference_images[]
audio_path
emotion optional
style_profile
shot_type: portrait|upper_body|full_body
background_reference optional
motion_strength
identity_strength
expression_strength
seed
fps
duration
```

## Canonical AvatarResult

```text
video_path
character_id
identity_score optional
sync_score optional
emotion_score optional
fps
duration
seed
warnings[]
```

## Character consistency checks

Automatisch controleren:

```text
face/visor geometry drift
color drift
logo/marking drift
eye placement
mouth placement
silhouette consistency
unwanted limb/object creation
background bleed into character
frame-to-frame flicker
```

Voor KC-Dee is identity consistency belangrijker dan fotorealistische menselijke face fidelity.

## Audio sync checks

```text
speech onset ↔ mouth onset
pause ↔ mouth closure/idle
energy peak ↔ motion emphasis
emotion change ↔ facial/body response
speaker switch ↔ active character switch
```

## KCD pipelinepatroon

```text
KC-Dee script
 ↓
Voice Engine → final voice
 ↓
emotion/prosody analysis
 ↓
AvatarAdapter
  - identity reference
  - voice audio
  - emotion
  - shot design
 ↓
video segment
 ↓
identity + sync QC
 ↓
retake indien nodig
```

## Voor niet-menselijke chatbot-mascots

Een generiek avatar-model moet niet aannemen dat het onderwerp een menselijk gezicht heeft. Onze semantic face controls zijn daarom abstract:

```text
gaze
eye_open
eye_shape
brow_or_equivalent
mouth_open
mouth_shape
smile
head_yaw/pitch/roll
body_bob
emphasis
idle_motion
```

Een KC-Dee adapter vertaalt die controls naar visor/eyes/mond/body van zijn eigen ontwerp.

## EU-veilige implementatiestrategie

We bouwen dit als vendor-neutraal contract. Een later gekozen model/engine mag HunyuanVideo-Avatar functioneel vervangen zolang het:

```text
reference image + audio → identity-stable animated character
```

kan uitvoeren en een licentie heeft die KCD in Nederland/EU toestaat.

## Niet opslaan

- Tencent modelweights
- Tencent source code
- checkpoints
- login-/accountgegevens
- API keys

## Kernles

De belangrijkste innovatie voor KCD is niet een specifieke avatarvendor, maar de scheiding tussen **identity conditioning**, **audio/prosody conditioning**, **emotion conditioning** en **speaker-specific masks**. Dat ontwerp kan in elke toekomstige legale avatar-engine opnieuw worden toegepast.
