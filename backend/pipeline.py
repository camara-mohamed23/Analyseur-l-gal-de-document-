# backend/pipeline.py
import os, re, tempfile, subprocess
from typing import List, Dict, Tuple
import regex as re2

# Optionnel pour lire les PDF (pip install pymupdf)
try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "backend/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- Petites regex utiles (dates / montants) ---
MONEY_RE = re2.compile(r"""(?ix)
(?<!\w)(
  \d{1,3}(?:[ \.\u00A0]\d{3})*(?:,\d{2})? | \d+(?:,\d{2})?
)\s*(?:€|eur|euros?|euro)\b
""")
DATE_RE  = re2.compile(r"""(?ix)\b(
   \d{1,2}(?:er)?\s+(?:janv|févr|fev|mars|avr|mai|juin|juil|ao[uû]t|sept|oct|nov|d[ée]c)\w*\s+\d{4}
 | \d{1,2}/\d{1,2}/\d{4}
)\b""")

# --- Découpage des clauses (titres type Article 1, 2, etc.) ---
CLAUSE_HEAD_RE = re.compile(r"(?im)^(?:article|clause|section)\s+[0-9IVX\.\-]+.*$")

def _read_text_any(path: str) -> str:
    """Lit un .txt directement, ou un .pdf via PyMuPDF si dispo.
       Sinon renvoie du texte brut (best-effort)."""
    if path.lower().endswith(".pdf") and fitz:
        try:
            doc = fitz.open(path)
            return "\n".join(p.get_text("text") for p in doc)
        except Exception:
            pass
        # OCR (si 'ocrmypdf' installé sur ta machine — sinon saute)
        try:
            with tempfile.TemporaryDirectory() as tmp:
                ocred = os.path.join(tmp, "ocr.pdf")
                subprocess.run(["ocrmypdf", "--force-ocr", path, ocred], check=True)
                doc2 = fitz.open(ocred)
                return "\n".join(p.get_text("text") for p in doc2)
        except Exception:
            return ""
    # .txt ou fallback
    try:
        with open(path, "rb") as f:
            return f.read().decode("utf-8", errors="ignore")
    except Exception:
        return ""

def detect_language(text: str) -> str:
    return "fr" if re.search(r"\b(le|la|les|de|des|contrat|loi|article)\b", (text or "").lower()) else "en"

def split_clauses(text: str) -> List[Dict]:
    lines = (text or "").splitlines()
    idxs = [i for i, l in enumerate(lines) if CLAUSE_HEAD_RE.search(l)]
    idxs = [0] + idxs + [len(lines)]
    out = []
    for order, (a, b) in enumerate(zip(idxs, idxs[1:])):
        chunk = "\n".join(lines[a:b]).strip()
        if not chunk:
            continue
        title = lines[a].strip() if a != 0 else "Préambule"
        out.append({"title": title, "text": chunk, "order_index": order})
    return out

def summarize_text(txt: str, max_chars=1800) -> str:
    """Résumé simple (sans lib externe) : prend les 4 plus gros paragraphes."""
    t = (txt or "")[:max_chars]
    paras = [p.strip() for p in t.split("\n") if p.strip()]
    if not paras:
        return t[:300]
    top = sorted(paras, key=len, reverse=True)[:4]
    return " ".join(top)

def extract_entities(text: str) -> Dict:
    """Pas de spaCy. On extrait au moins MONEY et DATE via regex."""
    txt = text or ""
    amounts = [m.group(0) for m in MONEY_RE.finditer(txt)]
    dates   = [d.group(0) for d in DATE_RE.finditer(txt)]
    ents = []
    for a in amounts:
        start = txt.find(a); end = start + len(a)
        ents.append({"text": a, "label": "MONEY", "start": start, "end": end})
    for d in dates:
        start = txt.find(d); end = start + len(d)
        ents.append({"text": d, "label": "DATE", "start": start, "end": end})
    return {"ents": ents, "amounts": amounts, "dates": dates}

def apply_rules(text: str, clauses: List[Dict], rules_path="backend/rules.yaml") -> List[Dict]:
    """Règles simples. Si le fichier rules.yaml est absent → pas d'erreur."""
    risks = []
    try:
        import yaml
        if os.path.exists(rules_path):
            rules = yaml.safe_load(open(rules_path, encoding="utf-8")) or {}
        else:
            rules = {}
    except Exception:
        rules = {}

    def has_any(keywords: List[str]) -> bool:
        corpus = (text or "").lower()
        return any(k.lower() in corpus for k in (keywords or []))

    for code, kw in (rules.get("must_have") or {}).items():
        if not has_any(kw):
            risks.append({"code": f"MISSING_{str(code).upper()}",
                          "level": "MEDIUM",
                          "message": f"Clause obligatoire manquante: {code}"})
    for code, kw in (rules.get("red_flags") or {}).items():
        if has_any(kw):
            risks.append({"code": str(code).upper(),
                          "level": "HIGH",
                          "message": f"Signal/risque détecté: {code}"})
    return risks

def analyze(path: str) -> Tuple[str, str, list, dict, list]:
    """Fonction appelée par app.py"""
    text = _read_text_any(path)
    language = detect_language(text)
    clauses = split_clauses(text)
    summary_global = summarize_text(text)
    entities = extract_entities(text)
    for c in clauses[:12]:
        c["summary"] = summarize_text(c["text"])
    risks = apply_rules(text, clauses)
    return language, summary_global, clauses, entities, risks
