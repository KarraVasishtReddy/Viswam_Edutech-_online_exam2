import os, tempfile

os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "t.db")
os.environ["JWT_SECRET"] = "test-secret-test-secret-test-secret-1234"
os.environ["SEED_DEMO"] = "1"

import pytest
from fastapi.testclient import TestClient
import main

PAPER = dict(id="p1", title="T", subject="S", duration=30, passPct=40, shuffle=True, status="published",
             questions=[dict(id="q1", text="2+2?", type="mcq", marks=2, options=["3", "4", "5", "6"], correct=1),
                        dict(id="q2", text="pi", type="numeric", marks=1, answer="3.14"),
                        dict(id="q3", text="define", type="short", marks=2, answer="cell, membrane")])
PAPER["class"] = "10"


@pytest.fixture(scope="module")
def c():
    with TestClient(main.app) as client:
        yield client


def tok(c, e, p, r):
    j = c.post("/api/login", json=dict(email=e, password=p, role=r)).json()
    return {"Authorization": "Bearer " + j["token"]}


def test_full_flow(c):
    a = tok(c, "admin@school.edu", "admin123", "admin")
    s = tok(c, "john@school.edu", "student123", "student")
    assert c.post("/api/login", json=dict(email="john@school.edu", password="x", role="student")).status_code == 401
    assert c.post("/api/papers", json=PAPER, headers=a).status_code == 200
    assert c.post("/api/papers", json=PAPER, headers=s).status_code == 403
    sp = c.get("/api/papers", headers=s).json()
    assert all("correct" not in q and "answer" not in q for q in sp[0]["questions"])
    assert c.post("/api/exams/p1/start", headers=s).status_code == 200
    assert c.post("/api/violations", json={"type": "Tab switch"}, headers=s).json()["count"] == 1
    assert c.put("/api/exams/session", json={"a": {"q1": 1, "q2": "3.14", "q3": "the cell membrane"}, "i": 1}, headers=s).json()["ok"]
    assert c.post("/api/exams/submit", headers=s).status_code == 200
    assert c.post("/api/exams/p1/start", headers=s).status_code == 409
    r = c.get("/api/results", headers=a).json()[0]
    assert (r["marks"], r["total"], r["pct"], r["pass"], r["viol"]) == (5, 5, 100, True, 1)
    assert "answers" not in c.get("/api/results", headers=s).json()[0]
    assert c.patch(f"/api/results/{r['id']}/marks", json={"index": 2, "marks": 1}, headers=a).status_code == 200
    assert c.get("/api/results", headers=a).json()[0]["marks"] == 4


def test_bulk_and_auth(c):
    a = tok(c, "admin@school.edu", "admin123", "admin")
    j = c.post("/api/students/bulk", json={"rows": [["a@x.com", "A", "B", "ID9", "10"], ["bad", "x", "y", "1", "1"]]}, headers=a).json()
    assert j == {"added": 1, "skipped": 1}
    assert c.get("/api/papers").status_code == 401
    assert c.get("/").status_code == 200
