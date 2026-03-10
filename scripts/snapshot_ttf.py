import csv
import os
import re
from datetime import datetime, timezone
from urllib.request import urlopen, Request
import json
from pathlib import Path

ICE_URL = "https://www.ice.com/marketdata/api/productguide/charting/contract-data?productId=4331&hubId=7979"

# Monthly examples: Feb26, Mar26, Apr27 ...
MONTHLY_RE = re.compile(r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\d{2}$")

# Calendar examples: Cal26, Cal27 ...
CAL_RE = re.compile(r"^Cal\s?\d{2}$")

def fetch_json(url: str):
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

def is_month_or_calendar(market_strip: str) -> bool:
    s = (market_strip or "").strip()
    return bool(MONTHLY_RE.match(s) or CAL_RE.match(s))

def main():
    data = fetch_json(ICE_URL)

    monthly_or_cal = [x for x in data if is_month_or_calendar(str(x.get("marketStrip", "")))]

    now_utc = datetime.now(timezone.utc)
    stamp = now_utc.strftime("%Y-%m-%d_%H%M")
    out_dir = "snapshots"
    history_path = "snapshots/ttf_curve_history.csv"
    required_fields = ["snapshot_utc", "marketStrip", "lastPrice", "change", "volume", "lastTime", "endDate", "marketId"]
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"ttf_curve_{stamp}_utc.csv")

    fieldnames = [
        "snapshot_utc",
        "marketStrip",
        "lastPrice",
        "change",
        "volume",
        "lastTime",
        "endDate",
        "marketId",
    ]

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for x in monthly_or_cal:
            row = {
                "snapshot_utc": now_utc.isoformat(),
                "marketStrip": x.get("marketStrip"),
                "lastPrice": x.get("lastPrice"),
                "change": x.get("change"),
                "volume": x.get("volume"),
                "lastTime": x.get("lastTime"),
                "endDate": x.get("endDate"),
                "marketId": x.get("marketId"),
            }
            w.writerow(row)

    print(f"Wrote {out_path} ({len(monthly_or_cal)} rows)")

if __name__ == "__main__":
    main()
