# KC-Dee Sovereign Core

Doel: KC-Dee moet kunnen blijven antwoorden wanneer alle externe AI-, voice-, vision- en renderproviders worden uitgezet.

## Definitie van sovereign

Een build is pas sovereign als:

- chat-inference uitsluitend lokale modelweights gebruikt;
- geen fallback naar OpenAI, Groq, Anthropic, ElevenLabs of andere externe inference bestaat;
- memory en embeddings lokaal/eigen gehost zijn;
- voice, vision en rendering lokale adapters kunnen gebruiken;
- modelweights een bekende hash, versie, licentie en provenance hebben;
- een cut-the-cord test slaagt terwijl externe AI-egress geblokkeerd is.

## Runtime-contract

```text
KCD Chat
  -> Sovereign Core API
      -> local model runtime
          -> KCD-owned/local model weights
      -> local memory
      -> local tools
      -> local STT/TTS/vision/render adapters
```

De inference-runtime (bijvoorbeeld llama.cpp) is alleen de rekenmotor. Hij levert geen intelligentie als dienst. Het modelgedrag zit in de lokale weights die KC-Dee laadt.

## Fase 1 — runtime onafhankelijk

Eerst maken we externe AI tijdens runtime optioneel en uiteindelijk onmogelijk in sovereign mode.

- lokale LLM inference via een private endpoint;
- provider-neutral KCD API;
- geen internet-URL toegestaan als model-endpoint;
- lokale modelmanifesten + SHA-256 verificatie;
- offline health/status;
- cut-the-cord tests.

## Fase 2 — eigen KC-Dee model

Daarna vervangen we een open base model stap voor stap door een eigen KCD-model:

```text
rechten-gecontroleerde KCD corpus
-> eigen tokenizer
-> pretraining vanaf random weights
-> instruction/SFT
-> reasoning/tool training
-> evaluatie
-> quantization
-> signed model manifest
-> sovereign runtime
```

Tot die stap volledig is afgerond kan een open-weight model lokaal draaien zonder externe inference, maar het is dan nog geen volledig van-nul-getraind KCD foundation model.

## Railway/GitHub rol

Railway is orchestration/API/storage, niet de uiteindelijke zware GPU-inference host. GitHub bewaart broncode, manifests en reproduceerbare builds. De runtime moet ook op een eigen Linux/GPU-machine kunnen draaien.

## Mappen

- `core/` — lokale-only KCD gateway.
- `model_manifest.example.json` — contract voor modelweights/provenance.
- `docker-compose.yml` — portable lokale stack met llama.cpp.
- `cut_the_cord.py` — acceptance test zonder externe providers.
- `TRAINING_PLAN.md` — pad naar een eigen KC-Dee foundation model.

## Sovereign acceptance gate

Groen betekent minimaal:

```text
external_ai_calls = 0
external_voice_calls = 0
external_vision_calls = 0
model_endpoint_is_private = true
local_model_loaded = true
model_hash_verified = true
chat_test = pass
restart_test = pass
```

Geen enkele externe provider mag stil als fallback worden gebruikt.