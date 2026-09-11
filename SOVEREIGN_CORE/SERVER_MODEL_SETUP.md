# Qwen3-1.7B-Base server setup

This repo stores runtime configuration, not model weights.

## Target layout

```text
/opt/kcdee/models/
├── Qwen3-1.7B-Base/
│   ├── config.json
│   ├── generation_config.json
│   ├── merges.txt
│   ├── model.safetensors
│   ├── tokenizer.json
│   ├── tokenizer_config.json
│   └── vocab.json
└── Qwen3-1.7B-Base-Runtime/
    └── qwen3-1.7b-base-q4_k_m.gguf
```

## Deployment sequence

1. Copy or download the original `Qwen3-1.7B-Base.zip` to the server.
2. Extract the archive into `/opt/kcdee/models/Qwen3-1.7B-Base/`.
3. Verify the seven expected source files from `model_manifest.json` are present.
4. Keep the original safetensors source untouched.
5. Convert a separate runtime copy to GGUF.
6. Quantize that runtime copy as `Q4_K_M` for the 8 GB RAM server target.
7. Store the result at `/opt/kcdee/models/Qwen3-1.7B-Base-Runtime/qwen3-1.7b-base-q4_k_m.gguf`.
8. Calculate and record SHA-256 in `model_manifest.json` and in the runtime environment.
9. Start inference locally only and verify `/health` and `/v1/sovereign/status` before exposing anything outside the private runtime network.

## Safety rules

- Do not commit `.safetensors`, `.gguf`, ZIP archives, API keys, passwords, or tokens to this repository.
- The model endpoint remains private/internal.
- No external AI fallback is enabled.
- Imported model code is not executed from the downloaded model directory.
- The original source model remains recoverable and unchanged so conversion can be repeated later.

## Resource target

The initial runtime target is CPU inference on the existing 8 GB RAM server. Start with a 4096-token context. Increase it only after measuring actual memory use and stability.
