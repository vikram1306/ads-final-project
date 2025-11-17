from pathlib import Path
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import joblib
import scipy.sparse as sp

BASE = Path(__file__).resolve().parent
df = pd.read_csv(BASE/"merged_data.csv")
df.reset_index(inplace=True, drop=False)
df = df.rename(columns={'index':'id'})

cols = ['id','Title','Game Description','Developer','Publisher','Release Date','Link','Popular Tags','Supported Languages']
for c in cols:
    if c not in df.columns:
        df[c] = ""

meta = df[cols]
meta.to_csv(BASE/"games_meta.csv", index=False)
print("Wrote games_meta.csv with", len(meta), "rows")

def make_text(row):
    parts = [str(row.get('Title','')), str(row.get('Popular Tags','')), str(row.get('Game Description','')), str(row.get('Developer',''))]
    return " ".join([p for p in parts if p])

print("Building corpus...")
corpus = df.apply(make_text, axis=1).astype(str).tolist()

print("Fitting TF-IDF... (may take a while)")
tfidf = TfidfVectorizer(max_features=50000, stop_words='english', ngram_range=(1,2))
X = tfidf.fit_transform(corpus)
print("TF-IDF shape:", X.shape)

print("Fitting NearestNeighbors...")
nn = NearestNeighbors(n_neighbors=11, metric='cosine', algorithm='brute', n_jobs=4)
nn.fit(X)

ART = BASE/"artifacts"
ART.mkdir(exist_ok=True)

joblib.dump(tfidf, ART/"tfidf_vectorizer.joblib")
joblib.dump(nn, ART/"nn_model.joblib")
sp.save_npz(ART/"tfidf_matrix.npz", X)
print("Saved artifacts to", ART)
