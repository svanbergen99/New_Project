# Tekst

Deze map is de vaste werkmap voor alles wat nodig is voor **Tekst** binnen het KCD-project.

## Vaste keten

Tekst input → Tekst Collector → beveiliging/codering → Tekst Opslag → verwerking → antwoord/output.

## Wat hier onder Tekst valt

- tekstinput uit chat/API
- Tekst Collector
- beveiliging, IDs/codes en metadata vóór opslag
- Tekst Opslag
- normalisatie en verwerking van tekst
- conversation- en session-koppeling
- foutregistratie en feedback voor Tekst
- retrieval/memory-koppelingen voor goedgekeurde kennis
- koppeling met de tekst/AI-engine
- checks voor veilige opslag, correcte routing en fallbacks

## Regels

- Opslag bewaart de definitieve data.
- Collectors halen data op, controleren die en beveiligen/coderen die vóór opslag.
- Geen secrets, tokens of wachtwoorden in deze repository opslaan.
- Tekst-onderdelen blijven in deze map; Voice blijft apart in `../Voice/`.
