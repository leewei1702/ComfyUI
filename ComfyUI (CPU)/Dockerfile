FROM ghcr.io/open-webui/open-webui:ollama

WORKDIR /

RUN apt-get update && apt-get install -y \
  git \
  wget \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir comfy-cli

RUN yes | comfy --here install

# Uncomment the code below to install custom model for ollama
RUN ollama serve & while ! ollama list | grep -q 'NAME'; do sleep 1; done && ollama pull gemma3:270m

# Uncomment the code below to install custom model for ComfyUI
RUN yes | comfy model download --url https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned.safetensors --filename stable-diffusion-v1-5-pruned.safetensors --relative-path models/checkpoints

# Open-webui Environment Variable
ENV ENABLE_IMAGE_GENERATION=true

ENV IMAGE_GENERATION_ENGINE="comfyui"

ENV COMFYUI_BASE_URL="http://127.0.0.1:8188"

ENV IMAGE_GENERATION_MODEL="stable-diffusion-v1-5-pruned.safetensors"

ENV COMFYUI_WORKFLOW='{"3":{"inputs":{"seed":555721097155891,"steps":20,"cfg":10,"sampler_name":"euler","scheduler":"normal","denoise":1,"model":["4",0],"positive":["6",0],"negative":["7",0],"latent_image":["15",0]},"class_type":"KSampler","_meta":{"title":"KSampler"}},"4":{"inputs":{"ckpt_name":"stable-diffusion-v1-5-pruned.safetensors"},"class_type":"CheckpointLoaderSimple","_meta":{"title":"Load Checkpoint"}},"6":{"inputs":{"text":"","clip":["4",1]},"class_type":"CLIPTextEncode","_meta":{"title":"CLIP Text Encode (Prompt)"}},"7":{"inputs":{"text":"text, watermark","clip":["4",1]},"class_type":"CLIPTextEncode","_meta":{"title":"CLIP Text Encode (Prompt)"}},"8":{"inputs":{"samples":["3",0],"vae":["4",2]},"class_type":"VAEDecode","_meta":{"title":"VAE Decode"}},"9":{"inputs":{"filename_prefix":"ComfyUI","images":["8",0]},"class_type":"SaveImage","_meta":{"title":"Save Image"}},"15":{"inputs":{"width":512,"height":512,"batch_size":1},"class_type":"EmptyLatentImage","_meta":{"title":"Empty Latent Image"}}}'

ENV COMFYUI_WORKFLOW_NODES='[{"type":"prompt","key":"text","node_ids":["6"]},{"type":"model","key":"ckpt_name","node_ids":["4"]},{"type":"width","key":"width","node_ids":["15"]},{"type":"height","key":"height","node_ids":["15"]},{"type":"steps","key":"steps","node_ids":["3"]},{"type":"seed","key":"seed","node_ids":["3"]}]'

ENV ENABLE_IMAGE_EDIT=true

ENV IMAGE_EDIT_ENGINE="comfyui"

ENV IMAGES_EDIT_COMFYUI_BASE_URL="http://127.0.0.1:8188"

ENV IMAGE_EDIT_MODEL="stable-diffusion-v1-5-pruned.safetensors"

ENV IMAGES_EDIT_COMFYUI_WORKFLOW='{"3":{"inputs":{"seed":485912478059740,"steps":20,"cfg":10,"sampler_name":"euler","scheduler":"normal","denoise":0.6,"model":["4",0],"positive":["6",0],"negative":["7",0],"latent_image":["12",0]},"class_type":"KSampler","_meta":{"title":"KSampler"}},"4":{"inputs":{"ckpt_name":"stable-diffusion-v1-5-pruned.safetensors"},"class_type":"CheckpointLoaderSimple","_meta":{"title":"Load Checkpoint"}},"6":{"inputs":{"text":"","clip":["4",1]},"class_type":"CLIPTextEncode","_meta":{"title":"CLIP Text Encode (Prompt)"}},"7":{"inputs":{"text":"text, watermark","clip":["4",1]},"class_type":"CLIPTextEncode","_meta":{"title":"CLIP Text Encode (Prompt)"}},"8":{"inputs":{"samples":["3",0],"vae":["4",2]},"class_type":"VAEDecode","_meta":{"title":"VAE Decode"}},"9":{"inputs":{"filename_prefix":"ComfyUI","images":["8",0]},"class_type":"SaveImage","_meta":{"title":"Save Image"}},"11":{"inputs":{"image":""},"class_type":"LoadImage","_meta":{"title":"Load Image"}},"12":{"inputs":{"pixels":["13",0],"vae":["4",2]},"class_type":"VAEEncode","_meta":{"title":"VAE Encode"}},"13":{"inputs":{"upscale_method":"lanczos","width":512,"height":512,"crop":"disabled","image":["11",0]},"class_type":"ImageScale","_meta":{"title":"Upscale Image"}}}'

ENV IMAGES_EDIT_COMFYUI_WORKFLOW_NODES='[{"type":"image","key":"image","node_ids":["11"]},{"type":"prompt","key":"prompt","node_ids":["6"]},{"type":"model","key":"unet_name","node_ids":["4"]},{"type":"width","key":"width","node_ids":["13"]},{"type":"height","key":"height","node_ids":["13"]}]'

# Preinstall workflow
COPY ./ComfyUI_Workflow/*.json /ComfyUI/user/default/workflows/

COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 8188

CMD ["/start.sh"]