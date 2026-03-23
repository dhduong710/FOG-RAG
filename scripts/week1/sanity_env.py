import sys

print("python:", sys.version)

try:
    import torch
    print("torch:", torch.__version__)
    print("cuda available:", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("cuda device count:", torch.cuda.device_count())
        print("cuda device name:", torch.cuda.get_device_name(0))
except Exception as e:
    print("torch import failed:", repr(e))

try:
    import transformers
    print("transformers:", transformers.__version__)
except Exception as e:
    print("transformers import failed:", repr(e))

try:
    import peft
    print("peft: ok")
except Exception as e:
    print("peft import failed:", repr(e))

try:
    import networkx as nx
    print("networkx:", nx.__version__)
except Exception as e:
    print("networkx import failed:", repr(e))

print("sanity_env done")