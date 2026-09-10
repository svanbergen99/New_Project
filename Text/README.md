# Text

Deze map is de vaste werkmap voor alles wat nodig is voor **Text** binnen het KCD-project.

## Vaste keten

Text input → Text Collector → beveiliging/codering → Text Opslag → verwerking → antwoord/output.

## Wat hier onder Text valt

- tekstinput uit chat/API
- Text Collector
- beveiliging, IDs/codes en metadata vóór opslag
- Text Opslag
- normalisatie en verwerking van tekst
- conversation- en session-koppeling
- foutregistratie en feedback voor Text
- retrieval/memory-koppelingen voor goedgekeurde kennis
- koppeling met de text/AI-engine
- checks voor veilige opslag, correcte routing en fallbacks

## Regels

- Opslag bewaart de definitieve data.
- Collectors halen data op, controleren die en beveiligen/coderen die vóór opslag.
- Geen secrets, tokens of wachtwoorden in deze repository opslaan.
- Text-onderdelen blijven in deze map; Voice blijft apart in `../Voice/`.
