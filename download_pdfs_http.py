import os, time, requests
from urllib.parse import quote
from tqdm import tqdm

LIST_FILE = "ids_networks.txt"
OUT_DIR = "pdfs"
os.makedirs(OUT_DIR, exist_ok=True)

def id_to_pdf_url(aid: str) -> str:
    # arXiv PDF-URL Schema ist stabil:
    #   https://arxiv.org/pdf/<ID>.pdf
    # IDs können Slash enthalten (alte IDs), deshalb URL-escapen:
    return f"https://arxiv.org/pdf/{quote(aid)}.pdf"

headers = {
    "User-Agent": "arxiv-bulk-download-for-research/1.0 (contact: you@example.com)"
}

with open(LIST_FILE) as f:
    ids = [line.strip() for line in f if line.strip()]

for aid in tqdm(ids, desc="Download PDFs"):
    url = id_to_pdf_url(aid)
    out = os.path.join(OUT_DIR, f"{aid.replace('/', '_')}.pdf")
    if os.path.exists(out) and os.path.getsize(out) > 0:
        continue
    try:
        r = requests.get(url, headers=headers, timeout=60)
        if r.status_code == 200 and r.headers.get("Content-Type","").lower().startswith("application/pdf"):
            with open(out, "wb") as w:
                w.write(r.content)
        else:
            tqdm.write(f"Skip {aid}: HTTP {r.status_code}")
        time.sleep(0.5)  # höfliche Rate-Limitierung
    except Exception as e:
        tqdm.write(f"Error {aid}: {e}")
