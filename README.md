# Fundamentals of Data Science - Case Studies 2 and 5

**Name:** Madharapu Saketh  
**Roll No:** 160124733183  
**Section / Year:** CSE-3, III Year  
**Faculty:** S. Durga Devi  
**Institution:** Chaitanya Bharathi Institute of Technology (CBIT), Hyderabad

| Case Study | Topic |
|---|---|
| 2 | Clustering analysis of East-West Airlines customers (K-Means, Hierarchical, DBSCAN) |
| 5 | Wine quality assessment (statistics, EDA, multiple linear regression) |

## Repository contents

| File / folder | Description |
|---|---|
| `FDS_Case_Studies.ipynb` | Main notebook with code, outputs, plots and observations for both case studies |
| `FDS_Case_Studies.py` | The same code exported as a Python script |
| `report/FDS_Case_Studies_Report.pdf` | Final PDF report |
| `data/` | East-West Airlines Excel file and red / white wine CSV files |
| `figures/` | All plots produced by the notebook |
| `results/summary.json` | Key numbers produced by the notebook (used in the report) |
| `build_report.py` | Script that builds the PDF report from the results and figures |

## How to run

```bash
pip install -r requirements.txt
jupyter notebook FDS_Case_Studies.ipynb     # run all cells from the repository root
python build_report.py                      # optional: rebuild the PDF report
```

A fixed random state (42) is used everywhere, so results are reproducible.

## Data sources
* East-West Airlines: Shmueli and Bruce, *Data Mining for Business Analytics* (2016).
* Wine quality: Cortez et al. (2009), UCI Machine Learning Repository.
