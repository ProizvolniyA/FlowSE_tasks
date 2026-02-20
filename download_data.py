import os
import io
import pandas as pd
import soundfile as sf
from huggingface_hub import hf_hub_download
from tqdm import tqdm

repo_id = "JacobLinCool/VoiceBank-DEMAND-16k"
filename = "data/test-00000-of-00001.parquet"

print(" 1. Загрузка таблицы...")
file_path = hf_hub_download(repo_id=repo_id, filename=filename, repo_type="dataset")

print(" 2. Анализ структуры данных...")
df = pd.read_parquet(file_path)

print(f"Доступные колонки: {df.columns.tolist()}")

col_clean = 'audio' if 'audio' in df.columns else ('clean' if 'clean' in df.columns else None)
col_noisy = 'noisy_audio' if 'noisy_audio' in df.columns else ('noisy' if 'noisy' in df.columns else None)
col_txt = 'transcription' if 'transcription' in df.columns else ('text' if 'text' in df.columns else None)

if not col_clean or not col_noisy:
    print(" Нет колонок с аудио.")
    exit()

# Пути
base_dir = "./data/voicebank"
clean_dir = os.path.join(base_dir, "clean_testset_wav")
noisy_dir = os.path.join(base_dir, "noisy_testset_wav")
txt_dir = os.path.join(base_dir, "testset_txt")

for d in [clean_dir, noisy_dir, txt_dir]:
    os.makedirs(d, exist_ok=True)

print(f" 3. Извлечение файлов из '{col_clean}' и '{col_noisy}'...")

for i, row in tqdm(df.iterrows(), total=len(df)):
    name = f"test_{i:04d}"
    
    try:
        # Извлечение чистого аудио (проверяем, словарь это или сразу байты)
        clean_data = row[col_clean]['bytes'] if isinstance(row[col_clean], dict) else row[col_clean]
        with io.BytesIO(clean_data) as b:
            data, sr = sf.read(b)
            sf.write(os.path.join(clean_dir, f"{name}.wav"), data, sr)
            
        # Извлечение шумного аудио
        noisy_data = row[col_noisy]['bytes'] if isinstance(row[col_noisy], dict) else row[col_noisy]
        with io.BytesIO(noisy_data) as b:
            data, sr = sf.read(b)
            sf.write(os.path.join(noisy_dir, f"{name}.wav"), data, sr)
            
        # Текст
        if col_txt:
            with open(os.path.join(txt_dir, f"{name}.txt"), "w") as f:
                f.write(str(row[col_txt]))
            
    except Exception as e:
        print(f"\n Ошибка на файле {i}: {e}")
        # Если структура вложенная, выведем пример одного ряда для диагностики
        if i == 0:
            print(f"Пример данных в колонке: {row[col_clean]}")

print(f"\n Финита! Файлы в: {os.path.abspath(base_dir)}")