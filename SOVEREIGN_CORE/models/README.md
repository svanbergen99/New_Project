# Model storage

Model weights do not belong in Git history.

The runtime expects the server-side model at:

`/opt/kcdee/models/Qwen3-1.7B-Base-Runtime/qwen3-1.7b-base-q4_k_m.gguf`

The untouched Hugging Face source model is kept separately at:

`/opt/kcdee/models/Qwen3-1.7B-Base/`

See `../SERVER_MODEL_SETUP.md` and `../model_manifest.json`.
