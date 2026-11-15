import io
import re

from pypdf import PdfReader
from sqlalchemy import select

from backend.models.models import PlacementDrive

SEED = {
    "python", "java", "javascript", "typescript", "sql", "postgresql", "mongodb",
    "react", "vue", "node.js", "fastapi", "flask", "django", "docker", "git", "sqlite",
    "aws", "linux", "c++", "c#", "machine learning", "deep learning", "pandas",
    "numpy", "pytorch", "tensorflow", "html", "css", "tailwind", "rest api",
    "scikit-learn", "langchain", "langgraph", "chromadb", "faiss", "computer networks",
    "networking", "crewai", "azure", "jenkins", "github actions", "devops", "kali",
    "metasploit", "operating systems", "object oriented programming", "go", "kotlin",
    "react-native",
}

ALIASES = {
    "js": "javascript",
    "ts": "typescript",
    "postgres": "postgresql",
    "os": "operating systems",
    "ml": "machine learning",
    "dl": "deep learning",
    "nodejs": "node.js",
}

CGPA_RE = re.compile(
    r"(?:cgpa|gpa)\s*[:\-]?\s*(\d{1,2}(?:\.\d{1,2})?)(?![\d.])(?!\s*/\s*4)",
    re.IGNORECASE,
)


def pdf_to_text(data, max_pages=5):
    reader = PdfReader(io.BytesIO(data))
    return "\n".join((page.extract_text() or "") for page in reader.pages[:max_pages])


def load_vocab(session):
    rows = session.scalars(
        select(PlacementDrive.skills).where(PlacementDrive.skills.isnot(None))
    ).all()
    vocab = set(SEED)
    for row in rows:
        vocab.update(
            skill.strip().lower()
            for skill in re.split(r"[,;\n|]", row)
            if len(skill.strip()) >= 2
        )
    return vocab


def _has(term, text):
    pattern = rf"(?<![a-z0-9+#.]){re.escape(term)}(?![a-z0-9+#])"
    return re.search(pattern, text) is not None


def extract_skills(raw, vocab):
    text = raw.lower()
    found = {skill for skill in vocab if _has(skill, text)}
    found.update(
        canonical
        for alias, canonical in ALIASES.items()
        if _has(alias, text)
    )
    return sorted(found)


def extract_cgpa(raw):
    match = CGPA_RE.search(raw)
    if match:
        value = float(match.group(1))
        if 0 < value <= 10:
            return value
    return None


def extract_grad_year(raw):
    years = [
        int(year)
        for year in re.findall(r"\b(20[2-3]\d)\b", raw)
        if 2024 <= int(year) <= 2035
    ]
    return max(years) if years else None
