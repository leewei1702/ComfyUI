import io
import time
try:
    import torchaudio
    TORCH_AUDIO_AVAILABLE = True
except:
    TORCH_AUDIO_AVAILABLE = False
import av
from server import PromptServer
from protocol import BinaryEventTypes

class SaveAudioWebsocket:
    @classmethod
    def INPUT_TYPES(s):
        return {"required":
                    {"audio": ("AUDIO", ),}
                }

    RETURN_TYPES = ()
    FUNCTION = "save_audio"

    OUTPUT_NODE = True

    CATEGORY = "api/audio"

    def save_audio(self, audio):
        _OPUS_RATES = [8000, 12000, 16000, 24000, 48000]
        format = "mp3"
        quality = "320k"

        for batch_number,  waveform in enumerate(audio["waveform"].cpu()):
            # Use original sample rate initially
            sample_rate = audio["sample_rate"]

            # Handle Opus sample rate requirements
            if format == "opus":
                if sample_rate > 48000:
                    sample_rate = 48000
                elif sample_rate not in _OPUS_RATES:
                    # Find the next highest supported rate
                    for rate in sorted(_OPUS_RATES):
                        if rate > sample_rate:
                            sample_rate = rate
                            break
                    if sample_rate not in _OPUS_RATES:  # Fallback if still not supported
                        sample_rate = 48000

                # Resample if necessary
                if sample_rate != audio["sample_rate"]:
                    if not TORCH_AUDIO_AVAILABLE:
                        raise Exception("torchaudio is not available; cannot resample audio.")
                    waveform = torchaudio.functional.resample(waveform, audio["sample_rate"], sample_rate)

            # Create output with specified format
            output_buffer = io.BytesIO()
            output_container = av.open(output_buffer, mode="w", format=format)

            layout = "mono" if waveform.shape[0] == 1 else "stereo"
            # Set up the output stream with appropriate properties
            if format == "opus":
                out_stream = output_container.add_stream("libopus", rate=sample_rate, layout=layout)
                if quality == "64k":
                    out_stream.bit_rate = 64000
                elif quality == "96k":
                    out_stream.bit_rate = 96000
                elif quality == "128k":
                    out_stream.bit_rate = 128000
                elif quality == "192k":
                    out_stream.bit_rate = 192000
                elif quality == "320k":
                    out_stream.bit_rate = 320000
            elif format == "mp3":
                out_stream = output_container.add_stream("libmp3lame", rate=sample_rate, layout=layout)
                if quality == "V0":
                    # TODO i would really love to support V3 and V5 but there doesn't seem to be a way to set the qscale level, the property below is a bool
                    out_stream.codec_context.qscale = 1
                elif quality == "128k":
                    out_stream.bit_rate = 128000
                elif quality == "320k":
                    out_stream.bit_rate = 320000
            else:  # format == "flac":
                out_stream = output_container.add_stream("flac", rate=sample_rate, layout=layout)

            frame = av.AudioFrame.from_ndarray(
                waveform.movedim(0, 1).reshape(1, -1).float().numpy(),
                format="flt",
                layout=layout,
            )
            frame.sample_rate = sample_rate
            frame.pts = 0
            output_container.mux(out_stream.encode(frame))

            # Flush encoder
            output_container.mux(out_stream.encode(None))

            # Close containers
            output_container.close()

            output_buffer.seek(0)

            audio_bytes = output_buffer.read()
                    
            PromptServer.instance.send_sync(BinaryEventTypes.TEXT, audio_bytes)

        return {}

    @classmethod
    def IS_CHANGED(s, audio):
        return time.time()

NODE_CLASS_MAPPINGS = {
    "SaveAudioWebsocket": SaveAudioWebsocket,
}
