"""
City Care Hospital Management Dashboard
Author: Anisha M.
Run locally with:  streamlit run app.py
(Run generate_data.py once first to create hospital.db)
"""

import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime

# -----------------------------------------------------------------
# PAGE CONFIG + THEME
# -----------------------------------------------------------------
st.set_page_config(
    page_title="City Care Hospital | Management Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

PRIMARY = "#0B5FA5"      # medical blue
ACCENT = "#E63946"       # medical red
BG_CARD = "#F4F8FB"
SUCCESS = "#2A9D8F"

st.markdown(f"""
<style>
.main {{ background-color: #FAFCFE; }}
.metric-card {{
    background: linear-gradient(135deg, {PRIMARY} 0%, #073B66 100%);
    padding: 18px 20px;
    border-radius: 14px;
    color: white;
    text-align: left;
    box-shadow: 0 4px 12px rgba(0,0,0,0.12);
}}
.metric-card h2 {{ margin: 0; font-size: 26px; }}
.metric-card p {{ margin: 0; font-size: 13px; opacity: 0.85; }}
.section-title {{
    color: {PRIMARY};
    font-weight: 700;
    border-left: 5px solid {ACCENT};
    padding-left: 10px;
    margin-top: 10px;
}}
[data-testid="stSidebar"] {{
    background-color: #073B66;
}}
[data-testid="stSidebar"] * {{ color: white !important; }}
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------
# DATA LOADING
# -----------------------------------------------------------------
@st.cache_data
def load_data():
    conn = sqlite3.connect("hospital.db")
    patients = pd.read_sql("SELECT * FROM patients", conn)
    doctors = pd.read_sql("SELECT * FROM doctors", conn)
    appointments = pd.read_sql("SELECT * FROM appointments", conn)
    bills = pd.read_sql("SELECT * FROM bills", conn)
    wards = pd.read_sql("SELECT * FROM wards", conn)
    beds = pd.read_sql("SELECT * FROM bed_allocations", conn)
    conn.close()

    appointments["appt_date"] = pd.to_datetime(appointments["appt_date"])
    bills["bill_date"] = pd.to_datetime(bills["bill_date"])
    beds["admit_date"] = pd.to_datetime(beds["admit_date"])
    beds["discharge_date"] = pd.to_datetime(beds["discharge_date"])
    return patients, doctors, appointments, bills, wards, beds


try:
    patients, doctors, appointments, bills, wards, beds = load_data()
except Exception:
    st.error("⚠️ hospital.db not found. Please run `python generate_data.py` first, "
             "then restart this app.")
    st.stop()

DEPARTMENTS = sorted(patients["department"].unique())

# -----------------------------------------------------------------
# SIDEBAR NAVIGATION
# -----------------------------------------------------------------
st.sidebar.markdown("## 🏥 City Care Hospital")
st.sidebar.caption("Hospital Management Dashboard")
st.sidebar.markdown("---")

module = st.sidebar.radio(
    "Choose a module",
    [
        "🏠 Overview",
        "🧑‍⚕️ Patients & Appointments",
        "💰 Billing & Revenue",
        "🛏️ Bed & Ward Occupancy",
        "📅 Doctor Scheduling",
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("Prepared by Anisha M.")
st.sidebar.caption(f"Data as of {datetime(2026,7,14).strftime('%d %b %Y')}")


# ===================================================================
# MODULE 1: OVERVIEW
# ===================================================================
if module == "🏠 Overview":
    st.title("🏥 City Care Hospital — Executive Overview")
    st.caption("A single view across patients, appointments, revenue and bed occupancy")

    total_patients = len(patients)
    total_appts = len(appointments)
    total_revenue = int(bills["total_amount"].sum())
    total_beds = int(wards["total_beds"].sum())
    occupied_beds = len(beds[beds["bed_status"] == "Occupied"])
    occ_rate = round((occupied_beds / total_beds) * 100, 1)

    c1, c2, c3, c4 = st.columns(4)
    for col, label, value in zip(
        [c1, c2, c3, c4],
        ["Total Patients", "Total Appointments", "Total Revenue", "Bed Occupancy"],
        [f"{total_patients}", f"{total_appts}", f"₹{total_revenue:,}", f"{occ_rate}%"]
    ):
        col.markdown(f"""<div class="metric-card"><p>{label}</p><h2>{value}</h2></div>""",
                      unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="section-title">Patients by Department</p>', unsafe_allow_html=True)
        dept_counts = patients["department"].value_counts().reset_index()
        dept_counts.columns = ["department", "count"]
        fig = px.bar(dept_counts, x="department", y="count", color="department",
                     color_discrete_sequence=px.colors.qualitative.Bold, text="count")
        fig.update_layout(showlegend=False, height=380)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">Revenue by Department</p>', unsafe_allow_html=True)
        rev_dept = bills.groupby("department")["total_amount"].sum().reset_index()
        fig = px.pie(rev_dept, names="department", values="total_amount", hole=0.45,
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(height=380)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<p class="section-title">Daily Appointment Volume (Last 30 Days)</p>',
                unsafe_allow_html=True)
    daily = appointments.groupby(appointments["appt_date"].dt.date).size().reset_index()
    daily.columns = ["date", "appointments"]
    fig = px.area(daily, x="date", y="appointments",
                   color_discrete_sequence=[PRIMARY])
    fig.update_layout(height=320)
    st.plotly_chart(fig, use_container_width=True)


# ===================================================================
# MODULE 2: PATIENTS & APPOINTMENTS
# ===================================================================
elif module == "🧑‍⚕️ Patients & Appointments":
    st.title("🧑‍⚕️ Patients & Appointment Scheduling")

    dept_filter = st.multiselect("Filter by Department", DEPARTMENTS, default=DEPARTMENTS)
    status_filter = st.multiselect(
        "Filter by Appointment Status",
        appointments["status"].unique().tolist(),
        default=appointments["status"].unique().tolist()
    )

    filtered_patients = patients[patients["department"].isin(dept_filter)]
    filtered_appts = appointments[
        appointments["department"].isin(dept_filter) &
        appointments["status"].isin(status_filter)
    ]

    c1, c2, c3 = st.columns(3)
    c1.metric("Patients (filtered)", len(filtered_patients))
    c2.metric("Appointments (filtered)", len(filtered_appts))
    c3.metric("Completed Rate",
              f"{round((filtered_appts['status'].eq('Completed').mean() or 0) * 100, 1)}%")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="section-title">Department-wise Patient Load</p>',
                    unsafe_allow_html=True)
        dl = filtered_patients["department"].value_counts().reset_index()
        dl.columns = ["department", "patients"]
        fig = px.bar(dl, x="department", y="patients", color="department", text="patients",
                     color_discrete_sequence=px.colors.qualitative.Prism)
        fig.update_layout(showlegend=False, height=360)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">Daily OPD Count</p>', unsafe_allow_html=True)
        opd = filtered_appts.groupby(filtered_appts["appt_date"].dt.date).size().reset_index()
        opd.columns = ["date", "count"]
        fig = px.line(opd, x="date", y="count", markers=True,
                       color_discrete_sequence=[ACCENT])
        fig.update_layout(height=360)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<p class="section-title">Appointment Status Breakdown</p>', unsafe_allow_html=True)
    status_counts = filtered_appts["status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]
    fig = px.pie(status_counts, names="status", values="count", hole=0.4,
                 color_discrete_sequence=px.colors.qualitative.Safe)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<p class="section-title">Patient Directory</p>', unsafe_allow_html=True)
    st.dataframe(filtered_patients, use_container_width=True, height=300)

    st.markdown('<p class="section-title">Appointment Log</p>', unsafe_allow_html=True)
    merged = filtered_appts.merge(patients[["patient_id", "name"]], on="patient_id") \
                            .merge(doctors[["doctor_id", "name"]], on="doctor_id",
                                   suffixes=("_patient", "_doctor"))
    st.dataframe(
        merged[["appointment_id", "name_patient", "name_doctor", "department",
                "appt_date", "time_slot", "status"]]
        .rename(columns={"name_patient": "patient", "name_doctor": "doctor"})
        .sort_values("appt_date", ascending=False),
        use_container_width=True, height=320
    )


# ===================================================================
# MODULE 3: BILLING & REVENUE
# ===================================================================
elif module == "💰 Billing & Revenue":
    st.title("💰 Billing & Revenue Analytics")

    dept_filter = st.multiselect("Filter by Department", DEPARTMENTS, default=DEPARTMENTS,
                                  key="bill_dept")
    date_range = st.date_input(
        "Date Range",
        value=(bills["bill_date"].min().date(), bills["bill_date"].max().date())
    )

    fb = bills[bills["department"].isin(dept_filter)]
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = date_range
        fb = fb[(fb["bill_date"].dt.date >= start) & (fb["bill_date"].dt.date <= end)]

    total_rev = int(fb["total_amount"].sum())
    avg_bill = int(fb["total_amount"].mean()) if len(fb) else 0
    top_dept = fb.groupby("department")["total_amount"].sum().idxmax() if len(fb) else "-"

    c1, c2, c3 = st.columns(3)
    c1.markdown(f"""<div class="metric-card"><p>Total Revenue</p><h2>₹{total_rev:,}</h2></div>""",
                unsafe_allow_html=True)
    c2.markdown(f"""<div class="metric-card"><p>Average Bill</p><h2>₹{avg_bill:,}</h2></div>""",
                unsafe_allow_html=True)
    c3.markdown(f"""<div class="metric-card"><p>Top Revenue Dept</p><h2>{top_dept}</h2></div>""",
                unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="section-title">Revenue by Department</p>', unsafe_allow_html=True)
        rd = fb.groupby("department")["total_amount"].sum().reset_index().sort_values(
            "total_amount", ascending=False)
        fig = px.bar(rd, x="department", y="total_amount", text="total_amount",
                     color="department", color_discrete_sequence=px.colors.qualitative.Bold)
        fig.update_traces(texttemplate="₹%{text:,.0f}")
        fig.update_layout(showlegend=False, height=380)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">Payment Mode Split</p>', unsafe_allow_html=True)
        pm = fb["payment_mode"].value_counts().reset_index()
        pm.columns = ["payment_mode", "count"]
        fig = px.pie(pm, names="payment_mode", values="count", hole=0.45,
                     color_discrete_sequence=[PRIMARY, ACCENT, SUCCESS])
        fig.update_layout(height=380)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<p class="section-title">Monthly Revenue Trend</p>', unsafe_allow_html=True)
    trend = fb.groupby(fb["bill_date"].dt.date)["total_amount"].sum().reset_index()
    trend.columns = ["date", "revenue"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=trend["date"], y=trend["revenue"], fill="tozeroy",
                              line=dict(color=PRIMARY)))
    fig.update_layout(height=320)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<p class="section-title">Billing Records</p>', unsafe_allow_html=True)
    st.dataframe(fb.sort_values("bill_date", ascending=False), use_container_width=True, height=320)


# ===================================================================
# MODULE 4: BED & WARD OCCUPANCY
# ===================================================================
elif module == "🛏️ Bed & Ward Occupancy":
    st.title("🛏️ Bed & Ward Occupancy Tracker")

    occ = beds[beds["bed_status"] == "Occupied"].groupby("ward_type").size()
    ward_summary = wards.copy()
    ward_summary["occupied"] = ward_summary["ward_type"].map(occ).fillna(0).astype(int)
    ward_summary["available"] = ward_summary["total_beds"] - ward_summary["occupied"]
    ward_summary["occupancy_pct"] = round(
        (ward_summary["occupied"] / ward_summary["total_beds"]) * 100, 1)

    cols = st.columns(len(ward_summary))
    for col, (_, row) in zip(cols, ward_summary.iterrows()):
        alert = "🔴 FULL" if row["occupancy_pct"] >= 100 else (
            "🟡 Near Full" if row["occupancy_pct"] >= 80 else "🟢 Available")
        col.markdown(f"""
        <div class="metric-card">
        <p>{row['ward_type']} Ward</p>
        <h2>{row['occupied']}/{row['total_beds']}</h2>
        <p>{row['occupancy_pct']}% occupied &nbsp; {alert}</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="section-title">Occupied vs Available Beds</p>',
                    unsafe_allow_html=True)
        melt = ward_summary.melt(id_vars="ward_type", value_vars=["occupied", "available"],
                                  var_name="status", value_name="beds")
        fig = px.bar(melt, x="ward_type", y="beds", color="status", barmode="stack",
                     color_discrete_map={"occupied": ACCENT, "available": SUCCESS})
        fig.update_layout(height=380)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">Ward-wise Occupancy %</p>', unsafe_allow_html=True)
        fig = px.bar(ward_summary, x="ward_type", y="occupancy_pct", text="occupancy_pct",
                     color="ward_type", color_discrete_sequence=px.colors.qualitative.Dark2)
        fig.add_hline(y=80, line_dash="dash", line_color="orange",
                      annotation_text="Near-full threshold")
        fig.update_layout(showlegend=False, height=380)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<p class="section-title">Occupancy Trend Over the Month</p>',
                unsafe_allow_html=True)
    date_range_all = pd.date_range(beds["admit_date"].min(), datetime(2026, 7, 14))
    trend_rows = []
    for d in date_range_all:
        admitted_that_day = beds[
            (beds["admit_date"] <= d) &
            ((beds["discharge_date"].isna()) | (beds["discharge_date"] >= d))
        ]
        trend_rows.append({"date": d, "occupied_beds": len(admitted_that_day)})
    trend_df = pd.DataFrame(trend_rows)
    fig = px.line(trend_df, x="date", y="occupied_beds", markers=False,
                  color_discrete_sequence=[PRIMARY])
    fig.add_hline(y=int(wards["total_beds"].sum()), line_dash="dot", line_color=ACCENT,
                  annotation_text="Total hospital capacity")
    fig.update_layout(height=340)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<p class="section-title">Bed Allocation Records</p>', unsafe_allow_html=True)
    bed_display = beds.merge(patients[["patient_id", "name"]], on="patient_id")
    st.dataframe(
        bed_display[["allocation_id", "name", "ward_type", "admit_date",
                     "discharge_date", "bed_status"]].sort_values("admit_date", ascending=False),
        use_container_width=True, height=320
    )


# ===================================================================
# MODULE 5: DOCTOR SCHEDULING
# ===================================================================
elif module == "📅 Doctor Scheduling":
    st.title("📅 Doctor-Patient Scheduling System")

    dept_filter = st.selectbox("Filter by Department", ["All"] + DEPARTMENTS)
    doc_pool = doctors if dept_filter == "All" else doctors[doctors["department"] == dept_filter]
    doctor_names = ["All"] + doc_pool["name"].tolist()
    doctor_filter = st.selectbox("Filter by Doctor", doctor_names)

    fa = appointments.merge(doctors, on="doctor_id", suffixes=("", "_doc"))
    if dept_filter != "All":
        fa = fa[fa["department"] == dept_filter]
    if doctor_filter != "All":
        fa = fa[fa["name"] == doctor_filter]

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Appointments", len(fa))
    c2.metric("No-Shows", int((fa["status"] == "No-Show").sum()))
    c3.metric("Completed", int((fa["status"] == "Completed").sum()))

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="section-title">Most-Booked Doctors</p>', unsafe_allow_html=True)
        booked = appointments.merge(doctors, on="doctor_id")["name"].value_counts().head(10) \
            .reset_index()
        booked.columns = ["doctor", "appointments"]
        fig = px.bar(booked, x="appointments", y="doctor", orientation="h",
                     color="appointments", color_continuous_scale="Blues")
        fig.update_layout(height=420, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">No-Show Rate by Department</p>',
                    unsafe_allow_html=True)
        noshow = appointments.groupby("department").apply(
            lambda x: round((x["status"] == "No-Show").mean() * 100, 1)
        ).reset_index()
        noshow.columns = ["department", "no_show_pct"]
        fig = px.bar(noshow, x="department", y="no_show_pct", text="no_show_pct",
                     color="department", color_discrete_sequence=px.colors.qualitative.Set3)
        fig.update_layout(showlegend=False, height=420)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<p class="section-title">Doctor Availability / Slot Schedule</p>',
                unsafe_allow_html=True)
    if doctor_filter != "All":
        sched = fa[["appt_date", "time_slot", "status"]].sort_values(
            ["appt_date", "time_slot"])
        sched = sched.merge(appointments.merge(patients[["patient_id", "name"]],
                             on="patient_id")[["appt_date", "time_slot", "name"]],
                             on=["appt_date", "time_slot"], how="left")
        st.dataframe(sched.rename(columns={"name": "patient"}), use_container_width=True, height=320)
    else:
        st.info("Select a specific doctor above to view their full slot-by-slot schedule "
                "(double-booking is prevented at data-entry level — one doctor can hold "
                "only one appointment per date & time slot).")

    st.markdown('<p class="section-title">Doctor Directory</p>', unsafe_allow_html=True)
    st.dataframe(doc_pool, use_container_width=True, height=280)
