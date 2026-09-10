# LTX-2.x / LTX-2.5 — Standalone Audio-Video Generation Knowledge

Snapshot: 2026-09.

Doel: de bruikbare architectuur- en pipelinekennis bewaren voor een eigen KCD video-engine zonder API-keys, accountdata of externe secrets in deze knowledge core op te slaan.

## Juridische / toegangstatus

- LTX-2.5 valt onder de LTX-2.x Community License.
- De licentie is wereldwijd maar kent aanvullende commerciële voorwaarden voor grotere organisaties; entities met >= $10M jaarlijkse omzet hebben voor commercieel gebruik een betaalde licentie nodig.
- Modelbestanden kunnen via Hugging Face aanvullende toegang/terms vereisen. Daarom bewaren wij hier GEEN modelweights, tokens of login-informatie.
- De kennis hieronder is zelfstandig bruikbaar voor ontwerp en adapterbouw; daadwerkelijke modelacquisitie blijft een aparte deploymentstap.

## Kernarchitectuur

LTX-2.x behandelt video en audio als gekoppelde generatieve modaliteiten.

Canonical mental model:

```text
prompt / reference image / reference video / audio
                  ↓
          text encoder + conditioners
                  ↓
      joint audio-video diffusion transformer
          ↙                         ↘
     video latent                 audio latent
          ↓                         ↓
      video VAE                   audio VAE
          ↓                         ↓
      frames/video           waveform / audio
                  ↓
             final mux
```

Belangrijk principe: audio hoeft niet pas achteraf te worden toegevoegd. Het model kan audio en video gezamenlijk conditioneren/genereren, waardoor timing tussen beeld en geluid onderdeel van de generatieve stap kan zijn.

## Bruikbare pipelinefamilies

### Distilled
Snelste algemene inferencepad. Goed voor previews, bulk-renders en iteraties.

### DFR — Diffusion Fidelity Rendering
Productiepad voor hogere kwaliteit.

```text
stage 1: half-resolution generatie + keyframe slots + audio
stage 2: spatial upscale + detailing LoRA + re-denoise video
optional: temporal densification
```

Audio komt primair uit stage 1; latere detaillering verbetert vooral het beeld.

### Image / video conditioning
- image-to-video
- video-to-video via IC-LoRA
- keyframe interpolation
- referentieframes op specifieke tijdposities

### Audio-to-video
Bestaande audio wordt als vaste condition gebruikt terwijl beeld eromheen wordt gegenereerd. Dit is interessant voor KC-Dee wanneer de echte Voice Engine eerst de definitieve voice levert.

### Retake
Alleen een gekozen tijdssegment opnieuw genereren terwijl de rest behouden blijft. Dit is ideaal voor automatische kwaliteitscorrectie in onze Video pipeline.

### Dub / lip-match pattern
Een referentieclip levert identity/motioncontext; nieuwe audio kan aan nieuwe lipbewegingen worden gekoppeld. Conceptueel bruikbaar voor character dubbing.

### HDR
Er zijn paden voor lineaire HDR/EXR-output en latere eigen tone mapping/color grading.

## Belangrijke technische constraints

- Veel pipelines gebruiken een temporeel raster van `8k + 1` frames.
- DFR-outputafmetingen moeten op vaste grids vallen; gangbaar is veelvoud van 64.
- Temporal upscaling verhoogt het aantal frames en playback-fps zonder de wall-clock duur te verlengen.
- Spatial upscaling en detailing kosten extra VRAM/tijd.
- FP8/quantization en CPU/disk offload zijn relevante memory-strategieën.

## KCD adaptercontract

```text
VideoGenRequest
  prompt
  negative_prompt optional
  reference_images[] optional
  reference_video optional
  reference_audio optional
  width
  height
  fps
  duration
  seed
  quality_profile: preview|final
  preserve_audio bool
  retake_range optional
  hdr bool

VideoGenResult
  video_path
  audio_path optional
  muxed_output_path
  width
  height
  fps
  duration
  seed
  model_profile
  generation_metadata
```

Adaptermethoden:

```text
capabilities()
generate_preview(request)
generate_final(request)
image_to_video(request)
audio_to_video(request)
retake(request, start, end)
interpolate_keyframes(request)
render_hdr(request)
```

## Beste KCD-flow

```text
script
 ↓
KC-Dee Voice Engine → definitieve voice.wav
 ↓
shot planner → keyframes / reference images
 ↓
LTX-style AudioToVideo of DFR generation
 ↓
automatic QC
 ↓
retake alleen slechte segmenten
 ↓
Remotion/FFmpeg final composition
 ↓
Video bucket
```

## Quality strategy

```text
PREVIEW
- distilled
- lagere resolutie
- korte clips
- minimale steps

FINAL
- DFR/detailing
- spatial upscale
- indien nodig temporal upscale
- HDR/EXR wanneer color pipeline dit ondersteunt
- QC op motion, identity, audio sync en artifacts
```

## Wat we NIET opslaan

- modelweights
- Hugging Face tokens
- API keys
- account credentials
- vendor cookies
- copyrighted demo-assets

## Kernles

Voor KCD is LTX vooral waardevol als een `AudioVideoGeneratorAdapter`: eerst onze eigen KC-Dee stem vastleggen, daarna video er strak omheen genereren, en slechte segmenten lokaal retaken in plaats van de hele film opnieuw maken.
