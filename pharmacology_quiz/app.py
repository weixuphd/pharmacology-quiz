#!/usr/bin/env python3
"""Secured quiz server for antiviral drug question bank — Chapter 44 Pharmacology.

Supports three question types: 是非题, 单选题, 简答题(多选).
Questions live ONLY in server memory. No bulk-export endpoint exists.
"""

import csv
import io
import os
import secrets
from pathlib import Path

from flask import Flask, jsonify, render_template, request, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["300 per hour", "30 per minute"],
    storage_uri=os.environ.get("RATELIMIT_STORAGE", "memory://"),
)

# ---------------------------------------------------------------------------
# Load question bank
# ---------------------------------------------------------------------------
CSV_PATH = Path(__file__).parent / "antiviral_v2.csv"
OPTION_KEYS = ["option_a", "option_b", "option_c", "option_d", "option_e",
               "option_f", "option_g", "option_h", "option_i", "option_j"]
LABELS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]


def load_questions() -> list[dict]:
    text = CSV_PATH.read_text(encoding="utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    questions = []
    for row in reader:
        qtype = row.get("type", "单选题").strip()
        # Collect non-empty options
        options = []
        for k in OPTION_KEYS:
            v = row.get(k, "").strip()
            if v:
                options.append(v)
        questions.append({
            "id": int(row["id"]),
            "type": qtype,
            "question": row["question"].strip(),
            "options": options,
            "correct": row["correct"].strip().upper(),
            "explanation": row["explanation"].strip(),
            "category": row.get("category", "").strip(),
        })
    return questions


QUESTIONS: list[dict] = load_questions()
CATEGORIES: list[str] = sorted({q["category"] for q in QUESTIONS if q["category"]})
TYPES: list[str] = sorted({q["type"] for q in QUESTIONS})

qtype_counts = {}
for t in TYPES:
    qtype_counts[t] = sum(1 for q in QUESTIONS if q["type"] == t)
print(f"[server] Loaded {len(QUESTIONS)} questions: {qtype_counts}")


# ---------------------------------------------------------------------------
# Helper: compare student answer with correct answer (supports multi-select)
# ---------------------------------------------------------------------------
def check_answer(student: str, correct: str, qtype: str) -> bool:
    """Compare answers. For 简答题(多选), order-insensitive set comparison."""
    s = "".join(sorted(set(student.upper())))
    c = "".join(sorted(set(correct.upper())))
    if qtype == "简答题(多选)":
        return s == c
    return s == c


def validate_answer(answer: str, num_options: int) -> bool:
    """Check answer only uses valid option letters."""
    valid = set(LABELS[:num_options])
    return all(ch in valid for ch in answer.upper())


# ---------------------------------------------------------------------------
# Frontend
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/mobile")
def mobile():
    return app.send_static_file("antiviral_app.html")


# ---------------------------------------------------------------------------
# API — metadata
# ---------------------------------------------------------------------------
@app.route("/api/info")
@limiter.limit("10 per second")
def api_info():
    return jsonify({
        "total": len(QUESTIONS),
        "categories": CATEGORIES,
        "types": TYPES,
        "type_counts": qtype_counts,
    })


# ---------------------------------------------------------------------------
# API — get ONE question (no correct answer included)
# ---------------------------------------------------------------------------
@app.route("/api/question/<int:idx>")
@limiter.limit("5 per second")
def api_question(idx: int):
    if idx < 0 or idx >= len(QUESTIONS):
        abort(404, description=f"Index {idx} out of range (0-{len(QUESTIONS)-1})")

    q = QUESTIONS[idx]
    return jsonify({
        "id": q["id"],
        "index": idx,
        "total": len(QUESTIONS),
        "type": q["type"],
        "question": q["question"],
        "options": q["options"],
        "category": q["category"],
    })


# ---------------------------------------------------------------------------
# API — check answer (supports multi-select for 简答题)
# ---------------------------------------------------------------------------
@app.route("/api/check", methods=["POST"])
@limiter.limit("5 per second")
def api_check():
    data = request.get_json(silent=True)
    if not data:
        abort(400, description="JSON body required")

    qid = data.get("id")
    answer = str(data.get("answer", "")).strip().upper()

    if not qid or not answer:
        abort(400, description="id (int) and answer (A-J or multi-letter) required")

    q = next((q for q in QUESTIONS if q["id"] == int(qid)), None)
    if not q:
        abort(404, description="Question not found")

    if not validate_answer(answer, len(q["options"])):
        valid = "/".join(LABELS[:len(q["options"])])
        abort(400, description=f"Answer must be one or more of: {valid}")

    return jsonify({
        "correct": check_answer(answer, q["correct"], q["type"]),
        "correct_answer": q["correct"],
        "explanation": q["explanation"],
    })


# ---------------------------------------------------------------------------
# API — reveal answer
# ---------------------------------------------------------------------------
@app.route("/api/reveal/<int:idx>")
@limiter.limit("3 per second")
def api_reveal(idx: int):
    if idx < 0 or idx >= len(QUESTIONS):
        abort(404)
    q = QUESTIONS[idx]
    return jsonify({
        "type": q["type"],
        "correct_answer": q["correct"],
        "explanation": q["explanation"],
    })


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------
@app.errorhandler(404)
def not_found(e):
    return jsonify(error="Not found", detail=str(e.description)), 404


@app.errorhandler(429)
def ratelimited(e):
    return jsonify(error="Too many requests",
                   detail="请求过于频繁，请稍后再试"), 429

@app.errorhandler(400)
def bad_request(e):
    return jsonify(error="Bad request", detail=str(e.description)), 400


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    print(f"[server] Listening on 0.0.0.0:{port}  (debug={debug})")
    app.run(host="0.0.0.0", port=port, debug=debug)
