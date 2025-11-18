
Gamers Republic — Game Recommendation System
===========================================

Project overview
----------------
Gamers Republic is a local Flask-based web application that helps users discover games using fuzzy autocomplete and tag-based recommendations, plus interactive global insights (Plotly). The project includes a neon-styled frontend (HTML/CSS/JS), a lightweight SQLite user system, and a metadata-driven recommendation engine.

This README is generated from the project report included with the repository. fileciteturn0file0

Key features
------------
- Secure user authentication (SQLite + hashed passwords)
- Fuzzy autocomplete search (RapidFuzz) — handles typos and abbreviations (e.g. "gta v")
- Game details endpoint with tag-based recommendations
- Insights page with 5 Plotly visualizations (Top Developers, Release Year distribution, Common words, Genres, Languages)
- Clean neon-themed UI with responsive layout
- Simple, local-first architecture (no external APIs required)

Quick setup (local)
-------------------
1. Clone the repository:
   git clone <your-repo-url>
   cd game_recommender_project_v4

2. Create & activate a virtual environment (recommended):
   python -m venv .venv
   # on Windows
   .venv\\Scripts\\activate
   # on macOS / Linux
   source .venv/bin/activate

3. Install dependencies:
   pip install -r requirements.txt

4. Prepare dataset & database:
   - Place your dataset file as `games_meta.csv` or `merged_data.csv` in project root.
   - The app will create `users.db` automatically on first run.

5. Run the app:
   python app.py
   Open the URL printed in the console (e.g. http://127.0.0.1:3456)

Authentication (register & login)
---------------------------------
- Register: /register (username, email, password)
- Login: /login (username or email, password)


Project structure (typical)
---------------------------
game_recommender_project_v4/
├─ app.py                  # Flask app, APIs, insights
├─ train_model.py          # (optional) training / preprocessing scripts
├─ games_meta.csv          # Dataset (Title, id, tags, description, etc.)
├─ merged_data.csv         # Alternate dataset filename
├─ requirements.txt
├─ users.db                # SQLite DB (created at runtime)
├─ static/
│  ├─ main.js
│  └─ style.css
└─ templates/
   ├─ base.html
   ├─ login.html
   ├─ register.html
   ├─ discover.html
   └─ insights.html

API endpoints
-------------------------
- GET /api/suggest?q=...       → returns fuzzy-matched suggestions (JSON)
- GET /api/game/<id>           → returns game details + recommendations (JSON)
- GET /insights/<id>           → insights page (Plotly visualizations)
- Auth routes: /login, /register, /logout
- /discover                    → main search UI (requires login)

OUTPUT SCREENS
-----------------

LOGIN PAGE:

<img width="1896" height="873" alt="image" src="https://github.com/user-attachments/assets/00ffab07-f784-4d50-92f5-8a678e701100" />

SIGN UP PAGE:

<img width="1888" height="875" alt="image" src="https://github.com/user-attachments/assets/ccc6fa4d-648e-4686-9777-36786308efbd" />

DISCOVER PAGE:

<img width="1899" height="877" alt="image" src="https://github.com/user-attachments/assets/1a44a141-cff8-4a85-b324-4fafbd634536" />

INSIGHTS PAGE:

<img width="1898" height="881" alt="image" src="https://github.com/user-attachments/assets/c44ee78a-356a-4c93-82a8-8798d41f122e" />

STEAM LINKED PAGE:

<img width="1918" height="872" alt="image" src="https://github.com/user-attachments/assets/93675d41-ae60-4544-86ae-f7c961472aca" />


Useful links & references
-------------------------
- Flask: https://flask.palletsprojects.com/
- Pandas: https://pandas.pydata.org/
- Plotly Python: https://plotly.com/python/
- RapidFuzz: https://maxbachmann.github.io/RapidFuzz/

Contact / Author
----------------
Project prepared by: Vikram Kochar
(Include your email or GitHub profile)

Appendix: Project report (detailed) included in repository: the project PDF report was uploaded with this repo. fileciteturn0file0
