# Visual Engine — Video Pipeline Architecture

Dit document legt de vaste route, vaste servicenames en live-koppelingen vast voor de video-verwerkingscyclus binnen de Visual Engine.

## Canonieke namen

Deze namen zijn vanaf nu leidend en moeten in Railway, configuratie en code exact dezelfde betekenis houden:

- **Engine1** — eigenaar van de video-job; analyseert, maakt en verbetert video's.
- **Video1** — video-processing stap van Engine1.
- **Storage1** — permanente opslag na Video1.
- **Redis1** — queue/router van Storage1 naar Beheer.
- **Beheer** — tweede controle-/verwerkingsstap.
- **Video2** — video-processing stap van Beheer.
- **Storage2** — permanente opslag na Video2.
- **Redis2** — queue/router van Storage2 naar Collega.
- **Collega** — derde controle-/verwerkingsstap.
- **Video3** — video-processing stap van Collega.
- **Storage3** — permanente opslag na Video3.
- **Redis3** — queue/router van Storage3 naar ReCheck.
- **Postgres1** — centrale administratie, historie en ReCheck-status.

Gebruik geen alternatieve namen zoals `Job1`, `Job2`, `Queue-A`, `Recheck DB` of vergelijkbare varianten voor deze onderdelen.

## Vaste hoofdroute

```text
Engine1
  |
  v
Video1
  |
  v
Storage1
  |
  v
Redis1
  |
  v
Beheer
  |
  v
Video2
  |
  v
Storage2
  |
  v
Redis2
  |
  v
Collega
  |
  v
Video3
  |
  v
Storage3
  |
  v
Redis3
  |
  v
Postgres1 / ReCheck
```

## ReCheck / teruglus

Na Video3 wordt de laatste versie eerst in Storage3 opgeslagen. Redis3 publiceert daarna dat deze versie klaarstaat voor ReCheck.

Postgres1 bewaart de ReCheck-uitkomst.

```text
Storage3
  |
  v
Redis3
  |
  v
Postgres1 / ReCheck
  |
  +-- FOUT --> Engine1 --> Video1 --> Storage1 --> Redis1 --> Beheer --> ...
  |
  +-- GOED --> definitieve registratie/eindopslag van Engine1
```

Bij een fout blijft dezelfde `video_id` bestaan, maar Engine1 maakt een nieuwe `version` en de volledige route begint opnieuw.

## Live routing map

Wanneer de omgeving live wordt gekoppeld, moeten de verbindingen altijd volgens deze tabel worden gezet:

| Van | Naar | Doel |
|---|---|---|
| Engine1 | Video1 | nieuwe of gecorrigeerde video laten verwerken |
| Video1 | Storage1 | output van stap 1 permanent opslaan |
| Storage1 | Redis1 | pas na succesvolle opslag een job publiceren |
| Redis1 | Beheer | versie aanbieden aan Beheer |
| Beheer | Video2 | verwerking/controle van stap 2 |
| Video2 | Storage2 | output van stap 2 permanent opslaan |
| Storage2 | Redis2 | pas na succesvolle opslag een job publiceren |
| Redis2 | Collega | versie aanbieden aan Collega |
| Collega | Video3 | verwerking/controle van stap 3 |
| Video3 | Storage3 | output van stap 3 permanent opslaan |
| Storage3 | Redis3 | pas na succesvolle opslag een ReCheck-job publiceren |
| Redis3 | Postgres1/ReCheck | laatste versie laten beoordelen/registreren |
| Postgres1/ReCheck | Engine1 | alleen bij fout/correctie nodig |
| Postgres1/ReCheck | Engine1 eindarchief | bij goedkeuring definitieve versie registreren |

## Vaste configuratienamen voor live koppelingen

Gebruik in code/configuratie vaste environment-variable namen zodat Railway-links later niet door elkaar kunnen raken:

```text
ENGINE1_URL
VIDEO1_URL
STORAGE1_BUCKET
REDIS1_URL

BEHEER_URL
VIDEO2_URL
STORAGE2_BUCKET
REDIS2_URL

COLLEGA_URL
VIDEO3_URL
STORAGE3_BUCKET
REDIS3_URL

POSTGRES1_URL
```

Als Railway voor een component zelf een standaard variable levert (bijvoorbeeld `REDIS_URL` of `DATABASE_URL`), mag die intern worden gebruikt, maar binnen de Visual Engine-configuratie wordt hij naar de bovenstaande vaste naam gemapt.

Voorbeeld:

```text
Railway Redis service 1 REDIS_URL -> VE config REDIS1_URL
Railway Redis service 2 REDIS_URL -> VE config REDIS2_URL
Railway Redis service 3 REDIS_URL -> VE config REDIS3_URL
Railway Postgres DATABASE_URL     -> VE config POSTGRES1_URL
```

Daarmee is uit iedere variable direct af te leiden bij welk pipeline-onderdeel hij hoort.

## Belangrijkste opslagregel

Een volgende Redis-job mag pas worden gepubliceerd nadat de bijbehorende videoversie succesvol in de juiste Storage staat.

Dus altijd:

```text
verwerken
-> video opslaan in StorageN
-> versie/status in Postgres1 registreren
-> job naar RedisN publiceren
-> volgende stap
```

Niet andersom.

## Wat staat waar?

### Storage1, Storage2 en Storage3

De Storage-services bevatten de daadwerkelijke videobestanden. Redis en Postgres bevatten geen grote videobestanden.

Iedere versie moet minimaal gekoppeld blijven aan:

```text
video_id
job_id
version
created_by
storage_name
storage_path
created_at
```

De definitieve/centrale video-opslag hoort uiteindelijk bij Engine1.

### Redis1, Redis2 en Redis3

Redis bevat alleen kleine jobberichten. Iedere Redis heeft één vaste richting:

```text
Redis1 = Storage1 -> Beheer
Redis2 = Storage2 -> Collega
Redis3 = Storage3 -> Postgres1/ReCheck
```

Voorbeeld jobbericht:

```json
{
  "video_id": "847",
  "job_id": "ve-847",
  "version": 4,
  "from": "Storage1",
  "to": "Beheer",
  "storage_path": "video_847/v004.mp4"
}
```

Redis is transport en nooit de bron van waarheid.

### Postgres1

Postgres1 is de centrale bron van waarheid voor administratie en historie. Het bewaart onder andere:

```text
video_id
job_id
current_version
current_stage
status
storage_name
storage_path
created_by
feedback
error_code
recheck_count
approved
created_at
updated_at
```

Postgres1 moet altijd kunnen beantwoorden:

- Welke video is dit?
- Welke versie is de nieuwste?
- Waar staat die versie?
- Welke stap heeft hem gemaakt?
- Welke fouten zijn gevonden?
- Hoe vaak is hij opnieuw door de cyclus gegaan?
- Welke versie is definitief goedgekeurd?

## Eigenaarschap

**Engine1 blijft eigenaar van de video-job en het uiteindelijke archief.**

Beheer en Collega zijn stappen binnen dezelfde cyclus. Een correctieronde krijgt een nieuwe `version`, maar behoudt dezelfde `video_id` en `job_id`.

## Samenvatting

```text
Engine1   = eigenaar / analyse / verbetering / eindarchief
Video1-3  = video-processing per stap
Storage1-3 = permanente videoversies
Redis1-3  = vaste doorgeefroutes tussen de stappen
Postgres1 = hoofdadministratie / historie / ReCheck
```

Deze namen, route en configuratie-mapping zijn de vaste standaard voor de Visual Engine en moeten bij live deployment als leidraad worden gebruikt voor alle service-links.