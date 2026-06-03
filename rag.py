import os

def load_rag():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    doc_path = os.path.join(base_dir, "docs", "dokdo_all.txt")
    with open(doc_path, encoding="utf-8") as f:
        content = f.read()
    return content

def search_docs(content, query):
    paragraphs = [p.strip() for p in content.split("\n") if len(p.strip()) > 20]
    query_words = query.lower().split()
    scored = []
    for p in paragraphs:
        score = sum(1 for w in query_words if w in p.lower())
        if score > 0:
            scored.append((score, p))
    scored.sort(reverse=True)
    top = [p for _, p in scored[:5]]
    return "\n".join(top) if top else ""