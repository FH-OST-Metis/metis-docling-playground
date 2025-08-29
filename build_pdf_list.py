import json, re, os, pandas as pd
from tqdm import tqdm

META = "data/arxiv-metadata-oai-snapshot.json"
OUT_DIR = "pdfs"
LIST_FILE = "ids_networks.txt"

os.makedirs(OUT_DIR, exist_ok=True)

# ---- Filter definieren ----
# arXiv-Kategorien: Netzwerke
KEEP_CATS = {"cs.SI", "cs.NI"}  # Social/Information Networks; Networking & Internet Architecture
# zusätzlich Keywords in Titel/Abstract
KEYWORDS = [
    r"\bnetwork(s)?\b",
    r"\bgraph(s)?\b",
    r"\bGNN(s)?\b",
    r"\bgraph neural",
    r"\bcommunity detection\b",
    r"\binformation network(s)?\b",
    r"\bsocial network(s)?\b",
]

kw_re = re.compile("|".join(KEYWORDS), re.IGNORECASE)

def match_paper(rec):
    cats = set((rec.get("categories") or "").split())
    if not (cats & KEEP_CATS):
        # wenn keine Netzwerkkategorie, dann per Keyword
        text = (rec.get("title") or "") + " " + (rec.get("abstract") or "")
        if not kw_re.search(text):
            return False
    return True

# ---- Metadaten streamen & filtern ----
ids = []
with open(META, "r") as f:
    for line in tqdm(f, desc="Filter metadata"):
        rec = json.loads(line)
        if match_paper(rec):
            # arXiv-ID normalisieren (z.B. '1707.08567' oder 'cs/0501001')
            aid = rec.get("id")
            if aid:
                ids.append(aid)

# Doppelte entfernen und etwas begrenzen (z.B. 1000 PDFs)
ids = pd.unique(pd.Series(ids)).tolist()
MAX_N = 200        # hier anpassen (z.B. 500, 2000, …)
ids = ids[:MAX_N]

with open(LIST_FILE, "w") as f:
    for aid in ids:
        f.write(aid.strip() + "\n")

print(f"Gespeichert: {len(ids)} IDs -> {LIST_FILE}")
