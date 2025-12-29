# How to Run Litellm

## Prerequisite

Install [uv package](https://docs.astral.sh/uv/)

## Code

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
