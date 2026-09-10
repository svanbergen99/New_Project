# KC-Dee Foundation Model — Training Plan

Dit document beschrijft de route van lokaal gehost open-weight model naar een daadwerkelijk eigen KCD-model.

## Doelklassen

### Class A — local-runtime-only

- weights lokaal opgeslagen;
- geen externe inference;
- model kan oorspronkelijk door een derde partij zijn getraind.

### Class B — KCD-adapted

- lokale base weights;
- eigen KCD instruction/fine-tuning;
- eigen evaluaties;
- nog gebaseerd op een extern foundation model.

### Class C — KCD-foundation

- eigen tokenizer of volledig gecontroleerde tokenizer;
- trainingsdataset met vastgelegde rechten/provenance;
- training vanaf random weights;
- eigen checkpoints;
- eigen instruction/reasoning/tool training;
- geen externe inference vereist.

Alleen Class C voldoet aan de strengste definitie: KC-Dee's basismodel is door KCD zelf opgebouwd.

## 1. Dataset governance

Maak eerst een datasetmanifest per bron:

```text
source_id
source_type
owner/license
commercial_training_allowed
redistribution_allowed
contains_personal_data
cleaning_version
content_hash
language
tokens_estimate
```

Geen bron gaat de pretraining-corpus in voordat rechten en privacy expliciet zijn beoordeeld.

## 2. Corpus pipeline

```text
raw approved sources
-> normalize unicode/text
-> remove secrets/PII where required
-> exact + near duplicate removal
-> language/quality classification
-> contamination filters
-> shard
-> immutable hashes
-> train/validation/test split
```

Test/evalsets worden vóór training bevroren om leakage te voorkomen.

## 3. Tokenizer

Voor volledige controle trainen we een KCD-tokenizer op de goedgekeurde corpusmix.

Acceptance checks:

- Nederlands en Engels efficiënt;
- code/API-termen niet extreem gefragmenteerd;
- vaste special tokens;
- deterministic encode/decode;
- tokenizer model + vocabulary gehasht en versioned.

## 4. Base-model architectuur

Start klein. Niet meteen een gigantisch foundation model.

Eerste sovereign modeldoel:

```text
0.3B–1B parameters
Nederlandse/Engelse basis
8k context
causal decoder transformer
RMSNorm
RoPE
SwiGLU
GQA waar passend
bf16 training
```

De exacte architectuur wordt pas vastgezet na compute-budget en benchmark.

## 5. Pretraining vanaf random weights

Bewaar per run:

```text
architecture config
random seed
dataset manifest hash
tokenizer hash
optimizer/scheduler
batch/tokens per step
learning rate
precision
hardware
code commit
checkpoints
validation loss
```

Checkpoints zijn KCD artifacts en worden buiten gewone Git-history opgeslagen.

## 6. Instruction/SFT

Na base pretraining leert KC-Dee antwoorden volgens zijn rol:

- duidelijke Nederlandse antwoorden;
- feitelijke onzekerheid aangeven;
- tool-call schemas;
- security boundaries;
- KCD concepts;
- conversation behavior.

Trainingsdata moet antwoorden bevatten, niet alleen ruwe documenten.

## 7. Reasoning en tools

Gebruik gecontroleerde synthetic + menselijke voorbeelden voor:

```text
planning
multi-step problems
tool selection
structured output
error recovery
memory retrieval decisions
```

Synthetic data mag in de uiteindelijke sovereign route niet afhankelijk blijven van een externe teacher. Als een externe teacher tijdelijk wordt gebruikt tijdens bootstrap, markeer die data apart en vervang/valideer ze later.

## 8. Evaluatie

Minimaal:

- Nederlandse taalvaardigheid;
- instructievolging;
- factuality/hallucination rate;
- reasoning suites;
- code/API-basics;
- tool schema correctness;
- refusal/security tests;
- latency/RAM/VRAM;
- long-context stability;
- regression tests tegen vorige checkpoint.

## 9. Quantization/deployment

Master checkpoint blijft high precision. Deploymentvarianten kunnen GGUF/quantized zijn.

```text
master checkpoint
-> export
-> quantize
-> benchmark quality delta
-> SHA-256
-> signed manifest
-> deploy local runtime
```

## 10. De cut-the-cord gate

Een release heet pas sovereign wanneer:

1. alle externe AI provider credentials verwijderd zijn uit de testomgeving;
2. internet-egress voor inference niet nodig is;
3. modelweights lokaal beschikbaar en geverifieerd zijn;
4. memory/embeddings lokaal werken;
5. KC-Dee na cold restart antwoordt;
6. de automatische `cut_the_cord.py` test slaagt;
7. provenance en hashes reproduceerbaar zijn.

## Compute-realiteit

Een klein model vanaf nul is haalbaar als engineering-/leerproject met eigen GPU-capaciteit. Een model op het niveau van grote commerciële foundation-modellen vereist zeer veel meer data, GPU's, tijd en energie. Daarom schalen we capability stapsgewijs en houden we de KCD API stabiel terwijl het onderliggende eigen model steeds beter wordt.