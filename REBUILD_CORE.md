# Rebuild Core

Dit document is de minimale vaste basis om vanuit een lege repository opnieuw een nieuwe realtime AI/visual/game-engine applicatie op te bouwen.

## Doel

Bewaar alleen herbruikbare bouwprincipes. Geen project-specifieke gebruikersdata, mediabestanden, gesprekken of tijdelijke output.

## 1. Basisarchitectuur

Gebruik losse verantwoordelijkheden:

```text
Input/API
   ↓
Collector / Gateway
   ↓
Validatie + authenticatie + normalisatie
   ↓
Engine / Orchestrator
   ↓
Externe API adapters
   ↓
Storage indien nodig
   ↓
Output / realtime stream
```

Een component krijgt één duidelijke verantwoordelijkheid. Externe providers worden altijd via een adapter aangeroepen zodat een provider later vervangen kan worden zonder de rest van het systeem opnieuw te bouwen.

## 2. API-adapter contract

Iedere externe API of game engine krijgt dezelfde globale vorm:

```text
adapter naam
base URL / SDK
AUTH env var naam
connect()
healthcheck()
request(input)
stream(input) indien ondersteund
normalize_response()
normalize_error()
timeout
retry policy
rate-limit handling
```

Nooit provider-specifieke logica overal door de applicatie verspreiden.

## 3. Security

- Geen echte API keys, tokens, wachtwoorden of private credentials in GitHub.
- Alleen environment-variable namen en configuratiecontracten in code/documentatie.
- Echte secrets blijven in Railway of een andere secret manager.
- Interne service-routes authenticeren met service-to-service credentials.
- Input valideren voordat die een engine of externe API bereikt.
- Logs mogen geen secrets of gevoelige payloads bevatten.
- Gebruik least privilege voor iedere service.
- Encrypt gevoelige persistente data wanneer opslag nodig is.

## 4. Environment-variable patroon

Gebruik stabiele namen per capability, niet per tijdelijke providernaam waar dat niet nodig is.

Voorbeeld:

```text
AI_API_KEY
GAME_ENGINE_API_KEY
VOICE_API_KEY
VIDEO_API_KEY
TEXT_API_KEY
STORAGE_URL
DATABASE_URL
REDIS_URL
INTERNAL_SERVICE_TOKEN
```

Provider-specifieke variabelen mogen daarnaast bestaan, bijvoorbeeld:

```text
GROQ_API_KEY
ELEVENLABS_API_KEY
DEEPGRAM_API_KEY
```

## 5. Collector-principe

Collectors zijn gateways tussen bron en systeem. Een Collector kan:

```text
ontvangen
valideren
authenticeren
normaliseren
ID / correlation_id toevoegen
metadata toevoegen
beveiligingsregels toepassen
routeren
```

Collectors zijn geen permanente hoofdopslag.

## 6. Storage-principe

Gebruik opslag alleen als het product het nodig heeft.

```text
Database = metadata, status, relaties, historie
Object/Bucket storage = grote bestanden zoals audio/video/assets
Redis/queue = tijdelijk transport, jobs en korte state
```

Redis is nooit de enige bron van waarheid voor belangrijke persistente data.

## 7. Realtime patroon

Voor realtime toepassingen:

```text
client
  ↓
WebSocket / SSE / realtime protocol
  ↓
gateway
  ↓
engine
  ↓
provider stream
  ↓
delta/event terug naar client
```

Belangrijk:

- niet wachten op het volledige resultaat als de provider kan streamen
- timeouts en disconnects afhandelen
- correlation_id per sessie/job
- backpressure/rate limits respecteren

## 8. Fouten en herstel

Iedere adapter en service geeft intern een genormaliseerde fout terug:

```text
error_code
source
retryable
safe_message
correlation_id
```

Externe/raw foutmeldingen of secrets nooit rechtstreeks naar de gebruiker sturen.

Bij tijdelijke providerproblemen:

```text
primary provider
   ↓ fout
fallback provider indien geconfigureerd
   ↓
veilige eindfout
```

## 9. Observability

Minimaal meten:

```text
request count
success/failure
first-response latency
total latency
provider
model/engine
rate-limit events
timeouts
```

Gebruik correlation IDs zodat één aanvraag door meerdere services gevolgd kan worden.

## 10. Railway rebuild

Om vanaf nul opnieuw te bouwen:

```text
1. Maak repository/service.
2. Deploy minimale health endpoint.
3. Voeg Railway environment variables/secrets toe.
4. Voeg Collector/Gateway toe.
5. Voeg Engine/Orchestrator toe.
6. Voeg externe API-adapter(s) toe.
7. Voeg streaming toe als nodig.
8. Voeg Storage/Database/Redis alleen toe wanneer nodig.
9. Voeg security checks en healthchecks toe.
10. Test end-to-end voordat nieuwe capabilities worden toegevoegd.
```

Iedere Railway service moet minimaal hebben:

```text
PORT
health endpoint
start command
region
required env vars
internal/public route-keuze
```

## 11. Startstructuur voor een nieuw project

```text
src/
  app/
  collectors/
  engine/
  adapters/
  security/
  storage/
  models/
  utils/
tests/
README.md
.env.example
```

`.env.example` bevat uitsluitend variabelenamen en nooit echte waarden.

## 12. Game-engine uitbreiding

Wanneer een game-engine API wordt gekozen, voeg hem als adapter toe zonder de kernarchitectuur te veranderen:

```text
User / AI decision
       ↓
Engine / Orchestrator
       ↓
GameEngineAdapter
       ↓
Game Engine API / SDK
       ↓
world state / actions / frames / events
       ↓
normalize
       ↓
AI + client
```

Bewaar per game-engine adapter minimaal:

```text
provider/engine naam
API/SDK versie
auth-methode
capabilities
rate limits
realtime protocol
input schema
output schema
asset handling
session/world identifiers
error mapping
```

## 13. Wat bewust NIET in deze repo hoort

```text
gebruikersdata
chatgeschiedenis
audio/video output
persoonlijke informatie
productiedatabase dumps
Redis contents
bucket contents
echte API keys/secrets
tijdelijke jobdata
```

## 14. Rebuild-regel

Als alle uitvoerende services verdwijnen maar dit document en de externe credentials/secrets nog bestaan, moet een nieuwe implementatie opnieuw kunnen worden ontworpen en opgebouwd zonder afhankelijk te zijn van de oude projectstructuur.

De bedoeling is niet oude code byte-voor-byte te herstellen. De bedoeling is een veilige, modulaire basis te behouden waarmee een compleet nieuw systeem kan worden gebouwd.
