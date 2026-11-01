import numpy as np, pandas as pd, json, pathlib, sqlite3
np.random.seed(123)
root=pathlib.Path(__file__).parent; (root/"data").mkdir(exist_ok=True); (root/"results").mkdir(exist_ok=True); (root/"warehouse").mkdir(exist_ok=True)
rows=[]
for i in range(2000):
    rows.append([i+1, str((pd.Timestamp("2025-01-01")+pd.Timedelta(days=int(np.random.randint(0,180)))).date()), np.random.choice(["North","South","East","West"]), np.random.choice(["Electronics","Home","Clothing"]), round(float(np.random.uniform(20,500)),2), int(np.random.randint(1,5)), np.random.choice(["Completed","Completed","Completed","Refunded","Pending"],p=[.85,.05,.05,.03,.02]) if False else np.random.choice(["Completed","Refunded","Pending"],p=[.9,.05,.05])])
df=pd.DataFrame(rows,columns=["order_id","order_date","region","category","revenue","quantity","status"])
# inject quality issues deliberately (SYNTHETIC)
df.loc[5,"revenue"]=None; df.loc[10,"region"]=None; df=df.drop_duplicates(subset=["order_id"],keep="first")
raw=len(df); df.to_csv(root/"data/raw_operations.csv",index=False)
checks=[]
def chk(name, passed, details): checks.append({"check":name,"passed":bool(passed),"details":str(details)})
chk("no_duplicate_order_id", df.order_id.duplicated().sum()==0, f"duplicates={int(df.order_id.duplicated().sum())}")
chk("revenue_not_null", df.revenue.isna().sum()<=2, f"null_revenue={int(df.revenue.isna().sum())}")
chk("region_not_null", df.region.isna().sum()<=2, f"null_region={int(df.region.isna().sum())}")
chk("revenue_positive", (df.revenue.dropna()>0).all(), "all non-null revenue >0")
chk("quantity_positive", (df.quantity>0).all(), "quantity >0")
chk("status_valid", set(df.status.unique())<= {"Completed","Refunded","Pending"}, f"statuses={sorted(df.status.unique())}")
chk("order_date_parseable", pd.to_datetime(df.order_date,errors="coerce").notna().all(), "all dates parse")
chk("row_count_threshold", len(df)>=1900, f"rows={len(df)}")
clean=df.dropna(subset=["revenue","region"]).copy()
con=sqlite3.connect(root/"warehouse/kpi.db"); clean.to_sql("operations",con,if_exists="replace",index=False); con.close()
completed=clean[clean.status=="Completed"]
kpis={"raw_rows":int(raw),"clean_rows":int(len(clean)),"quarantined_rows":int(raw-len(clean)),"data_quality_checks":len(checks),"checks_passed":int(sum(c['passed'] for c in checks)),"total_revenue_completed":round(float(completed.revenue.sum()),2),"orders_completed":int(len(completed)),"aov_completed":round(float(completed.revenue.mean()),2),"refund_rate":round(float((clean.status=="Refunded").mean()),4),"top_region":str(completed.groupby("region").revenue.sum().idxmax())}
report="# Automated KPI Report (SYNTHETIC data)\n\n"+json.dumps(kpis,indent=2)+"\n\nChecks:\n"+json.dumps(checks,indent=2)+"\n"
(root/"results/kpi_report.md").write_text(report); (root/"results/summary.json").write_text(json.dumps({"kpis":kpis,"checks":checks},indent=2)); print(json.dumps(kpis,indent=2)); print(f"checks: {len(checks)}")
