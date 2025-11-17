from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3, os, random, traceback
from pathlib import Path
import pandas as pd
import numpy as np

from rapidfuzz import process, fuzz

from plotly.offline import plot
import plotly.graph_objects as go

BASE = Path(__file__).resolve().parent

# ================================
# Load dataset
# ================================
if (BASE / "games_meta.csv").exists():
    META = pd.read_csv(BASE / "games_meta.csv")
elif (BASE / "merged_data.csv").exists():
    META = pd.read_csv(BASE / "merged_data.csv")
else:
    META = pd.DataFrame()

required_cols = [
    "id", "Title", "Developer", "Publisher", "Release Date",
    "Popular Tags", "Supported Languages", "Game Description", "Link"
]

for col in required_cols:
    if col not in META.columns:
        META[col] = ""

try:
    META["id"] = META["id"].astype(int)
except:
    META["id"] = range(len(META))

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = "dev-secret"

DB_PATH = BASE / "users.db"


# ================================
# Database Init
# ================================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT
    )""")
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("demo", "demo"))
    except:
        pass
    conn.commit()
    conn.close()

init_db()


# ================================
# Autocomplete
# ================================
@app.route("/api/suggest")
def suggest():
    q = request.args.get("q", "").strip()
    if q == "":
        return jsonify([])

    df = META
    qlow = q.lower()

    try:
        mask = df["Title"].astype(str).str.lower().str.contains(qlow, na=False)
        results = df[mask][["id", "Title"]].head(20).to_dict(orient="records")

        if len(results) == 0:
            choices = df["Title"].fillna("").astype(str).tolist()
            matches = process.extract(q, choices, scorer=fuzz.WRatio, limit=10)
            results = [
                {"id": int(df.iloc[idx]["id"]), "Title": title}
                for title, score, idx in matches if score > 50
            ]

        return jsonify(results)
    except:
        return jsonify([])


# ================================
# GAME DETAILS API
# ================================
@app.route("/api/game/<int:gid>")
def api_game(gid):
    df = META
    row = df[df["id"] == gid]
    if row.empty:
        return jsonify({"error": "not found"}), 404

    info = row.iloc[0].to_dict()

    tags = str(info.get("Popular Tags", "")).lower().replace(";", ",").split(",")
    tags = [t.strip() for t in tags if t.strip()]

    recs = []
    for _, r in df.iterrows():
        if int(r["id"]) == gid:
            continue
        rt = str(r["Popular Tags"]).lower().replace(";", ",").split(",")
        rt = [x.strip() for x in rt if x.strip()]
        score = len(set(tags) & set(rt))
        if score > 0:
            recs.append((score, r))

    recs = sorted(recs, key=lambda x: -x[0])[:10]
    recs_json = [{
        "id": int(r["id"]),
        "Title": r["Title"],
        "Developer": r["Developer"],
        "Publisher": r["Publisher"],
        "Release Date": r["Release Date"],
        "Link": r["Link"],
        "Popular Tags": r["Popular Tags"]
    } for score, r in recs]

    info["recommendations"] = recs_json
    return jsonify(info)


# ================================
# INSIGHTS PAGE (5 Graphs)
# ================================
@app.route("/insights/<int:gid>")
def insights(gid):
    df = META.copy()

    # Get game info
    row = df[df["id"] == gid]
    if row.empty:
        return "Game not found", 404

    game = row.iloc[0].to_dict()

    # ======================
    # GRAPH 1 — Top Devs
    # ======================
    top_dev = df["Developer"].value_counts().head(10)
    fig1 = go.Figure(go.Bar(
        x=top_dev.values,
        y=top_dev.index,
        orientation="h",
        marker=dict(color="#00eaff")
    ))
    fig1.update_layout(title="Top Developers", template="plotly_dark", height=350)
    dev_plot = plot(fig1, output_type="div", include_plotlyjs=True)

    # ======================
    # GRAPH 2 — Year Distribution
    # ======================
    df["Year"] = df["Release Date"].astype(str).str.extract(r"(\d{4})")
    df["Year"] = df["Year"].fillna(0).astype(int)
    yc = df[df["Year"] > 1900]["Year"].value_counts().sort_index()

    fig2 = go.Figure(go.Scatter(
        x=yc.index, y=yc.values, mode="lines+markers",
        line=dict(color="#ff00ff")
    ))
    fig2.update_layout(title="Release Year Distribution", template="plotly_dark", height=350)
    year_plot = plot(fig2, output_type="div", include_plotlyjs=False)

    # ======================
    # GRAPH 3 — Common Words
    # ======================
    desc_words = (
        df["Game Description"].astype(str)
        .str.lower()
        .str.replace(r"[^a-z ]", "", regex=True)
        .str.split()
    )

    flat_words = [w for lst in desc_words for w in lst if len(w) > 4]
    wc = pd.Series(flat_words).value_counts().head(12)

    fig3 = go.Figure(go.Bar(
        x=wc.values, y=wc.index, orientation="h", marker=dict(color="#be00ff")
    ))
    fig3.update_layout(title="Common Words in Descriptions", template="plotly_dark", height=350)
    words_plot = plot(fig3, output_type="div", include_plotlyjs=False)

    # ======================
    # GRAPH 4 — Genre Frequency
    # ======================
    tags = df["Popular Tags"].fillna("").astype(str).str.replace(";", ",").str.split(",")
    flat_tags = [t.strip() for lst in tags for t in lst if t.strip()]
    tc = pd.Series(flat_tags).value_counts().head(12)

    fig4 = go.Figure(go.Bar(
        x=tc.values, y=tc.index, orientation="h", marker=dict(color="#00ffaa")
    ))
    fig4.update_layout(title="Most Frequent Genres", template="plotly_dark", height=350)
    genre_plot = plot(fig4, output_type="div", include_plotlyjs=False)

    # ======================
    # GRAPH 5 — Languages
    # ======================
    langs = df["Supported Languages"].fillna("").astype(str).str.replace(";", ",").str.split(",")
    flat_langs = [l.strip() for lst in langs for l in lst if l.strip()]
    lc = pd.Series(flat_langs).value_counts().head(10)

    fig5 = go.Figure(go.Bar(
        x=lc.values, y=lc.index, orientation="h", marker=dict(color="#00b4d8")
    ))
    fig5.update_layout(title="Most Supported Languages", template="plotly_dark", height=350)
    lang_plot = plot(fig5, output_type="div", include_plotlyjs=False)

    return render_template(
        "insights.html",
        game=game,
        dev_plot=dev_plot,
        year_plot=year_plot,
        words_plot=words_plot,
        genre_plot=genre_plot,
        lang_plot=lang_plot
    )


# ================================
# ROUTES
# ================================
@app.route("/")
def index():
    if "user" in session:
        return redirect(url_for("discover"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("username")
        pwd = request.form.get("password")

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pwd))
        row = c.fetchone()
        conn.close()

        if row:
            session["user"] = user
            return redirect(url_for("discover"))

        return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/discover")
def discover():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("discover.html")

# ================================
# Run
# ================================
if __name__ == "__main__":
    port = random.randint(3000, 8999)
    print(f"Running at http://127.0.0.1:{port}")
    app.run(debug=True, host="127.0.0.1", port=port)
