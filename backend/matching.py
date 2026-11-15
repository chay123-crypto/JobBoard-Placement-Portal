import os
from functools import lru_cache

import numpy as np
from pypdf.errors import PdfReadError, PdfStreamError

from backend.resume_parser import extract_skills, load_vocab, pdf_to_text

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class ResumeMatchingError(Exception):
    pass


@lru_cache(maxsize=1)
def get_model():
    from fastembed import TextEmbedding

    return TextEmbedding(model_name=MODEL_NAME)


def embed(texts):
    vectors = []
    for vector in get_model().embed(texts):
        vector = np.asarray(vector, dtype=np.float32)
        norm = np.linalg.norm(vector)
        if norm == 0:
            raise ValueError("The embedding model returned a zero vector")
        vectors.append(vector / norm)
    return vectors


def job_text(title, skills, description):
    return f"{title}. Skills: {skills or ''}. {(description or '')[:500]}"


def student_text(skills, branch):
    return f"Skills: {', '.join(skills or [])}. Branch: {branch or ''}."


def similarity_score(student_vec, job_vec):
    if student_vec is None or job_vec is None:
        return None
    score = float(np.dot(student_vec, job_vec))
    return max(0.0, min(100.0, (score - 0.15) / (0.6 - 0.15) * 100))


def match_category(score):
    if score is None:
        return None
    if score > 75:
        return "Great"
    if score >= 50:
        return "Good"
    return "Weak"


def compute_match_scores(student, drives, session):
    scores = {drive.drive_id: None for drive in drives}
    if not drives:
        return scores

    resume_path = student.resume_path or ""
    if os.path.splitext(resume_path)[1].lower() != ".pdf" or not os.path.isfile(resume_path):
        return scores

    try:
        with open(resume_path, "rb") as resume_file:
            resume_text = pdf_to_text(resume_file.read())
    except (PdfReadError, PdfStreamError, ValueError, EOFError) as exc:
        raise ResumeMatchingError("Could not read the saved PDF resume") from exc

    if len(resume_text.strip()) < 50:
        return scores

    skills = extract_skills(resume_text, load_vocab(session))
    texts = [student_text(skills, student.dept)]
    texts.extend(job_text(drive.jobtitle, drive.skills, drive.job_desc) for drive in drives)
    vectors = embed(texts)
    student_vector = vectors[0]
    return {drive.drive_id: similarity_score(student_vector, job_vector) for drive, job_vector in zip(drives, vectors[1:])}
