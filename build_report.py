"""Builds report/FDS_Case_Studies_Report.pdf from results/summary.json and figures/*.png.
Put the college logo at assets/cbit_logo.png (PNG/JPG) and re-run to place it on the title page."""
import json, os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Image,
                                Table, TableStyle, PageBreak, KeepTogether, NextPageTemplate)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.utils import ImageReader

F = "/usr/share/fonts/truetype/liberation/"
pdfmetrics.registerFont(TTFont("Serif", F + "LiberationSerif-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Serif-B", F + "LiberationSerif-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Serif-I", F + "LiberationSerif-Italic.ttf"))
pdfmetrics.registerFont(TTFont("Serif-BI", F + "LiberationSerif-BoldItalic.ttf"))
pdfmetrics.registerFontFamily("Serif", normal="Serif", bold="Serif-B", italic="Serif-I", boldItalic="Serif-BI")

R = json.load(open("results/summary.json"))
NAVY = colors.black
LIGHT = colors.HexColor("#e6e6e6")

body = ParagraphStyle("body", fontName="Serif", fontSize=11.5, leading=17, alignment=TA_JUSTIFY, spaceAfter=8)
bullet = ParagraphStyle("bullet", parent=body, leftIndent=30, bulletIndent=14, spaceAfter=4)
h1 = ParagraphStyle("h1", fontName="Serif-B", fontSize=16, leading=20, textColor=NAVY, spaceBefore=14, spaceAfter=8, keepWithNext=1)
h2 = ParagraphStyle("h2", fontName="Serif-B", fontSize=13, leading=17, textColor=NAVY, spaceBefore=10, spaceAfter=6, keepWithNext=1)
h3 = ParagraphStyle("h3", fontName="Serif-BI", fontSize=11.5, leading=15, spaceBefore=6, spaceAfter=4, keepWithNext=1)
part = ParagraphStyle("part", fontName="Serif-B", fontSize=22, leading=28, alignment=TA_CENTER, textColor=NAVY)
cap = ParagraphStyle("cap", fontName="Serif-I", fontSize=10, leading=13, alignment=TA_CENTER, spaceAfter=8, spaceBefore=3)
tcap = ParagraphStyle("tcap", parent=cap, spaceBefore=6, spaceAfter=3)
cell = ParagraphStyle("cell", fontName="Serif", fontSize=9.5, leading=12, alignment=TA_CENTER)
cellb = ParagraphStyle("cellb", parent=cell, fontName="Serif-B")
celll = ParagraphStyle("celll", parent=cell, alignment=TA_LEFT)

class Doc(BaseDocTemplate):
    def __init__(self, fn, **kw):
        super().__init__(fn, pagesize=A4, leftMargin=2.5*cm, rightMargin=2.5*cm, topMargin=2.4*cm, bottomMargin=2.2*cm, **kw)
        fr = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="f")
        self.addPageTemplates([PageTemplate(id="title", frames=[fr], onPage=self.title_page),
                               PageTemplate(id="main", frames=[fr], onPage=self.main_page)])
    def title_page(self, c, d):
        c.saveState(); c.setStrokeColor(NAVY); c.setLineWidth(2.5)
        c.rect(1.3*cm, 1.3*cm, A4[0]-2.6*cm, A4[1]-2.6*cm); c.setLineWidth(0.8)
        c.rect(1.6*cm, 1.6*cm, A4[0]-3.2*cm, A4[1]-3.2*cm); c.restoreState()
    def main_page(self, c, d):
        c.saveState(); c.setFont("Serif", 9.5); c.setFillColor(colors.black)
        c.drawString(2.5*cm, A4[1]-1.5*cm, "Fundamentals of Data Science - Case Studies 2 and 5")
        c.drawRightString(A4[0]-2.5*cm, A4[1]-1.5*cm, "CBIT, Hyderabad")
        c.setStrokeColor(NAVY); c.setLineWidth(0.8); c.line(2.5*cm, A4[1]-1.65*cm, A4[0]-2.5*cm, A4[1]-1.65*cm)
        c.line(2.5*cm, 1.7*cm, A4[0]-2.5*cm, 1.7*cm)
        c.drawString(2.5*cm, 1.2*cm, "Madharapu Saketh  |  160124733183  |  CSE-3")
        c.drawRightString(A4[0]-2.5*cm, 1.2*cm, f"Page {d.page - 1}")
        c.restoreState()
    def afterFlowable(self, fl):
        if isinstance(fl, Paragraph) and fl.style.name in ("h1", "h2"):
            self.notify("TOCEntry", (0 if fl.style.name == "h1" else 1, fl.getPlainText(), self.page - 1))

def P(t, s=body): return Paragraph(t, s)
def B(items): return [Paragraph(i, bullet, bulletText="\u2022") for i in items]
fig_n = [0]; tab_n = [0]
def fig(name, caption, width=14.0):
    fig_n[0] += 1
    path = f"figures/{name}.png"
    iw, ih = ImageReader(path).getSize()
    w = width*cm; h = w*ih/iw
    if h > 12.5*cm: h = 12.5*cm; w = h*iw/ih
    return KeepTogether([Image(path, width=w, height=h), Paragraph(f"Figure {fig_n[0]}: {caption}", cap)])
def table(rows, widths, caption, header=True, left_first=True):
    tab_n[0] += 1
    data = []
    for i, r in enumerate(rows):
        data.append([Paragraph(str(c), (cellb if (i == 0 and header) else (celll if (j == 0 and left_first) else cell)))
                     for j, c in enumerate(r)])
    t = Table(data, colWidths=[w*cm for w in widths], repeatRows=1)
    st = [("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#444444")), ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
          ("TOPPADDING", (0,0), (-1,-1), 3), ("BOTTOMPADDING", (0,0), (-1,-1), 3)]
    if header: st += [("BACKGROUND", (0,0), (-1,0), LIGHT)]
    t.setStyle(TableStyle(st))
    return KeepTogether([Paragraph(f"Table {tab_n[0]}: {caption}", tcap), t, Spacer(1, 10)])
def n(x, d=2): return f"{x:,.{d}f}"

S = []
# ---------------- TITLE PAGE ----------------
S += [Spacer(1, 0.6*cm)]
logo = next((p for p in ["assets/cbit_logo.png", "assets/cbit_logo.jpg", "assets/cbit_logo.jpeg"] if os.path.exists(p)), None)
if logo:
    iw, ih = ImageReader(logo).getSize(); h = 4.2*cm
    im = Image(logo, width=h*iw/ih, height=h); im.hAlign = "CENTER"; S += [im]
else:
    ph = Table([[Paragraph("CBIT LOGO", ParagraphStyle("x", fontName="Serif-B", fontSize=12, alignment=TA_CENTER, textColor=colors.grey))]],
               colWidths=[3.6*cm], rowHeights=[3.6*cm])
    ph.setStyle(TableStyle([("BOX", (0,0), (-1,-1), 1, colors.grey), ("VALIGN", (0,0), (-1,-1), "MIDDLE")])); ph.hAlign = "CENTER"
    S += [ph]
S += [Spacer(1, 0.5*cm),
      Paragraph("CHAITANYA BHARATHI", ParagraphStyle("c1", fontName="Serif-B", fontSize=30, leading=36, alignment=TA_CENTER, textColor=NAVY)),
      Paragraph("INSTITUTE OF TECHNOLOGY", ParagraphStyle("c2", fontName="Serif-B", fontSize=30, leading=36, alignment=TA_CENTER, textColor=NAVY)),
      Spacer(1, 4),
      Paragraph("(Autonomous)  |  Gandipet, Hyderabad - 500075, Telangana", ParagraphStyle("c3", fontName="Serif", fontSize=12, alignment=TA_CENTER)),
      Paragraph("Department of Computer Science and Engineering", ParagraphStyle("c4", fontName="Serif-B", fontSize=14, leading=20, alignment=TA_CENTER, spaceBefore=6)),
      Spacer(1, 1.1*cm),
      Paragraph("FUNDAMENTALS OF DATA SCIENCE", ParagraphStyle("t0", fontName="Serif-B", fontSize=18, leading=24, alignment=TA_CENTER)),
      Paragraph("Case Study Report", ParagraphStyle("t1", fontName="Serif-I", fontSize=15, leading=20, alignment=TA_CENTER, spaceAfter=14)),
      Paragraph("Case Study 2: Clustering Analysis of East-West Airlines Customers", ParagraphStyle("t2", fontName="Serif-B", fontSize=14, leading=19, alignment=TA_CENTER, textColor=NAVY)),
      Paragraph("(K-Means, Hierarchical Clustering and DBSCAN)", ParagraphStyle("t3", fontName="Serif", fontSize=12, alignment=TA_CENTER, spaceAfter=8)),
      Paragraph("Case Study 5: Wine Quality Assessment Using Physicochemical Properties", ParagraphStyle("t4", fontName="Serif-B", fontSize=14, leading=19, alignment=TA_CENTER, textColor=NAVY)),
      Paragraph("(Statistical Analysis, EDA and Multiple Linear Regression)", ParagraphStyle("t5", fontName="Serif", fontSize=12, alignment=TA_CENTER)),
      Spacer(1, 1.3*cm)]
info = [["Name", "Madharapu Saketh"], ["Roll No.", "160124733183"], ["Section", "CSE-3"], ["Year", "III Year"],
        ["Subject", "Fundamentals of Data Science"], ["Faculty Name", "S. Durga Devi"]]
it = Table([[Paragraph(a, ParagraphStyle("ia", fontName="Serif-B", fontSize=13, leading=17)),
             Paragraph(":", ParagraphStyle("ib", fontName="Serif", fontSize=13, leading=17)),
             Paragraph(b, ParagraphStyle("ic", fontName="Serif", fontSize=13, leading=17))] for a, b in info],
           colWidths=[4.2*cm, 0.6*cm, 7*cm])
it.setStyle(TableStyle([("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5)])); it.hAlign = "CENTER"
S += [it, NextPageTemplate("main"), PageBreak()]

# ---------------- CONTENTS ----------------
S += [Paragraph("Contents", ParagraphStyle("ct", fontName="Serif-B", fontSize=20, leading=26, textColor=NAVY, spaceAfter=12))]
toc = TableOfContents(); toc.dotsMinLevel = 0
toc.levelStyles = [ParagraphStyle("t1", fontName="Serif-B", fontSize=12, leading=16, leftIndent=0, spaceBefore=3),
                   ParagraphStyle("t2", fontName="Serif", fontSize=11, leading=13.5, leftIndent=22)]
S += [toc, PageBreak()]

# ---------------- PART A ----------------
S += [Spacer(1, 6*cm), Paragraph("PART A", part), Spacer(1, 6),
      Paragraph("Case Study 2: Clustering Analysis", ParagraphStyle("pa", parent=part, fontSize=18, leading=24)), PageBreak()]
S += [P("1. Problem Statement", h1),
      P("East-West Airlines wants to know more about its customers: how they fly, how they earn and use frequent-flyer miles, and how they use the airline credit card. The dataset contains 3,999 members described by 11 variables such as miles balance, bonus miles, flight transactions and the number of days since enrolment."),
      P("The task is to divide these customers into meaningful groups (segments) using three clustering methods, K-Means, Hierarchical clustering and DBSCAN, to compare the methods, and to explain what kind of customer each group contains. Such groups can help the airline plan offers that suit each type of customer.")]

S += [P("2. Methodology", h1), P("The work was done in Python (pandas, scikit-learn, scipy, matplotlib and seaborn) in the following steps:"),
      *B(["<b>Preprocessing:</b> checked missing values and duplicates, removed extreme outliers, and scaled all features to the same range of importance.",
          "<b>Exploratory analysis:</b> studied the distribution of each feature, the correlations between features, and a two-dimensional view of the data using PCA.",
          "<b>K-Means:</b> tried K from 2 to 10, used the elbow curve and the silhouette score to choose K, and profiled each cluster.",
          "<b>Hierarchical clustering:</b> compared four linkage methods, drew a dendrogram, and profiled the final clusters.",
          "<b>DBSCAN:</b> used a k-distance plot and a grid of epsilon and minimum-samples values to choose parameters.",
          "<b>Evaluation:</b> compared the three methods using the silhouette score, cluster sizes and how easy the groups are to interpret."]),
      P("All results are produced by the accompanying Jupyter Notebook, and a fixed random state (42) is used so the results can be repeated.")]

S += [P("3. Statistical Findings", h1), P("3.1 Data preparation", h2),
      P(f"The data had <b>no missing values and no duplicate rows</b>. The identifier column (ID#) was dropped because it carries no information about behaviour. The summary statistics showed very large maximum values for Balance, Bonus_miles and the flight columns compared to their medians, so outliers were examined."),
      fig("cs2_boxplots_before", "Box plots of the six continuous features before outlier removal."),
      P("<b>Interpretation:</b> Every box is squeezed close to zero while many dots stretch far to the right. This means most customers have small values and a few customers have extremely large ones. If these extreme customers were kept, the cluster centres would be dragged towards them and most ordinary customers would end up in one big group."),
      P(f"A customer was treated as an outlier if any of the six continuous columns was more than 3 standard deviations away from its mean. This removed {R['air_rows_before'] - R['air_rows_after']} customers (8.0%) and left <b>{R['air_rows_after']:,}</b> customers for clustering. After this, all features were standardised (mean 0, standard deviation 1), because variables such as Balance (tens of thousands) and cc1_miles (1 to 5) are on very different scales and would otherwise dominate the distance calculations.")]

S += [P("3.2 Exploratory data analysis", h2),
      fig("cs2_histograms", "Distribution of each feature after outlier removal.", 15),
      P("<b>Interpretation:</b> Most features are right-skewed. Qual_miles, Flight_miles_12mo and Flight_trans_12 are zero for a large part of the customers, which tells us that many members rarely fly and collect their miles in other ways. Days_since_enroll is spread fairly evenly, so the airline has both new and long-standing members. The card-category columns (cc1, cc2, cc3) take only a few values, and most customers sit in the lowest category of cc2 and cc3."),
      fig("cs2_heatmap", "Correlation heatmap of the airline features.", 12.5),
      P("<b>Interpretation:</b> Flight miles and flight transactions are strongly related (0.87), which is natural because more flights give more miles. Bonus miles are strongly related to cc1_miles (0.83) and moderately to bonus transactions (0.60), showing that credit-card use is the main source of bonus miles. Balance has a moderate relation with Bonus_miles (0.40). The cc2 and cc3 columns are almost unrelated to everything else. No two features are identical, so all of them were kept for clustering."),
      fig("cs2_pca_raw", "Customers projected on the first two principal components.", 10.5),
      P(f"<b>Interpretation:</b> The two components keep only {R['pca_var']*100:.0f}% of the information in the data, so this picture is only an approximation. It shows one dense cloud with arms stretching out to the right and upward. There are no widely separated islands, so we should expect clusters that touch or overlap, and only moderate silhouette scores.")]

S += [P("4. Clustering Results", h1), P("4.1 K-Means", h2),
      fig("cs2_kmeans_elbow", "Elbow curve (left) and silhouette score (right) for K = 2 to 10.", 15),
      P(f"<b>Interpretation:</b> The inertia (total distance of points from their cluster centres) falls quickly until about K = 4 and then drops slowly, which forms the elbow. The silhouette scores stay between 0.24 and 0.33, with K = 4 giving {R['km_sil_by_k']['4']:.2f} and K = 6 giving {R['km_sil_by_k']['6']:.2f}. Since the difference is tiny, we chose <b>K = 4</b> because it has a clear elbow and gives a small number of segments that are easy to explain.")]
km = R["km_profile"]; ks = R["km_sizes"]
names = {"0": "Low-activity members", "3": "Credit-card earners", "1": "Frequent flyers", "2": "Rewards-card group"}
rows = [["Cluster", "Customers", "Balance", "Bonus miles", "Flight miles", "Flight trans.", "Days enrolled", "Award rate"]]
for k in ["0", "3", "1", "2"]:
    p = km[k]; rows.append([f"{k}: {names[k]}", f"{ks[k]:,}", n(p['Balance'],0), n(p['Bonus_miles'],0), n(p['Flight_miles_12mo'],0), n(p['Flight_trans_12'],1), n(p['Days_since_enroll'],0), f"{p['Award?']*100:.0f}%"])
S += [table(rows, [3.6, 2.1, 1.7, 1.8, 1.7, 1.5, 1.7, 1.4], "Average profile of each K-Means cluster."),
      fig("cs2_kmeans_clusters", "K-Means clusters (K = 4) shown on the first two principal components.", 12.5),
      P("<b>Interpretation:</b> Each colour is one segment. Cluster 0 (blue) is the large group on the left, cluster 3 (red) spreads along the lower right and cluster 1 (orange) holds the high-activity customers at the top. Cluster 2 (green) looks scattered because it is defined mainly by the Rewards credit-card column, which the two-dimensional picture does not show well."),
      fig("cs2_kmeans_profile", "Standardised average of every feature in each K-Means cluster.", 14),
      P("<b>Interpretation:</b> Red cells mean the cluster is above the overall average on that feature and blue cells mean below average. Cluster 3 stands out on cc1_miles and Bonus_miles, cluster 1 on the flight columns and Qual_miles, and cluster 2 on cc2_miles. Cluster 0 is below average almost everywhere."),
      P("<b>Segment descriptions:</b>"),
      *B([f"<b>Cluster 0 - Low-activity members ({ks['0']:,} customers, 60%):</b> small balance (about {n(km['0']['Balance'],0)} miles), few bonus miles, almost no flying, and only {km['0']['Award?']*100:.0f}% have claimed an award. These customers are the biggest group but the least engaged.",
          f"<b>Cluster 3 - Credit-card earners ({ks['3']:,} customers, 32%):</b> high balance ({n(km['3']['Balance'],0)} miles) and the highest bonus miles ({n(km['3']['Bonus_miles'],0)}), mostly from the frequent-flyer credit card (average card category {km['3']['cc1_miles']:.1f}). They are the longest-enrolled members and rarely fly, so they collect miles mainly by spending on the card.",
          f"<b>Cluster 1 - Frequent flyers ({ks['1']:,} customers, 7%):</b> they fly the most ({n(km['1']['Flight_miles_12mo'],0)} flight miles and about {km['1']['Flight_trans_12']:.0f} flights a year), have high balance and the highest award rate ({km['1']['Award?']*100:.0f}%). This is the most valuable group for the airline.",
          f"<b>Cluster 2 - Rewards-card group ({ks['2']} customers, 1%):</b> a very small group that uses the Rewards credit card (category {km['2']['cc2_miles']:.1f}), with moderate balance and no qualifying miles."]),
      P(f"The overall K-Means silhouette score is <b>{R['km_sil']:.3f}</b>, which is modest. It means the segments are real but overlap at their borders, which matches what the PCA plot showed.")]

hs = R["hier_sizes"]; hp = R["hier_profile"]; ls = R["hier_link_sizes"]; lk = R["hier_link"]
rows = [["Linkage", "Silhouette score", "Cluster sizes"]] + [[m.capitalize(), f"{lk[m]:.3f}", ", ".join(f"{v:,}" for v in ls[m])] for m in ["ward", "complete", "average", "single"]]
S += [P("4.2 Hierarchical clustering", h2),
      P("Four linkage methods were compared for four clusters. The cluster sizes are shown next to the scores because a high silhouette can be misleading."),
      table(rows, [4, 4, 7], "Comparison of linkage methods (four clusters each)."),
      P("<b>Interpretation:</b> Complete, average and single linkage give high scores (0.63 to 0.79), but only because they put almost every customer into one giant cluster and leave a handful of extreme customers in tiny clusters. That is not a useful segmentation. <b>Ward linkage</b> gives groups of sensible sizes, so it was used even though its score is lower."),
      fig("cs2_dendrogram", "Dendrogram using Ward linkage (last 30 merges).", 14.5),
      P("<b>Interpretation:</b> The dendrogram shows how clusters are merged step by step. The tall vertical lines at the top show that very different groups are joined only at the end. Cutting the tree where it crosses four branches gives four clusters, which agrees with the K-Means choice."),
      fig("cs2_hier_clusters", "Hierarchical clusters (Ward linkage, four clusters) on the principal components.", 12.5)]
rows = [["Cluster", "Customers", "Balance", "Bonus miles", "Flight miles", "Days enrolled", "Award rate"]]
hn = {"1": "Low-activity", "0": "Credit-card earners", "2": "Frequent flyers", "3": "Rewards-card group"}
for k in ["1", "0", "2", "3"]:
    p = hp[k]; rows.append([f"{k}: {hn[k]}", f"{hs[k]:,}", n(p['Balance'],0), n(p['Bonus_miles'],0), n(p['Flight_miles_12mo'],0), n(p['Days_since_enroll'],0), f"{p['Award?']*100:.0f}%"])
S += [table(rows, [4.0, 2.1, 1.9, 2, 2, 2, 1.6], "Average profile of each hierarchical cluster."),
      P(f"<b>Interpretation:</b> The hierarchical result is close to K-Means. It also finds a large low-activity group ({hs['1']:,} customers), a credit-card group with a very high balance, a frequent-flyer group and the same 38-customer Rewards-card group. The two methods agree on the overall picture; the Adjusted Rand Index between them is <b>{R['ari_km_hier']:.2f}</b> (1 means identical), which shows good but not perfect agreement. The Ward silhouette score is {R['hier_sil']:.3f}.")]

dg = R["db_grid"]
rows = [["Epsilon", "Min. samples", "Clusters", "Noise (%)", "Silhouette"]]
for g in dg: rows.append([g["eps"], g["min_samples"], g["clusters"], g["noise %"], "n/a" if g["silhouette"] < 0 else f"{g['silhouette']:.3f}"])
dbs = R["db_sizes"]
S += [P("4.3 DBSCAN", h2),
      P("DBSCAN does not need the number of clusters in advance, but it needs two settings: epsilon (the neighbourhood radius) and the minimum number of points in a neighbourhood. The k-distance plot was used first to find a suitable epsilon."),
      fig("cs2_kdistance", f"k-distance plot (k = 22) used to choose epsilon.", 11.5),
      P("<b>Interpretation:</b> The curve is flat for most customers and then turns sharply upward. The bend of the curve (distance of roughly 2 to 3) marks the point beyond which customers are far from everyone else, so epsilon should be chosen in that range. A grid of settings around this range was then tested."),
      table(rows, [2.5, 3, 2.5, 2.5, 2.5], "DBSCAN parameter search (silhouette is calculated without noise points)."),
      P(f"<b>Interpretation:</b> Small epsilon values (1.0 to 2.0) label 4% to 28% of customers as noise and give silhouette scores below 0.32. At epsilon 2.5 and 3.0 the scores jump above 0.5, but this is because almost everyone then belongs to one dense cluster. The best setting that kept the noise share low was <b>epsilon = {R['db_eps']}, min samples = {R['db_minpts']}</b>."),
      fig("cs2_dbscan_clusters", f"DBSCAN clusters (epsilon = {R['db_eps']}, min samples = {R['db_minpts']}); grey points are noise.", 12.5),
      P(f"<b>Interpretation:</b> DBSCAN found {R['db_clusters']} clusters, but one of them contains {dbs['0']:,} customers (96%) and the other three are tiny ({dbs['1']}, {dbs['2']} and {dbs['3']} customers). A further {R['db_noise']} customers ({R['db_noise_pct']:.1f}%) were marked as noise. The noise customers have the highest average balance (about {n(R['db_profile']['-1']['Balance'],0)} miles) and the most flight miles, so DBSCAN is in effect picking out the unusual high-value customers rather than splitting the ordinary ones. This is useful for spotting special cases, but it does not give a practical set of segments.")]

cm_ = R["comparison"]
rows = [["Algorithm", "Clusters", "Silhouette score", "Noise points", "Largest cluster"],
        ["K-Means", 4, f"{R['km_sil']:.3f}", 0, f"{max(ks.values()):,} (60%)"],
        ["Hierarchical (Ward)", 4, f"{R['hier_sil']:.3f}", 0, f"{max(hs.values()):,} (64%)"],
        ["DBSCAN", R["db_clusters"], f"{R['db_sil']:.3f}", R["db_noise"], f"{dbs['0']:,} (96%)"]]
S += [P("5. Model Evaluation and Comparison", h1),
      table(rows, [4, 2.2, 3, 2.5, 3.5], "Summary of the three clustering algorithms."),
      P("The silhouette score measures how well each customer fits its own cluster compared with the nearest other cluster; values near 1 are good and values near 0 mean overlapping clusters. Based on the table:"),
      *B(["<b>K-Means</b> has the best score among the methods that produce balanced segments (0.32). It is fast, easy to explain and gives four distinct customer types.",
          "<b>Hierarchical clustering</b> gives a very similar result (0.28) and adds a dendrogram that shows how groups relate, but it is slower on large data.",
          "<b>DBSCAN</b> has the highest number (0.54), but this number is not a fair comparison. It leaves noise points out and puts 96% of customers in one cluster. Its main value here is finding unusual customers."]),
      P("Overall, <b>K-Means with four clusters is the most practical choice</b> for this dataset.")]

S += [P("6. Business Interpretation", h1),
      P("The four segments suggest different actions for the airline:"),
      *B(["<b>Low-activity members:</b> send simple offers to bring them back, such as bonus miles on the next flight or on first card use.",
          "<b>Credit-card earners:</b> they are loyal and active on the card, so offers should focus on spending partners and on helping them redeem their large balances on flights.",
          "<b>Frequent flyers:</b> protect this small, valuable group with priority services and status benefits.",
          "<b>Rewards-card group:</b> too small to need a separate campaign, but worth watching as a niche."])]

S += [P("7. Conclusion (Case Study 2)", h1),
      P(f"After removing {R['air_rows_before'] - R['air_rows_after']} extreme customers and scaling the data, three clustering methods were applied to {R['air_rows_after']:,} airline customers. K-Means and Hierarchical clustering both found four meaningful segments: low-activity members, credit-card earners, frequent flyers and a small Rewards-card group. The silhouette scores (about 0.28 to 0.32) show that the segments overlap somewhat, which is normal for real customer data. DBSCAN mainly separated a few unusual high-value customers as noise. K-Means is recommended because it is simple, gives balanced groups and is easy to explain to the business."),
      PageBreak()]

# ---------------- PART B ----------------
S += [Spacer(1, 6*cm), Paragraph("PART B", part), Spacer(1, 6),
      Paragraph("Case Study 5: Wine Quality Assessment", ParagraphStyle("pb", parent=part, fontSize=18, leading=24)), PageBreak()]
S += [P("8. Problem Statement", h1),
      P("The company currently judges wine quality through sensory assessment, which means trained tasters score each wine. Management wants to know whether laboratory measurements can explain differences in quality and support a data-driven quality check."),
      P("The task is to find which physicochemical characteristics are most strongly related to quality and to build a multiple linear regression model that predicts the quality score from the 11 laboratory measurements.")]
S += [P("9. Methodology", h1),
      P(f"The Vinho Verde wine data from Cortez et al. (2009) was used. The red wine file (1,599 samples) and the white wine file (4,898 samples) were combined into one dataset of <b>{R['wine_n']:,} wines</b>. Each wine has 11 measurements (fixed acidity, volatile acidity, citric acid, residual sugar, chlorides, free sulfur dioxide, total sulfur dioxide, density, pH, sulphates and alcohol) and a quality score given by tasters from 0 to 10. There are no missing values. The wine type (red or white) was not used as a predictor because the task asks for the 11 physicochemical attributes only."),
      P("The steps were: descriptive statistics, exploratory plots, a correlation study, an 80/20 train-test split (random state 42), a multiple linear regression, error metrics on the test set, a multicollinearity check using the Variance Inflation Factor (VIF), and finally a business recommendation.")]

d = R["desc"]; cv = R["cv"]
rows = [["Attribute", "Mean", "Median", "Mode", "Std. dev.", "Skewness", "Coeff. of variation"]]
for a in ["alcohol", "volatile acidity", "residual sugar"]:
    rows.append([a.capitalize(), f"{d[a]['Mean']:.3f}", f"{d[a]['Median']:.3f}", f"{d[a]['Mode']:.2f}", f"{d[a]['Std Dev']:.3f}", f"{d[a]['Skewness']:.3f}", f"{cv[a]:.1f}%"])
S += [P("10. Task 1: Statistical Analysis", h1), P("10.1 Descriptive statistics and variability", h2),
      table(rows, [3.4, 1.8, 1.8, 1.6, 2, 2, 2.6], "Descriptive statistics for alcohol, volatile acidity and residual sugar."),
      P(f"<b>Interpretation:</b> For <b>residual sugar</b> the mean ({d['residual sugar']['Mean']:.2f}) is much larger than the median ({d['residual sugar']['Median']:.1f}) and the skewness is high ({d['residual sugar']['Skewness']:.2f}), so a few very sweet wines pull the average upwards while most wines are fairly dry. <b>Volatile acidity</b> is also right-skewed ({d['volatile acidity']['Skewness']:.2f}). <b>Alcohol</b> is only mildly skewed ({d['alcohol']['Skewness']:.2f}) and is the most symmetric of the three."),
      P(f"<b>Relative variability:</b> Standard deviations cannot be compared directly because the attributes have different units and scales. The coefficient of variation (standard deviation divided by mean) removes the units. It is {cv['residual sugar']:.1f}% for residual sugar, {cv['volatile acidity']:.1f}% for volatile acidity and {cv['alcohol']:.1f}% for alcohol. <b>Residual sugar therefore has the greatest relative variability</b>, and alcohol the least."),
      P("10.2 Alcohol and quality", h2),
      P(f"Pearson's correlation between alcohol and quality is <b>r = {R['r_alc_q']:.3f}</b> (p-value far below 0.001). The sign is positive, so wines with more alcohol tend to receive higher quality scores. The strength is moderate: alcohol explains about {R['r_alc_q']**2*100:.0f}% of the variation in quality (r squared). The very small p-value shows the relationship is not due to chance. However, correlation does not prove that alcohol causes better quality, and other measurements also play a role.")]

qc = R["quality_counts"]
S += [P("11. Task 2: Exploratory Data Analysis", h1), P("11.1 Distribution of quality scores", h2),
      fig("cs5_quality_hist", "Number of wines at each quality score.", 11.5),
      P(f"<b>Interpretation:</b> The scores form a bell shape centred on 5 and 6 (mean {R['quality_mean']:.2f}, standard deviation {R['quality_std']:.2f}). {qc['6']:,} wines scored 6 and {qc['5']:,} scored 5, together 77% of the data. Only {qc['3']} wines scored 3 and {qc['9']} scored 9. Because extreme wines are so rare, any model has very little information to learn what makes a wine truly bad or truly excellent."),
      P("11.2 Alcohol by quality score", h2),
      fig("cs5_alcohol_box", "Box plot of alcohol content for each quality score.", 12.5),
      P(f"<b>Interpretation:</b> From quality 5 upwards, the median alcohol rises steadily: {R['alc_median_by_q']['5']}% for score 5, {R['alc_median_by_q']['6']}% for score 6, {R['alc_median_by_q']['7']}% for score 7 and {R['alc_median_by_q']['8']}% for score 8. Better wines therefore usually contain more alcohol. Scores 3 and 4 do not follow this pattern, but they have few wines. Several dots above the boxes (potential outliers) appear for scores 5, 6 and 7, meaning some wines have unusually high alcohol for their score, so alcohol alone cannot decide quality. The boxes of neighbouring scores overlap a lot, which already suggests that prediction will not be very precise."),
      P("11.3 Correlation heatmap", h2),
      fig("cs5_heatmap", "Correlation heatmap of the 11 physicochemical attributes and quality.", 13.5)]
cq = R["corr_with_quality"]
S += [P(f"<b>Interpretation:</b> The bottom row shows how each attribute relates to quality. Alcohol has the strongest positive relation ({cq['alcohol']:.2f}), followed by density with a negative relation ({cq['density']:.2f}). Volatile acidity ({cq['volatile acidity']:.2f}) and chlorides ({cq['chlorides']:.2f}) show weaker negative relations. Residual sugar, pH, sulphates and the sulfur dioxide measures are almost unrelated to quality on their own. The heatmap also shows that the inputs are related to each other, for example density and alcohol (-0.69) and free and total sulfur dioxide (0.72). This will matter for the regression."),
      P("11.4 Attributes most strongly related to quality", h2),
      P(f"Ranking by absolute Pearson correlation, the two strongest attributes are <b>alcohol (r = {cq['alcohol']:.3f}, positive)</b> and <b>density (r = {cq['density']:.3f}, negative)</b>. A positive sign means quality rises as the attribute rises; a negative sign means quality falls as it rises. Density is largely a reflection of alcohol, because alcohol is lighter than water, so the two are not completely independent signals.")]

mt = R["metrics"]
S += [P("12. Task 3: Predictive Modelling", h1), P("12.1 Model and test-set performance", h2),
      P(f"A multiple linear regression was fitted on a training set of 5,197 wines (80%) and tested on the remaining 1,300 wines (20%), using random state 42 for the split."),
      table([["Metric", "Value", "Meaning"],
             ["MAE", f"{mt['MAE']:.3f}", "On average the prediction is wrong by about 0.57 quality points"],
             ["MSE", f"{mt['MSE']:.3f}", "Average squared error"],
             ["RMSE", f"{mt['RMSE']:.3f}", "Typical error size (in quality points); penalises large mistakes"],
             ["R squared", f"{mt['R2']:.3f}", "The model explains about 26% of the variation in quality"]],
            [3, 2.5, 9.5], "Performance of the regression model on the test set."),
      P(f"<b>Interpretation:</b> If we always guessed the average quality, the RMSE would be {R['baseline_rmse']:.3f}. The model lowers this to {mt['RMSE']:.3f}, so it does learn something real, but the improvement is small. The training R squared ({R['train_r2']:.3f}) is close to the test value, so the model is not over-fitting; it is simply too simple to capture much more. After rounding the predictions, {R['exact_acc']*100:.0f}% of wines get exactly the right score and {R['within1_acc']*100:.0f}% are within one point."),
      P("12.2 Most influential predictors and multicollinearity", h2),
      P("Raw coefficients cannot be compared because attributes have different units. The model was therefore refitted on standardised variables, so that each coefficient shows the change in quality (in standard deviations) for a one standard deviation change in the attribute."),
      fig("cs5_std_coef", "Standardised regression coefficients (blue positive, red negative).", 12.5)]
sc = R["std_coef"]
S += [P(f"<b>Interpretation:</b> The two largest coefficients are <b>alcohol ({sc['alcohol']:+.2f})</b> and <b>residual sugar ({sc['residual sugar']:+.2f})</b>, followed closely by volatile acidity ({sc['volatile acidity']:+.2f}) and density ({sc['density']:+.2f}). The positive coefficient of residual sugar looks surprising, since its simple correlation with quality is almost zero ({cq['residual sugar']:.2f}). This is a warning sign of multicollinearity, so it was checked before trusting the numbers."),
      fig("cs5_vif", "Variance Inflation Factor of each attribute.", 12)]
vf = R["vif"]; vn = R["vif_no_density"]
rows = [["Attribute", "VIF (all 11)", "VIF (without density)", "Std. coeff. (all 11)", "Std. coeff. (without density)"]]
snd = R["std_coef_no_density"]
for a in vf:
    rows.append([a, f"{vf[a]:.2f}", f"{vn[a]:.2f}" if a in vn else "-", f"{sc[a]:+.3f}", f"{snd[a]:+.3f}" if a in snd else "-"])
S += [table(rows, [4, 2.4, 3, 2.8, 3.2], "VIF and standardised coefficients with and without density."),
      P(f"<b>Interpretation:</b> A VIF above 10 is usually considered serious. <b>Density has a VIF of {vf['density']:.1f}</b> and residual sugar {vf['residual sugar']:.1f}, because density can be largely predicted from alcohol and sugar. When two inputs carry the same information, the model can split their effect between them in an unstable way. After removing density, all VIF values fall below 3, the test R squared stays the same ({R['r2_no_density']:.3f} against {mt['R2']:.3f}), and the coefficient of residual sugar drops from {sc['residual sugar']:.2f} to {snd['residual sugar']:.2f}. Now the two most influential predictors are <b>alcohol ({snd['alcohol']:+.2f})</b> and <b>volatile acidity ({snd['volatile acidity']:+.2f})</b>."),
      P("In plain words: higher alcohol goes with higher quality, and higher volatile acidity (which gives a vinegar-like taste) goes with lower quality. The effects of density and residual sugar should not be interpreted on their own, because they are tied together with alcohol."),
      P("12.3 Predicted versus actual quality", h2),
      fig("cs5_pred_vs_actual", "Predicted and actual quality scores for the test set (small random jitter added to the actual scores so that points are visible).", 11.5),
      P("<b>Interpretation:</b> If the model were perfect, all points would lie on the red dashed line. Instead the predictions stay in a narrow band of about 4 to 7.7, while actual scores run from 3 to 9. Low-quality wines are over-predicted and high-quality wines are under-predicted, because the model plays safe and pulls predictions towards the average. Many wines with the same actual score receive very different predictions, which reflects the low R squared."),
      fig("cs5_residuals", "Distribution of prediction errors (actual minus predicted) on the test set.", 11),
      P("<b>Interpretation:</b> The errors are centred near zero, so the model is not biased on average, but for some wines the error is close to 2 points. <b>Limitations of the model:</b> (i) a straight-line model cannot capture curved or interacting effects between measurements; (ii) the quality scores are whole numbers from human opinion, which are noisy; (iii) there are very few extreme wines, so the model cannot learn them; and (iv) correlated inputs make individual coefficients unstable.")]

S += [P("13. Task 4: Business Decision-Making", h1), P("13.1 Measurements for quality screening", h2),
      P("Based on the analysis, two measurements deserve attention in a laboratory screening process:"),
      *B([f"<b>Alcohol:</b> it has the strongest positive relation with quality (r = {R['r_alc_q']:.2f}), the highest standardised coefficient, and its median rises clearly from quality 5 to 8. It is also easy and cheap to measure.",
          "<b>Volatile acidity:</b> it has a consistent negative relation with quality and stays one of the two most influential predictors once multicollinearity is handled. Wines with a high value are likely to taste of vinegar and be rated lower."]),
      P("Density was not chosen even though its correlation is high, because it mostly repeats the information in alcohol and sugar.", body),
      P("13.2 Can the model replace sensory evaluation?", h2),
      P(f"<b>No.</b> The test-set results do not support replacing tasters. The R squared is only {mt['R2']:.2f}, so about three quarters of the variation in quality is not explained by the 11 measurements. The average error is {mt['MAE']:.2f} quality points (RMSE {mt['RMSE']:.2f}); since most wines score 5 or 6, an error of that size can move a wine from average to good or poor. Only {R['exact_acc']*100:.0f}% of wines are given the exact score, and the model almost never predicts the very low or very high scores that matter most for decisions."),
      P("The model is still useful as a <b>low-cost screening aid</b>: wines with low alcohol and high volatile acidity can be flagged for closer tasting, while expert tasters make the final decision."),
      P("13.3 Limitations", h2),
      *B(["<b>Subjective and imbalanced target:</b> quality is an opinion score, and 77% of wines are rated 5 or 6. Very few wines are rated 3, 4, 8 or 9, so the model cannot learn the extremes.",
          "<b>Limits of the approach and data:</b> only a linear model was used, so non-linear effects were not captured; red and white wines were mixed without a wine-type variable; and all samples are Portuguese Vinho Verde wines, so the results may not apply to other wines. Correlated predictors (density, sugar, alcohol) also make individual coefficients less reliable."])]

S += [P("14. Conclusion (Case Study 5)", h1),
      P(f"Alcohol is the physicochemical measurement most closely linked with wine quality (r = {R['r_alc_q']:.2f}), followed by density, volatile acidity and chlorides. The multiple linear regression reached a test R squared of {mt['R2']:.2f} with an average error of {mt['MAE']:.2f} points. Density showed serious multicollinearity (VIF {vf['density']:.1f}), and after handling it, alcohol and volatile acidity were the two most influential predictors. The model is a helpful screening tool but is not reliable enough to replace human tasters. Better results may need non-linear models, separate models for red and white wine, and more samples of very good and very poor wines.")]

S += [P("15. Overall Conclusion", h1),
      P("Both case studies show how data science can support business decisions. Clustering turned raw airline records into four understandable customer segments, and regression showed which laboratory measurements relate to wine quality and how far a simple model can go. In both cases, the figures needed careful reading: high silhouette scores for DBSCAN and the large coefficient of residual sugar looked impressive at first but were explained by one dominant cluster and by multicollinearity respectively."),
      P("16. References", h1),
      *B(["Cortez, P., Cerdeira, A., Almeida, F., Matos, T. and Reis, J. (2009). Modeling wine preferences by data mining from physicochemical properties. <i>Decision Support Systems</i>, 47(4), 547-553.",
          "Shmueli, G. and Bruce, P. (2016). East-West Airlines dataset, <i>Data Mining for Business Analytics</i>.",
          "Pedregosa, F. et al. (2011). Scikit-learn: Machine learning in Python. <i>Journal of Machine Learning Research</i>, 12, 2825-2830.",
          "Ester, M., Kriegel, H.-P., Sander, J. and Xu, X. (1996). A density-based algorithm for discovering clusters in large spatial databases with noise (DBSCAN). <i>KDD-96</i>.",
          "Source code: Jupyter Notebook (FDS_Case_Studies.ipynb) and Python script in the submitted GitHub repository (link given in the submission form)."])]

i = 0
while i < len(S) - 1:
    if isinstance(S[i], Paragraph) and S[i].style.name in ("h1", "h2") and isinstance(S[i+1], KeepTogether):
        S[i:i+2] = [KeepTogether([S[i]] + list(S[i+1]._content))]
    i += 1
doc = Doc("report/FDS_Case_Studies_Report.pdf", title="FDS Case Studies 2 and 5", author="Madharapu Saketh")
doc.multiBuild(S)
print("done; figures:", fig_n[0], "tables:", tab_n[0])
