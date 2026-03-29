import time
from comfy_api.latest import Types
from server import PromptServer
from protocol import BinaryEventTypes
import io

class SaveVideoWebsocket:
    @classmethod
    def INPUT_TYPES(s):
        return {"required":
                    {"video": ("VIDEO", ),}
                }

    RETURN_TYPES = ()
    FUNCTION = "save_video"

    OUTPUT_NODE = True

    CATEGORY = "api/video"

    def save_video(self, video):
        buffer = io.BytesIO()

        video.save_to(
            buffer,
            format=Types.VideoContainer.MP4,
            codec=Types.VideoCodec.H264     
        )

        buffer.seek(0)

        video_bytes = buffer.read()

        PromptServer.instance.send_sync(BinaryEventTypes.TEXT, video_bytes)

        return {}

    @classmethod
    def IS_CHANGED(s, video):
        return time.time()

NODE_CLASS_MAPPINGS = {
    "SaveVideoWebsocket": SaveVideoWebsocket,
}
