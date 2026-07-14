# City Care Hospital — Management Dashboard
**Author:** Anisha M.

A unified Streamlit dashboard for a hospital management system, combining five modules
into one app with a sidebar navigator:

1. 🏠 **Overview** — KPI cards + department load + revenue split + daily OPD trend
2. 🧑‍⚕️ **Patients & Appointments** — 120 patients across 5 departments, appointment log,
   department-wise patient load, daily OPD count chart
3. 💰 **Billing & Revenue** — consultation + test + medicine + room charges rolled into
   bills, revenue by department, payment mode split (Cash/Insurance/Card), monthly trend
4. 🛏️ **Bed & Ward Occupancy** — General/ICU/Private wards with fixed capacity,
   real-time occupancy %, full/near-full alerts, occupancy trend over the month
5. 📅 **Doctor Scheduling** — doctor availability, double-booking prevention (one doctor
   can only hold one appointment per date + time slot), no-show tracking,
   most-booked doctors chart

## How to run locally (Windows / IDLE users)

1. Install dependencies:
   ```
   pip install streamlit pandas plotly
   ```
2. Generate the database (run this once, or again any time to reset the data):
   ```
   python generate_data.py
   ```
3. Launch the dashboard:
   ```
   streamlit run app.py
   ```
4. Your browser will open automatically at `http://localhost:8501`

## Deploying to Streamlit Community Cloud

1. Push these 3 files to a GitHub repo: `app.py`, `generate_data.py`, `requirements.txt`
   - **Important:** keep the filename exactly `requirements.txt` (not a custom name) —
     Streamlit Cloud only auto-detects that exact filename.
2. Since `hospital.db` is generated locally and not stored in GitHub, add this as the
   first line inside `app.py`'s `load_data()` function fallback, OR simply also commit
   the generated `hospital.db` file to the repo so the cloud app has data immediately.
   (Easiest option: commit `hospital.db` alongside the scripts.)
3. Go to [share.streamlit.io](https://share.streamlit.io), connect your GitHub repo,
   set the main file to `app.py`, and deploy.

## Data notes
- All data is synthetically generated with Indian names/cities for demonstration.
- 120 patients, 25 doctors (5 per department), ~320 appointments over a rolling 30-day
  window, bills for all completed appointments + admitted patients, 3 wards
  (General: 40 beds, ICU: 10 beds, Private: 15 beds), 55 bed allocations.
- Re-run `generate_data.py` any time to regenerate a fresh dataset (drops and recreates
  all tables, so it's safe to re-run repeatedly).
