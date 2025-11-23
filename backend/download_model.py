from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="EbanLee/kobart-summary-v3",
    local_dir="./ai/kobart-summary-v3",
    local_dir_use_symlinks=False
)