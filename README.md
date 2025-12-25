# ComfyUI for CUDA, ROCm and CPU

## Prerequisite 
1. Install [Docker](https://www.docker.com/get-started/){:target="_blank"}
</br>

## Guideline for building and pushing your own ComfyUI images
1. Navigate to one of the ComfyUI CUDA/ROCm/CPU folder that you want to build
   - If you have Nvidia GPU, then download the ComfyUI (CUDA) folder.
   - If you have AMD GPU, then download the ComfyUI (ROCm) folder.
   - If you want to only use CPU, then download the ComfyUI (CPU) folder.</br>
     (⚠️ This option is generally not recommended as CPU is slower than GPU in performing AI workloads)

3. Run the command below to build it, replace <image_name> with your own image name
```
docker build -t <image_name> .
```
3. Run the command below to push it to remote repository, replace <image_name> with your own image name
```
docker push <image_name>
```
</br>

## Follow guide below to run the ROCm images

### 1. Install Radeon software for WSL with ROCm:
[ROCM Installation Guide](https://rocm.docs.amd.com/projects/radeon-ryzen/en/latest/docs/install/installrad/wsl/install-radeon.html){:target="_blank"}

### 2. Run the docker image with the following commands:
```
docker run --name comfyui-rocm -it --cap-add=SYS_PTRACE --security-opt seccomp=unconfined --ipc=host --shm-size 8G --device=/dev/dxg -v /usr/lib/wsl/lib/libdxcore.so:/usr/lib/libdxcore.so -v /opt/rocm/lib/libhsa-runtime64.so.1:/opt/rocm/lib/libhsa-runtime64.so.1 -p 8188:8188 leewei1702/comfyui:amd
```
</br>

## Link for pulling down my own CUDA, ROCm, CPU images 
[Link to my docker images](https://hub.docker.com/r/leewei1702/comfyui){:target="_blank"}
