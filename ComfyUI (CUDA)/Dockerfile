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

# Install Pytorch CUDA
RUN pip3 install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

# Install ComfyUI Easy Use Node
RUN git clone https://github.com/yolain/ComfyUI-Easy-Use.git ./ComfyUI/custom_nodes/comfyui-easy-use

RUN pip3 install --no-cache-dir -r ./ComfyUI/custom_nodes/comfyui-easy-use/requirements.txt

# Install ComfyUI Login
COPY ./ComfyUI-Login ./ComfyUI/custom_nodes/ComfyUI-Login

RUN pip3 install --no-cache-dir -r ./ComfyUI/custom_nodes/ComfyUI-Login/requirements.txt

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
