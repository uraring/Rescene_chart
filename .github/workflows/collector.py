import os, json, datetime, re, requests
from bs4 import BeautifulSoup

HISTORY_FILE = "melon_rank_history.json"

ARTISTS = {
    "RESCENE": ["RESCENE", "리센느"],
    "IVE": ["IVE", "아이브"],
    "aespa": ["aespa", "에스파"],
    "QWER": ["QWER"]
}

def clean_txt(s):
    return re.sub(r'\s+', ' ', s or '').strip()

def fetch_melon_top100():
    chart = []
    url = "https://www.melon.com/chart/index.htm"
    hdr = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://www.google.com/"
    }
    res = requests.get(url, headers=hdr, timeout=10)
    if res.status_code == 200:
        soup = BeautifulSoup(res.text, "html.parser")
        for tr in soup.select("tr.lst50, tr.lst100"):
            rk = tr.select_one("span.rank")
            tl = tr.select_one("div.ellipsis.rank01 a")
            at = tr.select_one("div.ellipsis.rank02 a")
            if rk and tl and at:
                chart.append({
                    "rank": int(rk.text.strip()),
                    "title": clean_txt(tl.text),
                    "artist": clean_txt(at.text)
                })
    return chart

def main():
    history = {}
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = {}

    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    cur_key = now.strftime("%Y-%m-%d %H:00")

    m_all = fetch_melon_top100()
    if not m_all:
        return

    for art, names in ARTISTS.items():
        if art not in history:
            history[art] = {}

        nms = [clean_txt(n).lower().replace(" ", "") for n in names]
        matched = [i for i in m_all if any(n in clean_txt(i["artist"]).lower().replace(" ", "") for n in nms)]

        slot_ranks = {}
        for item in matched:
            slot_ranks[item["title"]] = item["rank"]

        if slot_ranks:
            history[art][cur_key] = slot_ranks

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    print(f"Updated {cur_key} successfully.")

if __name__ == "__main__":
    main()
