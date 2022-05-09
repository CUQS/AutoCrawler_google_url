from concurrent.futures import thread
import os, json
import os.path as osp
import threading
import time
from sympy import re
from tqdm import tqdm
from tabulate import tabulate
from datetime import datetime

import requests
import base64
import shutil
import argparse


threading_end_count = [0]

file_root = "./filtered_links"
dst_root = "./raw_images"


def get_links(file, top=100):
    with open(file, 'r', encoding='utf-8-sig') as f:
        text = f.read()
        lines = text.split('\n')
        lines = filter(lambda x: x != '' and x is not None, lines)
    
    return [li for li in lines]


def chunkify(lst, n):
    return [lst[i::n] for i in range(n)]


def base64_to_object(src):
    header, encoded = str(src).split(',', 1)
    data = base64.decodebytes(bytes(encoded, encoding='utf-8'))
    return data


def get_extension_from_link(link, default='jpg'):
    splits = str(link).split('.')
    if len(splits) == 0:
        return default
    ext = splits[-1].lower()
    if ext == 'jpg' or ext == 'jpeg':
        return 'jpg'
    elif ext == 'gif':
        return 'gif'
    elif ext == 'png':
        return 'png'
    else:
        return default


def save_object_to_file(object, file_path, is_base64=False):
    try:
        with open('{}'.format(file_path), 'wb') as file:
            if is_base64:
                file.write(object)
            else:
                shutil.copyfileobj(object.raw, file)
    except Exception as e:
        pass


def download_process(thread_list, thread_idx, top_download=100):
    start = [time.time()]
    end = [start[0]]

    for fi in thread_list:
        count = 1

        key = fi.split(".")[0]
        url_links = get_links(osp.join(file_root, fi))

        dst_dir = osp.join(dst_root, key)

        if not osp.exists(dst_dir):
            os.makedirs(dst_dir)

        file_exist = [fi.split(".")[0] for fi in os.listdir(dst_dir)]

        status[thread_idx][3] = len(url_links)

        for idx, li in enumerate(url_links):
            idx_t = idx + 1
            image_idx = osp.join(dst_dir, f"{key}_{idx_t}")
            if not image_idx in file_exist:
                try:
                    if str(li).startswith('data:image/jpeg;base64'):
                        response = base64_to_object(li)
                        ext = 'jpg'
                        is_base64 = True
                    elif str(li).startswith('data:image/png;base64'):
                        response = base64_to_object(li)
                        ext = 'png'
                        is_base64 = True
                    else:
                        response = requests.get(li, stream=True)
                        ext = get_extension_from_link(li)
                        is_base64 = False
                    
                    save_object_to_file(response, f'{image_idx}.{ext}', is_base64=is_base64)
                    count += 1
                except:
                    pass
            else:
                count += 1
            status[thread_idx][2] = idx_t
            if status_update_time[1] - status_update_time[0] > 5:
                print("|--------------+--------------+------------+------------|")
                now = datetime.now()
                date_time = now.strftime("%Y/%m/%d,  %H:%M:%S")
                print("|------------------{}----------------|".format(date_time))
                print("|--------------+--------------+------------+------------|")
                print(tabulate(status, headers=['folder now', 'folder all', 'link now', 'link all'], tablefmt='orgtbl'))
                print("|--------------+--------------+------------+------------|")
                status_update_time[0] = time.time()
            # if count >= top_download + 1:
            #     break
        
        status[thread_idx][0] += 1

        end[0] = time.time()
        if (end[0] - start[0]) // 60 > 5:
            time.sleep(60)
            start[0] = time.time()
    
    threading_end_count[0] += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--download_single', type=str, default="", help="download single file by name tag")
    parser.add_argument('--download_all', action='store_true', help="download all files")
    args = parser.parse_args()

    thread_num = 4
    top_download = 100

    if not osp.exists(dst_root):
        os.makedirs(dst_root)

    thread_list_all = []

    print("--> get file links...")

    for fi in tqdm(os.listdir(file_root)):
        if not args.download_all and fi.split(".")[0] != args.download_single:
            continue
        thread_list_all.append(fi)

    thread_list_split = chunkify(thread_list_all, thread_num)
    status = [[0, len(ti), 0, 0] for ti in thread_list_split]
    status_update_time = [time.time(), time.time()]
    
    for idx, ti in enumerate(thread_list_split):
        print(f"--> thread {idx} start ...")
        th = threading.Thread(target=download_process, args=(ti, idx, top_download,))
        th.start()
        time.sleep(3)
    
    while threading_end_count[0] < thread_num:
        status_update_time[1] = time.time()
        continue


