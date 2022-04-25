import os.path as osp
import os, json
from tqdm import tqdm


def fast_sort(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def get_links(keywords_file):
        # read search keywords from file
        with open(keywords_file, 'r', encoding='utf-8-sig') as f:
            text = f.read()
            lines = text.split('\n')
            lines = filter(lambda x: x != '' and x is not None, lines)
            links = fast_sort(lines)

        return links


file_root = "./collected_links"
dst_root = "./filtered_links"

file_list = {}
count = 1

with open("./keywords_collect/name_meta.json", 'r', encoding='utf-8-sig') as f:
    name_meta = json.load(f)

keywords = []
for k, v in name_meta.items():
    name_t = v["name"]
    keywords.append(name_t)

if not osp.exists(dst_root):
    os.makedirs(dst_root)

for idx, name in tqdm(enumerate(keywords)):
    person_id = idx + 1
    if osp.exists(osp.join(dst_root, f"p{person_id}.txt")):
        continue

    assert name == name_meta[f"p{person_id}"]["name"]

    links = get_links(osp.join(file_root, f"{name}.txt"))
    
    with open(osp.join(dst_root, f"p{person_id}.txt"), "w") as f:
        for linki in links:
            f.write(linki)
            f.write("\n")
