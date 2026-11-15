from types import SimpleNamespace
from unittest.mock import patch

import numpy as np

from backend.matching import compute_match_scores, match_category, similarity_score


def test_similarity_score_uses_the_configured_scale():
    assert similarity_score(np.array([1.0, 0.0]), np.array([0.6, 0.8])) == 100
    assert similarity_score(np.array([1.0, 0.0]), np.array([0.15, 0.8])) == 0


def test_match_categories_follow_requested_thresholds():
    assert match_category(75.01) == "Great"
    assert match_category(75) == "Good"
    assert match_category(50) == "Good"
    assert match_category(49.99) == "Weak"
    assert match_category(None) is None


def test_match_scores_use_resume_skills_and_drive_text(tmp_path):
    resume_path = tmp_path / "resume.pdf"
    resume_path.write_bytes(b"%PDF-1.7 placeholder")
    student = SimpleNamespace(resume_path=str(resume_path), dept="CSE")
    drive = SimpleNamespace(
        drive_id=7,
        jobtitle="Backend Engineer",
        skills="Python, Flask",
        job_desc="Build APIs",
    )
    vectors = [
        np.array([1.0, 0.0]),
        np.array([0.6, 0.8]),
    ]

    with (
        patch("backend.matching.pdf_to_text", return_value="Python Flask developer " * 5),
        patch("backend.matching.load_vocab", return_value={"python", "flask"}),
        patch("backend.matching.embed", return_value=vectors) as embed_mock,
    ):
        scores = compute_match_scores(student, [drive], session=object())

    assert scores == {7: 100.0}
    assert embed_mock.call_args.args[0] == [
        "Skills: flask, python. Branch: CSE.",
        "Backend Engineer. Skills: Python, Flask. Build APIs",
    ]


def test_missing_pdf_returns_no_score_without_loading_model():
    student = SimpleNamespace(resume_path="", dept="CSE")
    drive = SimpleNamespace(drive_id=7)

    with patch("backend.matching.embed") as embed_mock:
        scores = compute_match_scores(student, [drive], session=object())

    assert scores == {7: None}
    embed_mock.assert_not_called()
