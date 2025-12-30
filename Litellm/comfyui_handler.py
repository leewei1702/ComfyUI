import time
import websocket #NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
import uuid
import json
import urllib.request
import httpx
import base64

from litellm import CustomLLM
from litellm.types.utils import ImageResponse, ImageObject
from litellm.llms.custom_httpx.http_handler import AsyncHTTPHandler
from typing import Any, Optional, Union

# --- Queue the workflow prompt via HTTP ---
def queue_prompt(prompt, client_id, api_base, api_key):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request("http://{}/prompt?token={}".format(api_base, api_key), data=data)
    return json.loads(urllib.request.urlopen(req).read())

# --- Receive images from ComfyUI WebSocket ---
def get_images(ws, prompt, save_image_websocket, client_id, api_base, api_key):
    prompt_id = queue_prompt(prompt, client_id, api_base, api_key)['prompt_id']
    output_images = {}
    current_node = ""
    while True:
        out = ws.recv()  # Receive message from WebSocket
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['prompt_id'] == prompt_id:
                    if data['node'] is None:
                        break # Execution is done
                    else:
                        current_node = data['node']
        else:
            if current_node == save_image_websocket:
                images_output = output_images.get(current_node, [])
                images_output.append(out[8:]) # Remove 8-byte header
                output_images[current_node] = images_output

    return output_images

# --- Custom LLM class ---
class ComfyUI(CustomLLM):
    
    # --- Image Generation ---
    async def aimage_generation(
            self, 
            model: str, 
            prompt: str, 
            model_response: ImageResponse,
            api_key: Optional[str],
            api_base: Optional[str], 
            optional_params: dict, 
            logging_obj: Any, 
            timeout: Optional[Union[float, httpx.Timeout]] = None, 
            client: Optional[AsyncHTTPHandler] = None, 
            **kwargs) -> ImageResponse:
        # --- Image generation workflow JSON ---
        image_gen_workflow_text = """
        {
        "3": {
            "inputs": {
            "seed": 555721097155891,
            "steps": 20,
            "cfg": 10,
            "sampler_name": "euler",
            "scheduler": "normal",
            "denoise": 1,
            "model": [
                "4",
                0
            ],
            "positive": [
                "6",
                0
            ],
            "negative": [
                "7",
                0
            ],
            "latent_image": [
                "15",
                0
            ]
            },
            "class_type": "KSampler",
            "_meta": {
            "title": "KSampler"
            }
        },
        "4": {
            "inputs": {
            "ckpt_name": "stable-diffusion-v1-5-pruned.safetensors"
            },
            "class_type": "CheckpointLoaderSimple",
            "_meta": {
            "title": "Load Checkpoint"
            }
        },
        "6": {
            "inputs": {
            "text": "generate blue ferrari car",
            "clip": [
                "4",
                1
            ]
            },
            "class_type": "CLIPTextEncode",
            "_meta": {
            "title": "CLIP Text Encode (Prompt)"
            }
        },
        "7": {
            "inputs": {
            "text": "text, watermark",
            "clip": [
                "4",
                1
            ]
            },
            "class_type": "CLIPTextEncode",
            "_meta": {
            "title": "CLIP Text Encode (Prompt)"
            }
        },
        "8": {
            "inputs": {
            "samples": [
                "3",
                0
            ],
            "vae": [
                "4",
                2
            ]
            },
            "class_type": "VAEDecode",
            "_meta": {
            "title": "VAE Decode"
            }
        },
        "15": {
            "inputs": {
            "width": 512,
            "height": 512,
            "batch_size": 1
            },
            "class_type": "EmptyLatentImage",
            "_meta": {
            "title": "Empty Latent Image"
            }
        },
        "17": {
            "inputs": {
            "images": [
                "8",
                0
            ]
            },
            "class_type": "SaveImageWebsocket",
            "_meta": {
            "title": "SaveImageWebsocket"
            }
        }
        }
        """

        save_image_websocket = "17"  # Node ID of the SaveImageWebsocket node in the image generation workflow
        
        # Load the image generation workflow
        image_gen_workflow = json.loads(image_gen_workflow_text)
        
        # Set the model file name
        image_gen_workflow["4"]["inputs"]["ckpt_name"] = optional_params.get("checkpoint", "")

        # Set the positive text prompt
        image_gen_workflow["6"]["inputs"]["text"] = prompt

        # Set the negative text prompt
        image_gen_workflow["7"]["inputs"]["text"] = optional_params.get("negative", "")

        # Set the width and height for the image generated
        image_gen_workflow["15"]["inputs"]["width"] = optional_params.get("width", 512)
        image_gen_workflow["15"]["inputs"]["height"] = optional_params.get("height", 512)

        # Set the Classifier-Free Guidance to balance creativity and adherence to the prompt
        image_gen_workflow["3"]["inputs"]["cfg"] = optional_params.get("cfg", 10)

        # Set the number of steps used in the denoising process
        image_gen_workflow["3"]["inputs"]["steps"] = optional_params.get("steps", 20)

        # Set the random seed for reproducibility
        image_gen_workflow["3"]["inputs"]["seed"] = optional_params.get("seed", 842849289)

        # Connect to ComfyUI WebSocket
        ws = websocket.WebSocket()
        client_id = str(uuid.uuid4())       # Unique client ID for this session
        ws.connect("ws://{}/ws?clientId={}&token={}".format(api_base, client_id, api_key))

        # Get images from the SaveImageWebsocket node
        images_bytes = get_images(ws, image_gen_workflow, save_image_websocket, client_id, api_base, api_key).get(save_image_websocket, [])
        
        if not images_bytes:
            raise ValueError("No images returned")

        # Convert the first image to base64 for LiteLLM
        base64_images_string = base64.b64encode(images_bytes[0]).decode("utf-8")

        ws.close()

        # Download images for testing
        # with open("Generated_Img.png", "wb") as fh:
        #     fh.write(images_bytes[0])

        return ImageResponse(
            created=int(time.time()),
            data=[ImageObject(b64_json=base64_images_string)],
        )
    
    # --- Image Edit ---
    async def aimage_edit(
        self,
        model: str,
        image: Any,
        prompt: str,
        model_response: ImageResponse,
        api_key: Optional[str],
        api_base: Optional[str],
        optional_params: dict,
        logging_obj: Any,
        timeout: Optional[Union[float, httpx.Timeout]] = None,
        client: Optional[AsyncHTTPHandler] = None,
        **kwargs,
    ) -> ImageResponse:
        
        # --- Image edit workflow JSON ---
        image_edit_workflow_text = """
        {        
        "3": {
            "inputs": {
            "seed": 802329597809280,
            "steps": 20,
            "cfg": 10,
            "sampler_name": "euler",
            "scheduler": "normal",
            "denoise": 0.6,
            "model": [
                "4",
                0
            ],
            "positive": [
                "6",
                0
            ],
            "negative": [
                "7",
                0
            ],
            "latent_image": [
                "12",
                0
            ]
            },
            "class_type": "KSampler",
            "_meta": {
            "title": "KSampler"
            }
        },
        "4": {
            "inputs": {
            "ckpt_name": "stable-diffusion-v1-5-pruned.safetensors"
            },
            "class_type": "CheckpointLoaderSimple",
            "_meta": {
            "title": "Load Checkpoint"
            }
        },
        "6": {
            "inputs": {
            "text": "add anime character inside the image",
            "clip": [
                "4",
                1
            ]
            },
            "class_type": "CLIPTextEncode",
            "_meta": {
            "title": "CLIP Text Encode (Prompt)"
            }
        },
        "7": {
            "inputs": {
            "text": "text, watermark",
            "clip": [
                "4",
                1
            ]
            },
            "class_type": "CLIPTextEncode",
            "_meta": {
            "title": "CLIP Text Encode (Prompt)"
            }
        },
        "8": {
            "inputs": {
            "samples": [
                "3",
                0
            ],
            "vae": [
                "4",
                2
            ]
            },
            "class_type": "VAEDecode",
            "_meta": {
            "title": "VAE Decode"
            }
        },
        "12": {
            "inputs": {
            "pixels": [
                "13",
                0
            ],
            "vae": [
                "4",
                2
            ]
            },
            "class_type": "VAEEncode",
            "_meta": {
            "title": "VAE Encode"
            }
        },
        "13": {
            "inputs": {
            "upscale_method": "lanczos",
            "width": 512,
            "height": 512,
            "crop": "disabled",
            "image": [
                "18",
                0
            ]
            },
            "class_type": "ImageScale",
            "_meta": {
            "title": "Upscale Image"
            }
        },
        "15": {
            "inputs": {
            "images": [
                "8",
                0
            ]
            },
            "class_type": "SaveImageWebsocket",
            "_meta": {
            "title": "SaveImageWebsocket"
            }
        },
        "18": {
            "inputs": {
            "base64_data": "",
            "image_output": "Preview",
            "save_prefix": "ComfyUI"
            },
            "class_type": "easy loadImageBase64",
            "_meta": {
            "title": "Load Image (Base64)"
            }
        }
        }
        """

        save_image_websocket = "15"  # Node ID of the SaveImageWebsocket node in the image edit workflow

        # Load the image edit workflow
        image_edit_workflow = json.loads(image_edit_workflow_text)
        
        # Set the model file name
        image_edit_workflow["4"]["inputs"]["ckpt_name"] = optional_params.get("checkpoint", "")

        # Set the image
        buffer = image[0]
        image_edit_workflow["18"]["inputs"]["base64_data"] = base64.b64encode(buffer.getvalue()).decode("utf-8")

        # Set the positive text prompt
        image_edit_workflow["6"]["inputs"]["text"] = prompt

        # Set the negative text prompt
        image_edit_workflow["7"]["inputs"]["text"] = optional_params.get("negative", "")

        # Set the width and height for the image generated
        image_edit_workflow["13"]["inputs"]["width"] = optional_params.get("width", 512)
        image_edit_workflow["13"]["inputs"]["height"] = optional_params.get("height", 512)

        # Set the Classifier-Free Guidance to balance creativity and adherence to the prompt
        image_edit_workflow["3"]["inputs"]["cfg"] = optional_params.get("cfg", 10)

        # Set the number of steps used in the denoising process
        image_edit_workflow["3"]["inputs"]["steps"] = optional_params.get("steps", 20)

        # Set the random seed for reproducibility
        image_edit_workflow["3"]["inputs"]["seed"] = optional_params.get("seed", 842849289)

        # Connect to ComfyUI WebSocket
        ws = websocket.WebSocket()
        client_id = str(uuid.uuid4())       # Unique client ID for this session
        ws.connect("ws://{}/ws?clientId={}&token={}".format(api_base, client_id, api_key))

        # Get images from the SaveImageWebsocket node
        images_bytes = get_images(ws, image_edit_workflow, save_image_websocket, client_id, api_base, api_key).get(save_image_websocket, [])
        
        if not images_bytes:
            raise ValueError("No images returned")

        # Convert the first image to base64 for LiteLLM
        base64_images_string = base64.b64encode(images_bytes[0]).decode("utf-8")

        ws.close()

        # Download images for testing
        # with open("Edited_Img.png", "wb") as fh:
        #     fh.write(images_bytes[0])

        return ImageResponse(
            created=int(time.time()),
            data=[ImageObject(b64_json=base64_images_string)],
        )


comfyui = ComfyUI()