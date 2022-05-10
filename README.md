# AutoCrawler_google_url

- Modified from [AutoCrawler](https://github.com/YoongiKim/AutoCrawler)
- Split the search part and download part, and only search from google

# How to use

1. Install Chrome

2. pip install -r requirements.txt

3. Write search keywords in `keywords_collect/name_meta.json`

4. Permission

    ```bash
    chmod 755 chromedriver/*
    ```

5. **Run "main.py"**

    ```bash
    python3 main.py [--skip true] [--threads 4] [--face false] [--no_gui auto] [--limit 0]
    # example
    python main.py --skip true --threads 2 --face false --no_gui auto --limit 0
    ```

6. URL links will be downloaded to 'collected_links' directory.

7. **Run "check_collected.py"**
    > `python check_collected.py`

8. **Run "download_links.py"**
    > `python download_links.py --download_all`

    - Download single keyword
  
    > `python download_links.py --download_single p2`

# Arguments

```
--skip true              Skips keyword if downloaded directory already exists. This is needed
                         when re-downloading.

--threads 4              Number of threads to download.

--face false             Face search mode

--no_gui auto            No GUI mode. (headless mode) Acceleration for full_resolution mode,
                         but unstable on thumbnail mode.
                         Default: "auto" - false if full=false, true if full=true
                         (can be used for docker linux system)
                   
--limit 0                Maximum count of images to download per site. (0: infinite)
--proxy-list ''          The comma separated proxy list like: "socks://127.0.0.1:1080,http://127.0.0.1:1081".
                         Every thread will randomly choose one from the list.
--print_url false        print download process with url      
```

# Remote crawling through SSH on your server

```
sudo apt-get install xvfb <- This is virtual display

sudo apt-get install screen <- This will allow you to close SSH terminal while running.

screen -S s1

Xvfb :99 -ac & DISPLAY=:99 python3 main.py
```

# Customize

You can make your own crawler by changing collect_links.py

# Issues

As google site consistently changes, please make issues if it doesn't work.
