FROM python:3.11

WORKDIR /

RUN apt-get update && apt-get install -y \
  git \
  wget \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir comfy-cli

RUN yes | comfy --here install

# Uncomment the code below to install custom model for ComfyUI
RUN yes | comfy model download --url https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned.safetensors --filename stable-diffusion-v1-5-pruned.safetensors --relative-path models/checkpoints

# Uncomment the code below to install video model for ComfyUI
# RUN yes | comfy model download --url https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors --filename wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors --relative-path models/diffusion_models
# RUN yes | comfy model download --url https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors --filename wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors --relative-path models/diffusion_models
# RUN yes | comfy model download --url https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors --filename wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors --relative-path models/loras
# RUN yes | comfy model download --url https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors --filename wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors --relative-path models/loras
# RUN yes | comfy model download --url https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors --filename wan_2.1_vae.safetensors --relative-path models/vae
# RUN yes | comfy model download --url https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors --filename umt5_xxl_fp8_e4m3fn_scaled.safetensors --relative-path models/text_encoders

# Install ComfyUI Easy Use Node
RUN git clone https://github.com/yolain/ComfyUI-Easy-Use.git ./ComfyUI/custom_nodes/comfyui-easy-use

RUN pip3 install --no-cache-dir -r ./ComfyUI/custom_nodes/comfyui-easy-use/requirements.txt

# Install ComfyUI Login
COPY ./ComfyUI-Login ./ComfyUI/custom_nodes/ComfyUI-Login

RUN pip3 install --no-cache-dir -r ./ComfyUI/custom_nodes/ComfyUI-Login/requirements.txt

# Install SaveVideoWebsocket Node
COPY ./websocket_video_save.py ./ComfyUI/custom_nodes/websocket_video_save.py

# Install SaveAudioWebsocket Node
COPY ./websocket_audio_save.py ./ComfyUI/custom_nodes/websocket_audio_save.py

# Preinstall workflow
COPY ./ComfyUI_Workflow/*.json /ComfyUI/user/default/workflows/

# Set the Comfy UI API Token (Comment to randomly generate api token)
# ENV COMFY_API_TOKEN=""

# Set the Comfy UI Login Username and Password (Comment to prompt for register page)
# ENV COMFY_USERNAME=""
# ENV COMFY_PASSWORD=""

COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 8188

CMD ["/start.sh"]
