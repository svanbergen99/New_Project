# Voice

Deze map is de vaste werkmap voor alles wat nodig is voor **Voice** binnen het KCD-project.

## Vaste keten

Voice input → Voice Collector → beveiliging/codering → Voice Opslag → verwerking → antwoord/output.

## Wat hier onder Voice valt

- Voice input en audiostreams
- Voice Collector
- beveiliging, IDs/codes en metadata vóór opslag
- Voice Opslag
- STT / speech-to-text
- TTS / text-to-speech
- realtime/streaming voice
- conversation- en session-koppeling
- foutregistratie en feedback voor Voice
- koppeling met de Voice Engine
- checks voor latency, bereikbaarheid en veilige fallbacks

## Regels

- Opslag bewaart de definitieve data.
- Collectors halen data op, controleren die en beveiligen/coderen die vóór opslag.
- Geen secrets, tokens of wachtwoorden in deze repository opslaan.
- Voice-onderdelen blijven in deze map; Tekst blijft apart in `../Tekst/`.
