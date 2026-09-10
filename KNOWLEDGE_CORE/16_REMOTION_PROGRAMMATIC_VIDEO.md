# Remotion — Standalone Programmatic Video Composition Knowledge

Snapshot: 2026-09.

Doel: deterministische montage, motion graphics, captions, audio/video layering en reproduceerbare MP4-rendering voor KCD.

## Licentiegrens

Remotion gebruikt een eigen licentie.

Volgens de 2026 licentietekst is gratis gebruik toegestaan voor:
- individuen;
- for-profit organisaties met maximaal 3 medewerkers;
- non-profit / not-for-profit organisaties;
- evaluatie zonder commercieel productiegebruik.

Grotere for-profit organisaties hebben een company license nodig. Controleer de actuele voorwaarden vóór commerciële schaalvergroting.

## Kernidee

React/code is de bron van waarheid voor de video.

```text
props/data
 ↓
Composition
 ↓
frame number + fps
 ↓
deterministic React render
 ↓
frames + audio
 ↓
encoder
 ↓
MP4 / image sequence / other output
```

Dit maakt Remotion geschikt voor KCD omdat dezelfde inputs exact dezelfde layout/timing kunnen produceren.

## Belangrijke bouwstenen

```text
Composition
  id
  width
  height
  fps
  durationInFrames
  defaultProps

Timeline logic
  current frame
  interpolation
  sequences
  transitions

Media
  video
  audio
  images
  captions
  SVG/canvas/WebGL
```

## Server-side renderpatroon

De relevante Node-renderflow is conceptueel:

```text
bundle project
 ↓
select composition
 ↓
resolve props / duration
 ↓
render media
 ↓
write final output
```

In de officiële code worden hiervoor onder andere `bundle`, `selectComposition` en `renderMedia` gebruikt.

KCD kapselt dit in één adapter zodat onze rest van het systeem niet afhankelijk wordt van Remotion-specifieke API's.

## Canonical CompositionRequest

```text
composition_id
width
height
fps
duration_frames or duration_seconds
props
video_tracks[]
audio_tracks[]
caption_tracks[]
overlays[]
quality_profile
output_format
output_path
```

## Canonical VideoTrack

```text
source
start_frame
end_frame optional
trim_start
trim_end
volume optional
opacity optional
transform optional
z_index
```

## Canonical AudioTrack

```text
source
start_frame
trim_start
trim_end
volume
duck_group optional
fade_in_frames
fade_out_frames
```

## Shot-based KCD montage

```text
Shot 01 intro
Shot 02 beach wide
Shot 03 KC-Dee close-up
Shot 04 idea montage
Shot 05 KCD return reveal
```

Elke shot wordt een afzonderlijke sequence met een expliciete duur. Daardoor kunnen individuele shots later door AI opnieuw worden gegenereerd zonder de rest van de timeline te veranderen.

## Frame deterministic animation

Gebruik tijd niet vanuit `Date.now()` of willekeurige browser-timing. Alle animatie wordt afgeleid uit:

```text
frame
fps
seeded values
input props
```

Zo blijft preview/render consistent.

## Caption pipeline

```text
voice transcript
 ↓
word/segment timestamps
 ↓
caption track
 ↓
frame-ranged caption components
 ↓
final burn-in or selectable subtitle asset
```

Voor KC-Dee:
- captions nooit over gezicht/visor zetten;
- maximaal enkele woorden tegelijk bij korte teaserstijl;
- timing op voice, niet op generieke scene duration.

## Motion graphics

Remotion is vooral geschikt voor:

```text
KCD logo reveals
UI overlays
status cards
animated typography
lower thirds
progress meters
transitions
particle/canvas overlays
captions
end cards
```

Fotorealistische wereldgeneratie hoort bij een render/generative engine; Remotion monteert die outputs tot één gecontroleerde video.

## Audio mix

```text
voice
music
ambience
foley
UI SFX
```

Voor elke track bewaren we gain/fades en eventueel ducking-regels. De finale loudness/QC gebeurt daarna nog via FFmpeg/audio tooling.

## Batch rendering

Omdat de composition props data-driven zijn, kan KCD één template met veel verschillende inputs renderen:

```text
same composition
+ different script
+ different employee/event data
+ different KC-Dee emotion
→ unique video
```

## RendererAdapter

```text
capabilities()
validate_composition(id, props)
preview(id, props)
render(id, props, output)
render_frames(id, props, range)
cancel(job_id)
probe_output(path)
```

## KCD final assembly flow

```text
AI generated clips
+ KC-Dee voice
+ Foley
+ music
+ subtitles
+ KCD UI assets
        ↓
Remotion timeline
        ↓
render MP4
        ↓
FFprobe / Video QC
        ↓
final bucket
```

## Error-prevention rules

```text
no network-dependent asset without prefetch/caching
no unseeded randomness
no dynamic duration mismatch
no missing fonts/assets at render time
no uncontrolled autoplay assumptions
no render completion without media probe
```

## Niet opslaan

- license keys
- service credentials
- cloud render credentials
- third-party paid assets

## Kernles

Remotion is niet onze AI-video-generator. Het is de **deterministische editor/render-compositor** die losse AI-shots, voice, foley, captions en KCD graphics tot één reproduceerbare echte video maakt.
