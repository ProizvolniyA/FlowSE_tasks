import os
import requests
import zipfile
import io
import pandas as pd
from huggingface_hub import hf_hub_download
from tqdm import tqdm
import shutil

# Ссылка на архив с текстами (зеркало VCTK)
TXT_URL = "https://datashare.ed.ac.uk/bitstream/handle/10283/2651/VCTK-Corpus.zip"
# TXT_URL = "https://huggingface.co/datasets/CSTR-Edinburgh/vctk/resolve/main/vctk-corpus.zip"

print("Шаг 1: Качаю архив с текстами...")
r = requests.get(TXT_URL, stream=True)
total_size = int(r.headers.get('content-length', 0))

with io.BytesIO() as f:
    with tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
            pbar.update(len(chunk))
    
    print("Шаг 2: Распаковка транскрипций...")
    with zipfile.ZipFile(f) as z:
        for file in z.namelist():
            if file.startswith('txt/') and file.endswith('.txt'):
                z.extract(file, path="./temp_vctk")

# Сопоставление с Parquet
print("Шаг 3: Синхронизация с аудиофайлами...")
repo_id_vb = "JacobLinCool/VoiceBank-DEMAND-16k"
parquet_path = hf_hub_download(repo_id=repo_id_vb, filename="data/test-00000-of-00001.parquet", repo_type="dataset")
df = pd.read_parquet(parquet_path)

target_dir = "./data/voicebank/testset_txt"
os.makedirs(target_dir, exist_ok=True)

success = 0
for i, row in tqdm(df.iterrows(), total=len(df)):
    vctk_id = row['id'] 
    speaker_id = vctk_id.split('_')[0]
    
    # Поиск файла в распакованном безобразии
    src_path = os.path.join("./temp_vctk", "txt", speaker_id, f"{vctk_id}.txt")
    dest_path = os.path.join(target_dir, f"test_{i:04d}.txt")
    
    if os.path.exists(src_path):
        shutil.copy(src_path, dest_path)
        success += 1

print(f"\nИзвлечено текстов: {success} из {len(df)}")

shutil.rmtree("./temp_vctk")

