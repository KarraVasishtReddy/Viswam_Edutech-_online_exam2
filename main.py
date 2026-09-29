"""Viswam EduTech Online Exam - backend API (FastAPI + SQLite).
Run:  uvicorn main:app --host 0.0.0.0 --port 8000
Env:  JWT_SECRET (required in prod), ADMIN_EMAIL, ADMIN_PASSWORD, SEED_DEMO=0|1,
      DB_PATH, MAX_VIOLATIONS, TZ_NAME, ALLOWED_ORIGINS (only if front end is hosted elsewhere)
"""
import os, json, time, hmac, hashlib, secrets, sqlite3, random
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import jwt
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

DB_PATH = os.environ.get("DB_PATH", "exam.db")
SECRET = os.environ.get("JWT_SECRET") or secrets.token_hex(32)  # set JWT_SECRET so logins survive restarts
MAXV = int(os.environ.get("MAX_VIOLATIONS", 3))
TZ = ZoneInfo(os.environ.get("TZ_NAME", "Asia/Kolkata"))
GRACE_MS = 5000

app = FastAPI(title="Viswam EduTech Exam API")
origins = [o for o in os.environ.get("ALLOWED_ORIGINS", "").split(",") if o]
if origins:
    app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"])

# ---------------- db / auth helpers ----------------
def hash_pw(pw, salt=None):
    salt = salt or secrets.token_hex(8)
    return f"{salt}${hashlib.pbkdf2_hmac('sha256', pw.encode(), salt.encode(), 100_000).hex()}"

def check_pw(pw, stored):
    try:
        return hmac.compare_digest(hash_pw(pw, stored.split("$")[0]), stored)
    except Exception:
        return False

def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

def get_db():
    c = conn()
    try:
        yield c
        c.commit()
    finally:
        c.close()

@app.on_event("startup")
def startup():
    c = conn()
    c.executescript("""
    create table if not exists users(email text primary key,name text,role text,pw text,sid text,"class" text);
    create table if not exists papers(id text primary key,status text,data text);
    create table if not exists sessions(email text primary key,pid text,start integer,data text);
    create table if not exists results(id integer primary key autoincrement,email text,pid text,data text);
    create unique index if not exists ux_attempt on results(email,pid);
    create table if not exists viol(id integer primary key autoincrement,t integer,email text,paper text,type text);
    """)
    if not c.execute("select 1 from users").fetchone():
        ins = "insert into users values(?,?,?,?,?,?)"
        c.execute(ins, (os.environ.get("ADMIN_EMAIL", "admin@school.edu").lower(), "Admin", "admin",
                        hash_pw(os.environ.get("ADMIN_PASSWORD", "admin123")), "", ""))
        if os.environ.get("SEED_DEMO", "1") == "1":
            c.execute(ins, ("john@school.edu", "John Doe", "student", hash_pw("student123"), "S001", "10"))
    c.commit(); c.close()

def now_ms():
    return int(time.time() * 1000)

def user(authorization: str = Header(None)):
    try:
        return jwt.decode(authorization.split()[1], SECRET, algorithms=["HS256"])
    except Exception:
        raise HTTPException(401, "Session expired - please log in again")

def admin(u=Depends(user)):
    if u["role"] != "admin":
        raise HTTPException(403, "Admins only")
    return u

def student(u=Depends(user)):
    if u["role"] != "student":
        raise HTTPException(403, "Students only")
    return u

FAILS = {}
def throttle(key):
    now = time.time()
    FAILS[key] = [t for t in FAILS.get(key, []) if now - t < 300]
    if len(FAILS[key]) >= 5:
        raise HTTPException(429, "Too many failed attempts. Try again in 5 minutes.")

# ---------------- auth ----------------
class Login(BaseModel):
    email: str
    password: str
    role: str

@app.post("/api/login")
def login(b: Login, c=Depends(get_db)):
    email = b.email.strip().lower()
    throttle(email)
    u = c.execute("select * from users where email=? and role=?", (email, b.role)).fetchone()
    if not u or not check_pw(b.password, u["pw"]):
        FAILS.setdefault(email, []).append(time.time())
        raise HTTPException(401, "Invalid credentials")
    usr = {"email": u["email"], "name": u["name"], "role": u["role"]}
    tok = jwt.encode({**usr, "exp": datetime.now(timezone.utc) + timedelta(hours=12)}, SECRET, algorithm="HS256")
    return {"token": tok, "user": usr}

@app.get("/api/time")
def server_time():
    return {"now": now_ms()}

# ---------------- papers ----------------
def strip(p):
    p = json.loads(json.dumps(p))
    for q in p["questions"]:
        q.pop("correct", None); q.pop("answer", None)
    return p

def paper_of(c, pid):
    r = c.execute("select data from papers where id=?", (pid,)).fetchone()
    return json.loads(r["data"]) if r else None

@app.get("/api/papers")
def list_papers(u=Depends(user), c=Depends(get_db)):
    ps = [json.loads(r["data"]) for r in c.execute("select data from papers").fetchall()]
    if u["role"] == "admin":
        return ps
    return [strip(p) for p in ps if p.get("status") == "published"]

@app.post("/api/papers")
def save_paper(p: dict, u=Depends(admin), c=Depends(get_db)):
    if not str(p.get("id", "")).strip() or not p.get("title") or not isinstance(p.get("questions"), list) or not p["questions"]:
        raise HTTPException(422, "Invalid paper")
    if p.get("status") not in ("draft", "published"):
        raise HTTPException(422, "Invalid status")
    c.execute("insert into papers(id,status,data) values(?,?,?) on conflict(id) do update set status=excluded.status,data=excluded.data",
              (p["id"], p["status"], json.dumps(p)))
    return {"ok": True}

@app.delete("/api/papers/{pid}")
def delete_paper(pid: str, u=Depends(admin), c=Depends(get_db)):
    c.execute("delete from papers where id=?", (pid,))
    return {"ok": True}

# ---------------- students ----------------
class Bulk(BaseModel):
    rows: list[list[str]]

@app.get("/api/students")
def list_students(u=Depends(admin), c=Depends(get_db)):
    return [dict(r) for r in c.execute("select email,name,role,sid,\"class\" from users where role='student' order by name")]

@app.post("/api/students/bulk")
def bulk_students(b: Bulk, u=Depends(admin), c=Depends(get_db)):
    added = skipped = 0
    for r in b.rows:
        r = [x.strip() for x in r] + [""] * 5
        e = r[0].lower()
        if "@" not in e or not r[3] or c.execute("select 1 from users where email=?", (e,)).fetchone():
            skipped += 1
            continue
        c.execute("insert into users values(?,?,?,?,?,?)", (e, f"{r[1]} {r[2]}".strip(), "student", hash_pw(r[3]), r[3], r[4]))
        added += 1
    return {"added": added, "skipped": skipped}

# ---------------- exam sessions ----------------
def load_session(c, email):
    r = c.execute("select * from sessions where email=?", (email,)).fetchone()
    return {"email": email, "pid": r["pid"], "start": r["start"], **json.loads(r["data"])} if r else None

def store_session(c, s):
    c.execute("update sessions set data=? where email=?",
              (json.dumps({k: s[k] for k in ("order", "a", "i", "v")}), s["email"]))

@app.post("/api/exams/{pid}/start")
def start_exam(pid: str, u=Depends(student), c=Depends(get_db)):
    p = paper_of(c, pid)
    if not p or p.get("status") != "published":
        raise HTTPException(404, "Paper not available")
    if c.execute("select 1 from results where email=? and pid=?", (u["email"], pid)).fetchone():
        raise HTTPException(409, "You have already attempted this exam")
    s = load_session(c, u["email"])
    if s:
        if s["pid"] != pid:
            raise HTTPException(409, "Finish your current exam first")
        return {"ok": True}
    order = [q["id"] for q in p["questions"]]
    if p.get("shuffle"):
        random.shuffle(order)
    c.execute("insert into sessions values(?,?,?,?)",
              (u["email"], pid, now_ms(), json.dumps({"order": order, "a": {}, "i": 0, "v": 0})))
    return {"ok": True}

@app.get("/api/sessions")
def sessions(u=Depends(user), c=Depends(get_db)):
    if u["role"] == "admin":
        return [load_session(c, r["email"]) for r in c.execute("select email from sessions").fetchall()]
    s = load_session(c, u["email"])
    return [s] if s else []

class Save(BaseModel):
    a: dict
    i: int = 0

@app.put("/api/exams/session")
def save_session(b: Save, u=Depends(student), c=Depends(get_db)):
    s = load_session(c, u["email"])
    if not s:
        raise HTTPException(404, "No active exam")
    p = paper_of(c, s["pid"])
    if now_ms() > s["start"] + p["duration"] * 60000 + GRACE_MS:
        return {"ok": False, "expired": True}
    valid = set(s["order"])
    s["a"] = {k: (v if isinstance(v, int) else v[:5000]) for k, v in b.a.items()
              if k in valid and isinstance(v, (int, str))}
    s["i"] = max(0, min(b.i, len(s["order"]) - 1))
    store_session(c, s)
    return {"ok": True}

class Viol(BaseModel):
    type: str

@app.post("/api/violations")
def add_violation(b: Viol, u=Depends(student), c=Depends(get_db)):
    s = load_session(c, u["email"])
    if not s:
        raise HTTPException(404, "No active exam")
    p = paper_of(c, s["pid"]) or {}
    t = b.type[:60]
    c.execute("insert into viol(t,email,paper,type) values(?,?,?,?)", (now_ms(), u["email"], p.get("title", ""), t))
    if t != "Copy/paste attempt":
        s["v"] += 1
        store_session(c, s)
    return {"count": s["v"], "autosubmit": s["v"] >= MAXV}

@app.get("/api/violations")
def list_violations(u=Depends(admin), c=Depends(get_db)):
    return [dict(r) for r in c.execute("select t,email,paper,type from viol order by id desc limit 1000")]

# ---------------- grading / results ----------------
def grade(q, a):
    s = str(a if a is not None else "").strip()
    if not s:
        return 0
    m = q.get("marks", 0)
    if q["type"] == "mcq":
        return m if isinstance(a, int) and a == q.get("correct") else 0
    if q["type"] == "numeric":
        try:
            given, want = float(s), float(q.get("answer"))
        except (TypeError, ValueError):
            return 0
        return m if abs(given - want) <= max(abs(want) * 0.01, 1e-9) else 0
    kw = [k.strip().lower() for k in str(q.get("answer", "")).split(",") if k.strip()]
    if not kw:
        return 0
    return round(m * sum(k in s.lower() for k in kw) / len(kw) * 2) / 2

@app.post("/api/exams/submit")
def submit_exam(u=Depends(student), c=Depends(get_db)):
    s = load_session(c, u["email"])
    if not s:
        raise HTTPException(404, "No active exam")
    p = paper_of(c, s["pid"])
    qs, answers = p["questions"], []
    for q in qs:
        g = s["a"].get(q["id"])
        given = "" if g is None else str(g)
        if q["type"] == "mcq":
            ok = isinstance(g, int) and 0 <= g < len(q["options"])
            given = f'{"ABCD"[g]}. {q["options"][g]}' if ok else ""
            exp = f'{"ABCD"[q["correct"]]}. {q["options"][q["correct"]]}'
        else:
            exp = q.get("answer", "")
        answers.append({"text": q["text"], "type": q["type"], "max": q["marks"], "got": grade(q, g), "given": given, "exp": exp})
    total = sum(q["marks"] for q in qs)
    marks = sum(a["got"] for a in answers)
    pct = round(marks / total * 100) if total else 0
    data = {"title": p["title"], "marks": marks, "total": total, "pct": pct, "passPct": p["passPct"],
            "pass": pct >= p["passPct"], "viol": s["v"], "answers": answers,
            "date": datetime.now(TZ).strftime("%d %b %Y, %H:%M"),
            "review": any(q["type"] in ("short", "long") for q in qs)}
    c.execute("insert into results(email,pid,data) values(?,?,?)", (u["email"], s["pid"], json.dumps(data)))
    c.execute("delete from sessions where email=?", (u["email"],))
    return {"ok": True}

def fmt(r, full):
    d = json.loads(r["data"])
    if not full:
        d.pop("answers", None)
    return {**d, "id": r["id"], "email": r["email"], "pid": r["pid"]}

@app.get("/api/results")
def results(u=Depends(user), c=Depends(get_db)):
    if u["role"] == "admin":
        return [fmt(r, True) for r in c.execute("select * from results order by id").fetchall()]
    return [fmt(r, False) for r in c.execute("select * from results where email=? order by id", (u["email"],)).fetchall()]

class Mark(BaseModel):
    index: int
    marks: float

@app.patch("/api/results/{rid}/marks")
def set_mark(rid: int, b: Mark, u=Depends(admin), c=Depends(get_db)):
    r = c.execute("select data from results where id=?", (rid,)).fetchone()
    if not r:
        raise HTTPException(404, "Result not found")
    d = json.loads(r["data"])
    if not 0 <= b.index < len(d["answers"]):
        raise HTTPException(422, "Bad question index")
    a = d["answers"][b.index]
    a["got"] = max(0, min(a["max"], b.marks))
    d["marks"] = sum(x["got"] for x in d["answers"])
    d["pct"] = round(d["marks"] / d["total"] * 100) if d["total"] else 0
    d["pass"], d["review"] = d["pct"] >= d["passPct"], False
    c.execute("update results set data=? where id=?", (json.dumps(d), rid))
    return {"ok": True}

# ---------------- static front end (must be last) ----------------
app.mount("/", StaticFiles(directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), "static"), html=True), name="static")
