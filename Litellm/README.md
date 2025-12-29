# Custom API Server for image generation and image edit in Litellm

## Prerequisite

Install [uv package](https://docs.astral.sh/uv/)

## Code for running this litellm

```
uv venv
```

```
source .venv/bin/activate
```

```
uv pip install litellm[proxy]
```

```
uv pip install websocket-client
```

```
litellm --config ./config.yaml

```

