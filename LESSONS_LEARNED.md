# Lessons Learned — Voice & Text

Dit bestand bewaart alleen herbruikbare technische lessen uit eerder Voice- en Text/chat-engine werk. Geen gebruikersdata, geen mediabestanden en geen secrets.

Doel: bij een nieuw project dezelfde fouten niet opnieuw maken.

## 1. Railway / deployment

- Een gewijzigde Railway variable telt pas als live nadat de juiste deployment daadwerkelijk actief is.
- Controleer altijd project, environment, service-id en public domain voordat een deployment als correct wordt beschouwd.
- Maak geen duplicate services met bijna dezelfde naam; verifieer eerst welke service canoniek is.
- Koppel een service alleen aan de juiste repository. Visual/Engine en Voice Engine mogen nooit per ongeluk naar elkaars repo wijzen.
- Gebruik vaste, canonieke servicenames en env-var namen; let op hoofdlettergevoeligheid.

## 2. Provider en model

- Behandel provider en model als twee aparte velden. Een model-id die met `openai/` begint betekent niet automatisch dat OpenAI de provider is.
- Hard-code geen oud model in CI wanneer productie bewust een ander model gebruikt.
- Provider-specifieke logica hoort achter een adapter en niet verspreid door de applicatie.
- Voeg timeouts, rate-limit handling en een veilige fallback toe waar mogelijk.

## 3. Streaming

- SSE is geen gewone JSON-response. Parse SSE-events volgens het protocol (`data:`, `event:`, lege regel als grens).
- Bouw geen client op een interne streamingroute die nog niet bestaat; definieer en test het contract eerst.
- Een streamingroute moet dezelfde authenticatie-, logging-, storage- en securityregels behouden als de niet-streamende route.
- Streaming mag Data Collector/telemetry nooit stilletjes omzeilen.
- Stuur deltas direct door; wacht niet eerst tot het hele providerantwoord binnen is.
- Strip protocol-/provider-tags robuust over chunkgrenzen; neem nooit aan dat een tag in één chunk arriveert.
- Handel client disconnects, upstream disconnects en incomplete streams expliciet af.
- Geef raw upstream errors of stacktraces nooit rechtstreeks door in SSE-events.
- Voeg een expliciete fallback toe wanneer browser-streaming niet beschikbaar is; voorkom dubbele user/bot UI-rows bij fallback.

## 4. Async / realtime

- Voer blokkerende netwerkcalls niet rechtstreeks uit in een async WebSocket/event-loop pad.
- Gebruik async clients of verplaats blocking werk naar een thread/executor.
- Meet minimaal first-response latency en total latency.
- Gebruik correlation/session IDs zodat één realtime request door alle services gevolgd kan worden.

## 5. Voice input/output

- Een microfoonfeature is pas echt als `getUserMedia`/MediaRecorder of een echte realtime audiopipeline aanwezig is; geen vaste testtekst als productiepad.
- Controleer dat STT-client, audioformaat, streamingroute en provider werkelijk end-to-end gekoppeld zijn.
- TTS/STT routes moeten dezelfde auth- en errorcontracten volgen als chat.
- Leg provider voice-id/config apart vast van de rest van de engine zodat stemmen later vervangbaar blijven.

## 6. SDK's en dependencies

- Neem geen API/SDK-methodes aan op basis van een oudere versie; controleer de gebruikte major versie.
- Pin belangrijke dependencies zodat een onverwachte upgrade productie niet breekt.
- Als een NLP/model dependency vereist is, controleer bij startup dat die werkelijk aanwezig en geladen is.
- Laat ontbrekende dependencies niet stil verdwijnen achter brede exception handlers.

## 7. Storage / memory

- Een memory/vector store is niet persistent alleen omdat hij tijdens runtime werkt; persistence expliciet configureren en testen.
- Slik storage-/memory-exceptions niet stil in. Log veilig en markeer de operatie als niet-opgeslagen.
- Redis is transport/cache/queue, geen enige bron van waarheid voor belangrijke data.
- Grote media horen in object/bucket storage; metadata/status/historie in een database.

## 8. Security

- Geen echte API keys, tokens of wachtwoorden in GitHub.
- Interne service-routes vereisen service-to-service authenticatie.
- Publieke routes en interne routes krijgen niet automatisch dezelfde toegangsrechten.
- Gebruik geen open CORS + credentials zonder expliciete, beperkte origin allowlist.
- Redact gevoelige input/output vóór logging of langdurige opslag.
- Externe foutdetails worden genormaliseerd naar een veilige `safe_message`.

## 9. Frontend / chat

- Bewaar bestaande sessie/auth-semantiek bij nieuwe transportlagen; streaming mag trusted-device gedrag niet veranderen.
- Behandel 401/403, 429, 502 en 503 bewust en verschillend.
- Voeg foutafhandeling, reconnect/fallback en idempotent UI-gedrag toe voordat realtime als klaar wordt beschouwd.
- Bouw rich formatting pas na complete stream op als dat nodig is; deltas zelf veilig als tekst tonen.

## 10. Git / branches / CI

- Controleer vóór merge of de featurebranch achterloopt op `main`.
- Rebase/herbouw een branch op actuele `main` wanneer relevante files niet conflicteren; merge geen stale branch blind.
- Verifieer na rebase exact welke files veranderd zijn.
- Gebruik CI-checks als guardrail, maar controleer of de check zelf nog klopt en niet op oude configuratie is gebaseerd.
- Na merge: deploymentstatus van de juiste Railway service verifiëren.

## 11. Observability / collector

- Iedere nieuwe response-route moet expliciet bepalen of en hoe telemetry/Data Collector wordt aangeroepen.
- Collector-fouten mogen het primaire antwoord niet blokkeren, maar mogen ook niet volledig onzichtbaar blijven.
- Bewaar provider, model/engine, latency, success/failure en relevante redaction-status als metadata waar passend.

## 12. Rebuild-regel

Bij ieder nieuw project eerst deze vragen beantwoorden:

```text
1. Wat is de input?
2. Welke auth is vereist?
3. Wat is het API/streaming contract?
4. Welke externe provider/engine zit achter een adapter?
5. Wat moet persistent worden opgeslagen en wat juist niet?
6. Welke telemetry moet altijd meelopen?
7. Wat gebeurt er bij timeout, rate limit, providerfout of disconnect?
8. Welke secrets/env vars zijn nodig?
9. Hoe testen we end-to-end?
10. Hoe weten we na deploy zeker dat de juiste service live staat?
```

Als één van deze punten onbeantwoord is, is de capability nog niet production-ready.
