from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import torch
import torchaudio

processor = Wav2Vec2Processor.from_pretrained("/app/wav2vec2-large-xlsr-53-th")
model = Wav2Vec2ForCTC.from_pretrained("/app/wav2vec2-large-xlsr-53-th")

def speech2text(path_to_audio):
    resampling_to = 16000
    speech_array, sampling_rate = torchaudio.load(path_to_audio)
    resampler = torchaudio.transforms.Resample(sampling_rate, resampling_to)
    speech_array = resampler(speech_array)[0].numpy()

    inputs = processor(speech_array, sampling_rate=16_000, return_tensors="pt", padding=True)

    # inference
    with torch.no_grad():
        logits = model(inputs.input_values,).logits

    predicted_ids = torch.argmax(logits, dim=-1)
    result_text = processor.batch_decode(predicted_ids)
    return result_text