# GameRec v4

Dark-themed, detailed-card UI, local-only Flask app.

Setup:
1. Open this folder in PyCharm.
2. Create venv and install requirements:
   pip install -r requirements.txt
3. Train model:
   python train_model.py
4. Run the app:
   python app.py
5. Open the printed http://127.0.0.1:PORT in your browser.
6. Login: demo / demo

Notes:
- App runs only on localhost (127.0.0.1) on a random port for each run.
- If your dataset is large, training may take time. Use n_jobs in train_model.py accordingly.
