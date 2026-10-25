#!/usr/bin/env python
# coding: utf-8

# # Fundamentals of Data Science - Case Studies 2 and 5
# 
# ### Madharapu Saketh | 160124733183 | CSE-3 | III Year | CBIT

# In[1]:


import json, warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.cluster.hierarchy import linkage, dendrogram

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import (silhouette_score, mean_absolute_error,
                             mean_squared_error, r2_score)
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid", context="notebook")
plt.rcParams.update({"figure.dpi": 110, "axes.titlesize": 13, "axes.titleweight": "bold",
                     "axes.labelsize": 11})

DATA = Path("data")
FIG = Path("figures"); FIG.mkdir(exist_ok=True)
RES = Path("results"); RES.mkdir(exist_ok=True)
RANDOM_STATE = 42
results = {}

def save(name):
    plt.tight_layout()
    plt.savefig(FIG / f"{name}.png", dpi=200, bbox_inches="tight")
    plt.show()


# # Case Study 2: Clustering Analysis (East-West Airlines)

# ## 2.1 Loading the data

# In[2]:


air = pd.read_excel(DATA / "EastWestAirlines.xlsx", sheet_name="data")
print("Shape:", air.shape)
air.head()


# ## 2.2 Data preprocessing

# ### Missing values and duplicates

# In[3]:


air = air.drop(columns="ID#")
print("Missing values:", int(air.isna().sum().sum()))
print("Duplicate rows:", int(air.duplicated().sum()))
air.describe().T.round(2)


# ### Removing outliers

# In[4]:


num_cols = ["Balance", "Qual_miles", "Bonus_miles", "Bonus_trans",
            "Flight_miles_12mo", "Flight_trans_12"]
z = ((air[num_cols] - air[num_cols].mean()) / air[num_cols].std()).abs()
keep = (z < 3).all(axis=1)

before = len(air)
clean = air[keep].reset_index(drop=True)
print(f"Rows before: {before}, rows after: {len(clean)}, removed: {before - len(clean)} "
      f"({(before - len(clean)) / before:.1%})")
results["air_rows_before"] = before
results["air_rows_after"] = len(clean)

fig, axes = plt.subplots(2, 3, figsize=(12, 6))
for ax, c in zip(axes.ravel(), num_cols):
    sns.boxplot(x=air[c], ax=ax, color="#9ecae1", fliersize=2)
    ax.set_title(c); ax.set_xlabel("Value")
fig.suptitle("Box Plots Before Outlier Removal", fontsize=14, fontweight="bold", y=1.02)
save("cs2_boxplots_before")


# ### Scaling the features

# In[5]:


features = list(clean.columns)
scaler = StandardScaler()
X = scaler.fit_transform(clean[features])
X_df = pd.DataFrame(X, columns=features)
print("Mean after scaling (approx):", X.mean().round(3), " Std:", X.std().round(3))


# ## 2.3 Exploratory data analysis

# In[6]:


fig, axes = plt.subplots(3, 4, figsize=(14, 9))
for ax, c in zip(axes.ravel(), features):
    sns.histplot(clean[c], bins=30, ax=ax, color="#3182bd")
    ax.set_title(c); ax.set_xlabel("Value"); ax.set_ylabel("Customers")
fig.suptitle("Distribution of Each Feature (After Outlier Removal)", fontsize=14, fontweight="bold", y=1.01)
save("cs2_histograms")


# In[7]:


plt.figure(figsize=(9, 7))
sns.heatmap(clean.corr(), annot=True, fmt=".2f", cmap="coolwarm", center=0,
            linewidths=0.5, cbar_kws={"label": "Pearson correlation"})
plt.title("Correlation Heatmap of Airline Features")
save("cs2_heatmap")


# In[8]:


pca = PCA(n_components=2, random_state=RANDOM_STATE)
X_pca = pca.fit_transform(X)
print("Variance explained by PC1 and PC2:", pca.explained_variance_ratio_.round(3),
      "| total:", pca.explained_variance_ratio_.sum().round(3))
results["pca_var"] = float(pca.explained_variance_ratio_.sum())

plt.figure(figsize=(7, 5.5))
plt.scatter(X_pca[:, 0], X_pca[:, 1], s=6, alpha=0.5, color="#3182bd")
plt.xlabel("Principal Component 1"); plt.ylabel("Principal Component 2")
plt.title("Customers Projected on Two Principal Components")
save("cs2_pca_raw")


# ## 2.4 K-Means clustering

# In[9]:


k_range = range(2, 11)
inertia, sil = [], []
for k in k_range:
    km = KMeans(n_clusters=k, n_init=10, random_state=RANDOM_STATE).fit(X)
    inertia.append(km.inertia_)
    sil.append(silhouette_score(X, km.labels_))

fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
ax[0].plot(list(k_range), inertia, "o-", color="#08519c")
ax[0].set_xlabel("Number of clusters (K)"); ax[0].set_ylabel("Inertia (within-cluster sum of squares)")
ax[0].set_title("Elbow Curve for K-Means")
ax[1].plot(list(k_range), sil, "s-", color="#a50f15")
ax[1].set_xlabel("Number of clusters (K)"); ax[1].set_ylabel("Silhouette score")
ax[1].set_title("Silhouette Score for Different K")
save("cs2_kmeans_elbow")
pd.DataFrame({"K": list(k_range), "Inertia": np.round(inertia, 0), "Silhouette": np.round(sil, 4)})


# In[10]:


best_k_sil = int(list(k_range)[int(np.argmax(sil))])
print("K with highest silhouette:", best_k_sil, "->", round(max(sil), 4))
results["km_sil_by_k"] = {int(k): float(s) for k, s in zip(k_range, sil)}


# In[11]:


K_CHOSEN = 4
kmeans = KMeans(n_clusters=K_CHOSEN, n_init=10, random_state=RANDOM_STATE).fit(X)
clean["KMeans"] = kmeans.labels_
km_sil = silhouette_score(X, kmeans.labels_)
print(f"K-Means (K={K_CHOSEN}) silhouette score: {km_sil:.4f}")
print(clean["KMeans"].value_counts().sort_index().to_string())
results["km_k"] = K_CHOSEN
results["km_sil"] = float(km_sil)
results["km_sizes"] = {int(k): int(v) for k, v in clean["KMeans"].value_counts().sort_index().items()}

profile_km = clean.groupby("KMeans")[features].mean().round(1)
profile_km.insert(0, "Customers", clean["KMeans"].value_counts().sort_index())
profile_km


# In[12]:


def plot_clusters(labels, title, fname, noise_label=None):
    plt.figure(figsize=(7.5, 5.5))
    palette = sns.color_palette("tab10", n_colors=max(len(set(labels)), 3))
    for i, lab in enumerate(sorted(set(labels))):
        m = labels == lab
        if noise_label is not None and lab == noise_label:
            plt.scatter(X_pca[m, 0], X_pca[m, 1], s=8, c="lightgrey", label="Noise", alpha=0.7)
        else:
            plt.scatter(X_pca[m, 0], X_pca[m, 1], s=8, color=palette[i % 10], label=f"Cluster {lab}", alpha=0.7)
    plt.xlabel("Principal Component 1"); plt.ylabel("Principal Component 2")
    plt.title(title); plt.legend(markerscale=2.5, fontsize=9)
    save(fname)

plot_clusters(kmeans.labels_, f"K-Means Clusters (K={K_CHOSEN})", "cs2_kmeans_clusters")


# In[13]:


prof_scaled = pd.DataFrame(kmeans.cluster_centers_, columns=features)
plt.figure(figsize=(10, 3.8))
sns.heatmap(prof_scaled, annot=True, fmt=".2f", cmap="RdBu_r", center=0,
            cbar_kws={"label": "Standardised cluster mean"})
plt.xlabel("Feature"); plt.ylabel("K-Means cluster")
plt.title("K-Means Cluster Profiles (Standardised Averages)")
save("cs2_kmeans_profile")


# ## 2.5 Hierarchical clustering

# In[14]:


link_scores, link_sizes = {}, {}
for method in ["ward", "complete", "average", "single"]:
    ag = AgglomerativeClustering(n_clusters=4, linkage=method).fit(X)
    link_scores[method] = silhouette_score(X, ag.labels_)
    link_sizes[method] = sorted(np.bincount(ag.labels_).tolist(), reverse=True)
link_df = pd.DataFrame({"Linkage": list(link_scores), "Silhouette": np.round(list(link_scores.values()), 4),
                        "Cluster sizes": [str(v) for v in link_sizes.values()]})
results["hier_link_sizes"] = link_sizes
results["hier_link"] = {k: float(v) for k, v in link_scores.items()}
link_df


# In[15]:


Z = linkage(X, method="ward")
plt.figure(figsize=(11, 5))
dendrogram(Z, truncate_mode="lastp", p=30, show_leaf_counts=True, leaf_rotation=90, leaf_font_size=9,
           color_threshold=0.7 * max(Z[:, 2]))
plt.xlabel("Cluster (number of customers in brackets)"); plt.ylabel("Ward distance")
plt.title("Dendrogram (Ward Linkage, Last 30 Merges)")
save("cs2_dendrogram")


# In[16]:


hier = AgglomerativeClustering(n_clusters=4, linkage="ward").fit(X)
clean["Hierarchical"] = hier.labels_
hier_sil = silhouette_score(X, hier.labels_)
print(f"Hierarchical (Ward, 4 clusters) silhouette score: {hier_sil:.4f}")
print(clean["Hierarchical"].value_counts().sort_index().to_string())
results["hier_sil"] = float(hier_sil)
results["hier_sizes"] = {int(k): int(v) for k, v in clean["Hierarchical"].value_counts().sort_index().items()}

profile_h = clean.groupby("Hierarchical")[features].mean().round(1)
profile_h.insert(0, "Customers", clean["Hierarchical"].value_counts().sort_index())
profile_h


# In[17]:


plot_clusters(hier.labels_, "Hierarchical Clusters (Ward Linkage, 4 Clusters)", "cs2_hier_clusters")


# ## 2.6 DBSCAN

# In[18]:


min_pts = 2 * X.shape[1]
nbrs = NearestNeighbors(n_neighbors=min_pts).fit(X)
dist, _ = nbrs.kneighbors(X)
kdist = np.sort(dist[:, -1])

plt.figure(figsize=(8, 4.5))
plt.plot(kdist, color="#08519c")
plt.xlabel("Customers (sorted by distance)"); plt.ylabel(f"Distance to the {min_pts}th nearest neighbour")
plt.title("k-Distance Plot for Choosing Epsilon")
save("cs2_kdistance")


# In[19]:


rows = []
for eps in [1.0, 1.5, 2.0, 2.5, 3.0]:
    for mp in [5, 10, 22]:
        lab = DBSCAN(eps=eps, min_samples=mp).fit_predict(X)
        n_clu = len(set(lab)) - (1 if -1 in lab else 0)
        noise = (lab == -1).mean()
        mask = lab != -1
        s = silhouette_score(X[mask], lab[mask]) if n_clu >= 2 else np.nan
        rows.append({"eps": eps, "min_samples": mp, "clusters": n_clu,
                     "noise %": round(100 * noise, 1), "silhouette": round(s, 4) if n_clu >= 2 else np.nan})
db_grid = pd.DataFrame(rows)
db_grid


# In[20]:


cand = db_grid[(db_grid["clusters"] >= 2) & (db_grid["noise %"] < 15)].dropna()
best = cand.sort_values("silhouette", ascending=False).iloc[0] if len(cand) else \
       db_grid.dropna().sort_values("silhouette", ascending=False).iloc[0]
EPS, MINPTS = float(best["eps"]), int(best["min_samples"])
print("Chosen parameters -> eps:", EPS, " min_samples:", MINPTS)

db = DBSCAN(eps=EPS, min_samples=MINPTS).fit(X)
clean["DBSCAN"] = db.labels_
mask = db.labels_ != -1
n_clusters_db = len(set(db.labels_)) - (1 if -1 in db.labels_ else 0)
db_sil = silhouette_score(X[mask], db.labels_[mask]) if n_clusters_db >= 2 else float("nan")
print(f"Clusters found: {n_clusters_db}, noise points: {(~mask).sum()} ({(~mask).mean():.1%})")
print(f"DBSCAN silhouette score (noise excluded): {db_sil:.4f}")
print(clean["DBSCAN"].value_counts().sort_index().to_string())
results.update({"db_eps": EPS, "db_minpts": MINPTS, "db_clusters": n_clusters_db,
                "db_noise": int((~mask).sum()), "db_noise_pct": float((~mask).mean() * 100),
                "db_sil": float(db_sil),
                "db_sizes": {int(k): int(v) for k, v in clean["DBSCAN"].value_counts().sort_index().items()}})
plot_clusters(db.labels_, f"DBSCAN Clusters (eps={EPS}, min_samples={MINPTS})", "cs2_dbscan_clusters", noise_label=-1)


# In[21]:


profile_db = clean.groupby("DBSCAN")[features].mean().round(1)
profile_db.insert(0, "Customers", clean["DBSCAN"].value_counts().sort_index())
profile_db


# ## 2.7 Comparison of the three algorithms

# In[22]:


comp = pd.DataFrame({
    "Algorithm": ["K-Means", "Hierarchical (Ward)", "DBSCAN"],
    "Clusters": [K_CHOSEN, 4, n_clusters_db],
    "Silhouette score": [round(km_sil, 4), round(hier_sil, 4), round(db_sil, 4)],
    "Noise points": [0, 0, int((~mask).sum())],
})
results["comparison"] = comp.to_dict(orient="records")
comp


# In[23]:


from sklearn.metrics import adjusted_rand_score
ari = adjusted_rand_score(clean["KMeans"], clean["Hierarchical"])
print(f"Adjusted Rand Index (K-Means vs Hierarchical): {ari:.3f}")
results["ari_km_hier"] = float(ari)

seg = clean.groupby("KMeans").agg(Customers=("Balance", "size"), Avg_Balance=("Balance", "mean"),
        Avg_Bonus_miles=("Bonus_miles", "mean"), Avg_Flight_miles=("Flight_miles_12mo", "mean"),
        Avg_Days_enrolled=("Days_since_enroll", "mean"), Award_rate=("Award?", "mean")).round(2)
seg


# In[24]:


results["km_profile"] = clean.groupby("KMeans")[features].mean().round(2).to_dict(orient="index")
results["km_profile"] = {str(k): v for k, v in results["km_profile"].items()}
results["hier_profile"] = {str(k): v for k, v in clean.groupby("Hierarchical")[features].mean().round(2).to_dict(orient="index").items()}
results["db_profile"] = {str(k): v for k, v in clean.groupby("DBSCAN")[features].mean().round(2).to_dict(orient="index").items()}
results["db_grid"] = db_grid.fillna(-1).to_dict(orient="records")


# # Case Study 5: Wine Quality Assessment

# ## 5.1 Loading the data

# In[25]:


red = pd.read_csv(DATA / "winequality-red.csv", sep=";")
white = pd.read_csv(DATA / "winequality-white.csv", sep=";")
red["wine_type"] = "red"; white["wine_type"] = "white"
wine = pd.concat([red, white], ignore_index=True)

predictors = ["fixed acidity", "volatile acidity", "citric acid", "residual sugar", "chlorides",
              "free sulfur dioxide", "total sulfur dioxide", "density", "pH", "sulphates", "alcohol"]
print("Red:", red.shape, " White:", white.shape, " Combined:", wine.shape)
print("Missing values:", int(wine[predictors + ['quality']].isna().sum().sum()))
results["wine_n"] = len(wine); results["wine_red_n"] = len(red); results["wine_white_n"] = len(white)
wine.head()


# ## Task 1: Statistical analysis

# ### 1(a) Descriptive statistics

# In[26]:


cols3 = ["alcohol", "volatile acidity", "residual sugar"]
desc = pd.DataFrame({
    "Mean": wine[cols3].mean(),
    "Median": wine[cols3].median(),
    "Mode": [wine[c].mode().iloc[0] for c in cols3],
    "Std Dev": wine[cols3].std(),
    "Skewness": wine[cols3].skew(),
}).round(4)
results["desc"] = desc.to_dict(orient="index")
desc


# ### 1(b) Relative variability (Coefficient of Variation)

# In[27]:


cv = (wine[cols3].std() / wine[cols3].mean() * 100).round(2)
results["cv"] = cv.to_dict()
print("Coefficient of variation (%):"); print(cv.to_string())
print("\nMost variable attribute:", cv.idxmax())


# ### 1(c) Pearson correlation between alcohol and quality

# In[28]:


r, p = stats.pearsonr(wine["alcohol"], wine["quality"])
print(f"Pearson r = {r:.4f}, p-value = {p:.3e}")
results["r_alc_q"] = float(r); results["p_alc_q"] = float(p)


# ## Task 2: Exploratory data analysis

# ### 2(a) Histogram of quality scores

# In[29]:


plt.figure(figsize=(7.5, 4.8))
ax = sns.countplot(x="quality", data=wine, color="#3182bd")
for c in ax.containers: ax.bar_label(c, fontsize=9)
plt.xlabel("Quality score"); plt.ylabel("Number of wines")
plt.title("Distribution of Wine Quality Scores")
save("cs5_quality_hist")
qc = wine["quality"].value_counts().sort_index()
results["quality_counts"] = {int(k): int(v) for k, v in qc.items()}
results["quality_mean"] = float(wine["quality"].mean()); results["quality_std"] = float(wine["quality"].std())
print((qc / len(wine) * 100).round(1).to_string())


# ### 2(b) Box plot of alcohol by quality

# In[30]:


plt.figure(figsize=(8.5, 5))
sns.boxplot(x="quality", y="alcohol", data=wine, color="#9ecae1", fliersize=3)
plt.xlabel("Quality score"); plt.ylabel("Alcohol (% by volume)")
plt.title("Alcohol Content by Wine Quality Score")
save("cs5_alcohol_box")
med = wine.groupby("quality")["alcohol"].median().round(2)
results["alc_median_by_q"] = {int(k): float(v) for k, v in med.items()}
print(med.to_string())


# ### 2(c) Correlation heatmap

# In[31]:


corr = wine[predictors + ["quality"]].corr()
plt.figure(figsize=(10.5, 8.5))
mask_up = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask_up, annot=True, fmt=".2f", cmap="coolwarm", center=0, vmin=-1, vmax=1,
            linewidths=0.5, cbar_kws={"label": "Pearson correlation"})
plt.title("Correlation Heatmap of Physicochemical Attributes and Quality")
save("cs5_heatmap")
results["corr_with_quality"] = corr["quality"].drop("quality").round(4).to_dict()


# ### 2(d) Two attributes most related to quality

# In[32]:


cq = corr["quality"].drop("quality")
top2 = cq.abs().sort_values(ascending=False).head(2).index.tolist()
print(cq.round(4).sort_values(key=abs, ascending=False).to_string())
print("\nTop two by |r|:", top2)
results["top2_corr"] = {a: float(cq[a]) for a in top2}


# ## Task 3: Predictive modelling

# ### 3(a, b) Train-test split and model fitting

# In[33]:


X_w = wine[predictors]
y_w = wine["quality"]
X_train, X_test, y_train, y_test = train_test_split(X_w, y_w, test_size=0.2, random_state=RANDOM_STATE)
print("Training:", X_train.shape, " Testing:", X_test.shape)

lr = LinearRegression().fit(X_train, y_train)
y_pred = lr.predict(X_test)
print("Intercept:", round(lr.intercept_, 3))
pd.DataFrame({"Attribute": predictors, "Coefficient": lr.coef_.round(4)})


# ### 3(c) Test-set performance

# In[34]:


mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)
print(f"MAE  : {mae:.4f}")
print(f"MSE  : {mse:.4f}")
print(f"RMSE : {rmse:.4f}")
print(f"R2   : {r2:.4f}")
results["metrics"] = {"MAE": float(mae), "MSE": float(mse), "RMSE": float(rmse), "R2": float(r2)}
results["train_r2"] = float(lr.score(X_train, y_train))
base = np.full(len(y_test), y_train.mean())
results["baseline_rmse"] = float(np.sqrt(mean_squared_error(y_test, base)))
print("Baseline RMSE (predict the mean):", round(results["baseline_rmse"], 4))
print("Within +/-0.5 of actual after rounding:", f"{(np.round(y_pred) == y_test).mean():.1%}",
      "| within +/-1:", f"{(np.abs(np.round(y_pred) - y_test) <= 1).mean():.1%}")
results["exact_acc"] = float((np.round(y_pred) == y_test).mean())
results["within1_acc"] = float((np.abs(np.round(y_pred) - y_test) <= 1).mean())


# ### 3(d) Most influential predictors and multicollinearity

# In[35]:


sx, sy = StandardScaler(), StandardScaler()
Xs = sx.fit_transform(X_train)
ys = sy.fit_transform(y_train.values.reshape(-1, 1)).ravel()
lr_std = LinearRegression().fit(Xs, ys)
std_coef = pd.Series(lr_std.coef_, index=predictors)
order = std_coef.abs().sort_values(ascending=False).index
print(std_coef[order].round(4).to_string())
results["std_coef"] = std_coef[order].round(4).to_dict()

plt.figure(figsize=(8, 5))
colors = ["#3182bd" if v > 0 else "#de2d26" for v in std_coef[order][::-1]]
plt.barh(order[::-1], std_coef[order][::-1], color=colors)
plt.axvline(0, color="black", lw=0.8)
plt.xlabel("Standardised coefficient"); plt.ylabel("Attribute")
plt.title("Standardised Regression Coefficients (Blue = Positive, Red = Negative)")
save("cs5_std_coef")


# In[36]:


def vif_table(df):
    out = {}
    for c in df.columns:
        others = df.drop(columns=c)
        r2_j = LinearRegression().fit(others, df[c]).score(others, df[c])
        out[c] = 1 / (1 - r2_j)
    return pd.Series(out).sort_values(ascending=False)

vif = vif_table(X_train).round(2)
results["vif"] = vif.to_dict()
print(vif.to_string())

plt.figure(figsize=(8, 5))
plt.barh(vif.index[::-1], vif.values[::-1], color="#6baed6")
plt.axvline(5, color="orange", ls="--", label="VIF = 5 (moderate)")
plt.axvline(10, color="red", ls="--", label="VIF = 10 (serious)")
plt.xlabel("Variance Inflation Factor"); plt.ylabel("Attribute")
plt.title("Multicollinearity Check Using VIF")
plt.legend()
save("cs5_vif")


# In[37]:


pred_nd = [p for p in predictors if p != "density"]
sx2 = StandardScaler(); sy2 = StandardScaler()
lr_nd = LinearRegression().fit(sx2.fit_transform(X_train[pred_nd]), ys)
std_nd = pd.Series(lr_nd.coef_, index=pred_nd)
Xte_nd = X_test[pred_nd]
lr_nd_raw = LinearRegression().fit(X_train[pred_nd], y_train)
r2_nd = r2_score(y_test, lr_nd_raw.predict(Xte_nd))
print("Standardised coefficients without density:")
print(std_nd.reindex(std_nd.abs().sort_values(ascending=False).index).round(4).to_string())
print(f"\nTest R2 without density: {r2_nd:.4f}  (with density: {r2:.4f})")
results["std_coef_no_density"] = std_nd.reindex(std_nd.abs().sort_values(ascending=False).index).round(4).to_dict()
results["r2_no_density"] = float(r2_nd)
results["vif_no_density"] = vif_table(X_train[pred_nd]).round(2).to_dict()


# ### 3(e) Predicted versus actual quality

# In[38]:


rng = np.random.default_rng(RANDOM_STATE)
jitter = rng.uniform(-0.12, 0.12, len(y_test))
plt.figure(figsize=(7.5, 6))
plt.scatter(y_test + jitter, y_pred, s=12, alpha=0.4, color="#3182bd", label="Test wines")
plt.plot([3, 9], [3, 9], "r--", label="Perfect prediction")
plt.xlabel("Actual quality score"); plt.ylabel("Predicted quality score")
plt.title("Predicted vs Actual Quality (Test Set)")
plt.legend()
save("cs5_pred_vs_actual")

print("Predicted range:", y_pred.min().round(2), "to", y_pred.max().round(2))
print(pd.DataFrame({"actual": y_test.values, "pred": y_pred}).groupby("actual")["pred"].mean().round(2).to_string())


# In[39]:


residuals = y_test - y_pred
plt.figure(figsize=(7.5, 4.5))
sns.histplot(residuals, bins=30, kde=True, color="#3182bd")
plt.xlabel("Residual (actual - predicted)"); plt.ylabel("Number of wines")
plt.title("Distribution of Prediction Errors (Test Set)")
save("cs5_residuals")


# ## Task 4: Business decision-making

# In[40]:


print("Test R2:", round(r2, 3), "| RMSE:", round(rmse, 3), "| MAE:", round(mae, 3))
print(f"Only {results['exact_acc']:.0%} of wines get the exact score right; {results['within1_acc']:.0%} are within one point.")


# In[41]:


with open(RES / "summary.json", "w") as f:
    json.dump(results, f, indent=2, default=float)
print("Saved results/summary.json")

