# Simple moteur TF-IDF sans dépendances lourdes (no numpy/scipy/torch)
import math, re
from typing import List, Tuple, Dict, Any

TOKEN_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+")

def _tokenize(text: str) -> List[str]:
    return [t.lower() for t in TOKEN_RE.findall(text or "")]

class ClauseIndex:
    def __init__(self, index_dir: str = "backend/indexes"):
        self.index_dir = index_dir  # pas utilisé ici, mais gardé pour compat
        self.docs: List[Tuple[int, int, str, str]] = []  # (doc_id, clause_id, title, text)
        self.df: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.vectors: List[Dict[str, float]] = []  # TF-IDF par clause
        self.norms: List[float] = []

    def load(self):
        # Rien à charger pour cette version simplifiée
        pass

    def build(self, meta: List[Tuple[int, int, str, str]]):
        self.docs = meta[:]  # [(document_id, clause_id, title, text)]
        self.df.clear()
        self.idf.clear()
        self.vectors.clear()
        self.norms.clear()

        # 1) DF
        for _, _, _, text in self.docs:
            toks = set(_tokenize(text))
            for t in toks:
                self.df[t] = self.df.get(t, 0) + 1

        # 2) IDF
        N = max(len(self.docs), 1)
        for t, df in self.df.items():
            self.idf[t] = math.log((N + 1) / (df + 1)) + 1.0  # lisse légèrement

        # 3) TF-IDF par clause
        for _, _, _, text in self.docs:
            vec: Dict[str, float] = {}
            toks = _tokenize(text)
            if not toks:
                self.vectors.append(vec)
                self.norms.append(0.0)
                continue
            tf: Dict[str, int] = {}
            for t in toks:
                tf[t] = tf.get(t, 0) + 1
            max_tf = max(tf.values())
            for t, f in tf.items():
                tf_norm = 0.5 + 0.5 * (f / max_tf)  # tf normalisé
                vec[t] = tf_norm * self.idf.get(t, 0.0)
            # norme
            norm = math.sqrt(sum(w * w for w in vec.values()))
            self.vectors.append(vec)
            self.norms.append(norm)

    def _cosine(self, qv: Dict[str, float], qn: float, dv: Dict[str, float], dn: float) -> float:
        if qn == 0.0 or dn == 0.0:
            return 0.0
        # produit scalaire
        num = 0.0
        # itérer sur le plus petit dict pour la perf
        if len(qv) < len(dv):
            for t, w in qv.items():
                if t in dv:
                    num += w * dv[t]
        else:
            for t, w in dv.items():
                if t in qv:
                    num += w * qv[t]
        return num / (qn * dn)

    def search(self, q: str, k: int = 5) -> List[Dict[str, Any]]:
        # TF-IDF de la requête
        qtoks = _tokenize(q)
        if not qtoks:
            return []
        qtf: Dict[str, int] = {}
        for t in qtoks:
            qtf[t] = qtf.get(t, 0) + 1
        max_qtf = max(qtf.values())
        qvec: Dict[str, float] = {}
        for t, f in qtf.items():
            tf_norm = 0.5 + 0.5 * (f / max_qtf)
            qvec[t] = tf_norm * self.idf.get(t, 0.0)
        qnorm = math.sqrt(sum(w * w for w in qvec.values()))

        # scores
        scored: List[Tuple[float, int]] = []
        for i, dv in enumerate(self.vectors):
            s = self._cosine(qvec, qnorm, dv, self.norms[i])
            if s > 0:
                scored.append((s, i))
        scored.sort(reverse=True)
        top = scored[:k]

        # format de sortie
        hits: List[Dict[str, Any]] = []
        for score, idx in top:
            doc_id, clause_id, title, text = self.docs[idx]
            snippet = text[:300].replace("\n", " ")
            hits.append({
                "document_id": doc_id,
                "clause_id": clause_id,
                "title": title,
                "snippet": snippet,
                "score": float(round(score, 6)),
            })
        return hits
