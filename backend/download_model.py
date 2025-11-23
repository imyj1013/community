import os
from huggingface_hub import snapshot_download

local_dir = "./ai/kobart-summary-v3"
if not os.path.exists(local_dir):
    os.makedirs(local_dir)

snapshot_download(
    repo_id="EbanLee/kobart-summary-v3",
    local_dir=local_dir,
    local_dir_use_symlinks=False
)