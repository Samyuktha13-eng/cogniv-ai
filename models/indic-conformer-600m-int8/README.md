---
license: mit
base_model: ai4bharat/indic-conformer-600m-multilingual
tags:
  - automatic-speech-recognition
  - quantization
  - onnx
  - int8
  - conformer
  - ctc
  - rnnt
---

# IndicConformer-600M — ONNX Runtime dynamic INT8

An INT8-quantized checkpoint of [`ai4bharat/indic-conformer-600m-multilingual`](https://huggingface.co/ai4bharat/indic-conformer-600m-multilingual) — full credit to AI4Bharat for the base model, training, and the 22-language coverage of official Indian languages this checkpoint inherits entirely. This repo only quantizes the released weights; it introduces no new training data or architecture.

**What's quantized**: the shared 24-layer Conformer encoder (`encoder.onnx`, 97.5% of the model's parameters) via `onnxruntime.quantization.quantize_dynamic` (weight-only INT8, no calibration data). The CTC decoder, RNNT decoder/joint network, and the 22 per-language output heads are unchanged fp32 — their combined weight mass (~90MB) was small enough not to be worth the added risk on a first pass.

**Results vs. the fp32 baseline** (264-example stratified half-sample across 22 languages, both decoding heads — see the full methodology below):

| Metric | fp32 baseline | INT8 (this repo) |
|---|---|---|
| WER vs. text (CTC) | 0.2081 | 0.2053 |
| WER vs. text (RNNT) | 0.1966 | 0.1998 |
| Resident memory after load | 3.34 GB | 2.50 GB (-25%) |
| On-disk size | ~2.4 GB | 0.74 GB (-69%) |
| CPU inference time / audio duration (CTC) | 0.319 | 0.286 (faster) |
| CPU inference time / audio duration (RNNT) | 0.448 | 0.561 → 0.448 (faster) |

Aggregate WER is essentially unchanged on both decoding heads, and quantization also made CPU inference faster, not just smaller. WER-vs-baseline-transcript (a direct diff against the fp32 model's own output on the same audio, isolating behavioral drift from absolute quality) is 0.067 (CTC) / 0.055 (RNNT) — nonzero, meaning some individual transcriptions did shift wording even though the aggregate didn't get worse. Full per-language breakdown and methodology: see `TECHNICAL_REPORT.md` in [github.com/hazardscarn/vyoma_hackathon](https://github.com/hazardscarn/vyoma_hackathon) (`asr` branch).

Developed by David Babu.

## Usage

This is **not** a standard `transformers` architecture — like the base model, it's served through ONNX Runtime sessions plus a TorchScript preprocessor, wired together by the base model's own `model_onnx.py`. Use the `asr_exports` module from the GitHub repo above (handles this automatically, including a quick `load()`/`unload()` cycle for memory-constrained deployments), or directly:

```python
from asr_exports import QuantizedIndicConformer, ASRTranscriber

engine = QuantizedIndicConformer()   # downloads + caches this repo automatically
engine.load()

asr = ASRTranscriber(engine)
text = asr.transcribe_file("audio.wav", language="Hindi", decoding="ctc")   # or decoding="rnnt"
print(text)

engine.unload()
```

Supports all 22 languages the base model covers (Assamese, Bengali, Bodo, Dogri, Gujarati, Hindi, Kannada, Kashmiri, Konkani, Maithili, Malayalam, Manipuri, Marathi, Nepali, Odia, Punjabi, Sanskrit, Santali, Sindhi, Tamil, Telugu, Urdu) — **no English support**, same as the base model.

### Offline / one-time-download deployment (e.g. Jetson)

```bash
huggingface-cli download hazardscarn10/indic-conformer-600m-int8 --local-dir ./checkpoint
```

then `QuantizedIndicConformer(checkpoint_dir="./checkpoint")` skips the Hub entirely on every subsequent load — only the base model's tiny `model_onnx.py` glue code (~8KB) still resolves through `huggingface_hub`'s own local cache, no re-download after the first run.
