import requests
import gzip
import shutil
import os

def download_mesh():
    url = "https://nlmpubs.nlm.nih.gov/projects/mesh/rdf/2025/mesh2025.nt.gz"
    local_gz = "mesh2025.nt.gz"
    local_nt = "mesh2025.nt"

    if not os.path.exists(local_nt):
        print(f"正在下載 {url}...")
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_gz, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        
        print("下載完成，正在解壓縮...")
        with gzip.open(local_gz, 'rb') as f_in:
            with open(local_nt, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        print(f"解壓縮完成：{local_nt}")
    else:
        print(f"{local_nt} 已存在，跳過下載。")

if __name__ == "__main__":
    download_mesh()