# Visual Engine — Video Pipeline Architecture

Dit document legt de vaste route vast voor de video-verwerkingscyclus binnen de Visual Engine.

## Rollen

- **1 — Engine**: maakt, analyseert en verbetert de video.
- **2 — Beheer**: controleert/beheert de output van de Engine.
- **3 — Collega**: laatste controle-/beoordelingsstap voordat de video teruggaat naar ReCheck/Engine.
- **Storage X**: permanente opslag van de videoversie die bij de betreffende stap hoort.
- **Redis**: job-queue/verkeersregelaar tussen twee stappen. Redis bevat geen grote videobestanden.
- **Postgres**: centrale administratie en ReCheck-status. Postgres bewaart metadata, versies, fouten, status en storage-referenties; niet de videobestanden zelf.

## Vaste route

```text
1 ENGINE
  |
  v
STORAGE 1
  |
  v
REDIS: Job 1 -> Job 2
  |
  v
2 BEHEER
  |
  v
STORAGE 2
  |
  v
REDIS: Job 2 -> Job 3
  |
  v
3 COLLEGA
  |
  v
STORAGE 3
  |
  v
REDIS: Job 3 -> ReCheck
  |
  v
RECHECK / POSTGRES
  |
  +-- fout / verbetering nodig --> terug naar 1 ENGINE
  |
  +-- goedgekeurd --> definitieve route / eindopslag van 1
```

De cyclus kan meerdere keren worden uitgevoerd:

```text
1 -> X -> 2 -> X -> 3 -> X -> 1 -> X -> 2 -> X -> 3 -> X -> 1 ...
```

Hierbij staat `X` voor permanente video-opslag.

## Belangrijkste regel

Een volgende Redis-job mag pas worden gepubliceerd nadat de nieuwe videoversie succesvol in de bijbehorende Storage is opgeslagen.

Dus altijd:

```text
verwerking
-> video opslaan
-> Postgres-versie/status registreren
-> Redis-job publiceren
-> volgende stap
```

Niet andersom.

## Wat staat waar?

### Storage

Storage bevat de echte videobestanden, bijvoorbeeld:

```text
video_847/
  original/
  engine/
    v001.mp4
    v004.mp4
  beheer/
    v002.mp4
    v005.mp4
  collega/
    v003.mp4
    v006.mp4
  final/
    final.mp4
```

De definitieve/centrale video-opslag hoort uiteindelijk bij **Engine 1**.

### Redis

Redis transporteert alleen kleine jobberichten, bijvoorbeeld:

```json
{
  "video_id": "847",
  "version": 4,
  "from_stage": 1,
  "to_stage": 2,
  "storage_path": "video_847/engine/v004.mp4"
}
```

Redis is tijdelijk transport en niet de bron van waarheid.

### Postgres

Postgres is de centrale bron van waarheid voor de administratie, bijvoorbeeld:

```text
video_id
current_version
current_stage
status
storage_path
created_by_stage
feedback
error_code
recheck_count
approved
created_at
updated_at
```

Postgres moet daardoor altijd kunnen beantwoorden:

- Welke video is dit?
- Welke versie is de nieuwste?
- In welke stap zit hij nu?
- Waar staat het videobestand?
- Welke fouten zijn gevonden?
- Hoe vaak is hij opnieuw door de cyclus gegaan?
- Welke versie is uiteindelijk goedgekeurd?

## ReCheck-regel

Na stap 3 wordt de laatste opgeslagen versie uit Storage 3 via `Redis: Job 3 -> ReCheck` aangeboden aan ReCheck.

ReCheck registreert de beoordeling in Postgres.

- **Fout gevonden**: video gaat terug naar Engine 1 voor analyse en verbetering. Engine 1 maakt een nieuwe versie en de volledige cyclus start opnieuw.
- **Goedgekeurd**: de goedgekeurde versie wordt als definitieve versie in/voor de opslag van Engine 1 geregistreerd.

## Eigenaarschap

**Engine 1 blijft eigenaar van de video-job en het uiteindelijke archief.**

Beheer en Collega zijn stappen binnen de beoordelingscyclus. Zij mogen nieuwe versies, beoordeling en feedback toevoegen, maar de video-job blijft gekoppeld aan dezelfde `video_id`.

## Identiteit van een job

Iedere video krijgt vanaf het begin een vaste identiteit:

```text
video_id
job_id
version
origin
current_stage
status
storage_path
```

Een nieuwe correctieronde krijgt een nieuwe `version`, maar behoudt dezelfde `video_id`.

## Samenvatting

```text
STORAGE = videobestanden
POSTGRES = hoofdadministratie / historie / ReCheck-status
REDIS = wachtrij en transport tussen stappen
ENGINE 1 = eigenaar en eindarchief
```

Deze route is de standaardarchitectuur voor de Visual Engine totdat bewust een nieuwe versie van dit ontwerp wordt vastgesteld.
