import os
import random
import re
import glob

base_dir = "./data/voicebank"
clean_txt_dir = os.path.join(base_dir, "testset_txt")

# Папки для испорченных данных
out_del_dir = os.path.join(base_dir, "testset_txt_deleted")
out_sub_dir = os.path.join(base_dir, "testset_txt_substituted")
out_typo_dir = os.path.join(base_dir, "testset_txt_typos")

for d in [out_del_dir, out_sub_dir, out_typo_dir]:
    os.makedirs(d, exist_ok=True)

# общий словарь (Vocabulary)
txt_files = glob.glob(os.path.join(clean_txt_dir, "*.txt"))
if not txt_files:
    print(f"Не найдены текстовые файлы в {clean_txt_dir}")
    exit()

all_words = []
for file in txt_files:
    with open(file, 'r', encoding='utf-8') as f:
        text = f.read()
        #убираем пунктуацию
        words = re.findall(r'\b\w+\b', text.lower())
        all_words.extend(words)

# убираем дубликаты 
vocabulary = list(set(all_words))
print(f" Собран словарь из {len(vocabulary)} уникальных слов.")

# удаляет 1-2 случайных слова из предложения, если слов больше 3
def corrupt_deletion(words):
    
    if len(words) <= 3:
        return words
    
    num_to_delete = random.choice([1, 2])
    idx_to_delete = random.sample(range(len(words)), num_to_delete)
    
    return [word for i, word in enumerate(words) if i not in idx_to_delete]

# Заменяет 1-2 слова на абсолютно случайные из словаря 
def corrupt_substitution(words, vocab):
    
    if len(words) <= 2:
        return words
    
    res = words.copy()
    num_to_sub = random.choice([1, 2])
    idx_to_sub = random.sample(range(len(words)), num_to_sub)
    
    for idx in idx_to_sub:
        res[idx] = random.choice(vocab)
    return res


# Меняет или удаляет случайную букву в 1-2 длинных словах
def corrupt_typo(words):
    
    res = words.copy()
    # слова длиннее 4 символов
    long_words_idx = [i for i, w in enumerate(words) if len(w) > 4]
    
    if not long_words_idx:
        return words 
        
    num_to_typo = min(len(long_words_idx), random.choice([1, 2]))
    idx_to_typo = random.sample(long_words_idx, num_to_typo)
    
    for idx in idx_to_typo:
        word = list(res[idx])
        char_idx = random.randint(0, len(word) - 2)
        
        # 50% перестановка
        # 50% удаление
        if random.random() > 0.5:
            word[char_idx], word[char_idx+1] = word[char_idx+1], word[char_idx]
        else:
            word.pop(char_idx)
            
        res[idx] = "".join(word)
    return res


print("Ломаем текст ...")

for file_path in txt_files:
    filename = os.path.basename(file_path)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read().strip()
        
    # сохраняем пунктуацию, ломаем только слова
    
    words = text.split()
    
    # мутации
    del_text = " ".join(corrupt_deletion(words))
    sub_text = " ".join(corrupt_substitution(words, vocabulary))
    typo_text = " ".join(corrupt_typo(words))
    

    with open(os.path.join(out_del_dir, filename), 'w', encoding='utf-8') as f:
        f.write(del_text)
        
    with open(os.path.join(out_sub_dir, filename), 'w', encoding='utf-8') as f:
        f.write(sub_text)
        
    with open(os.path.join(out_typo_dir, filename), 'w', encoding='utf-8') as f:
        f.write(typo_text)

print("Текст успешно мутировал.")
print(f"Глянь папки {out_del_dir}, {out_sub_dir} и {out_typo_dir}")