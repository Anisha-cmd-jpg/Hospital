"""
City Care Hospital - Database Generator
Author: Anisha M.
Creates hospital.db (SQLite) with realistic sample data:
patients, doctors, appointments, bills, wards, bed_allocations
Run this ONCE before running app.py
"""

import sqlite3
import random
from datetime import datetime, timedelta

random.seed(42)

# ---------------------------------------------------------
# 1. REFERENCE DATA
# ---------------------------------------------------------

DEPARTMENTS = ["Cardiology", "Orthopedics", "Pediatrics", "General Medicine", "ENT"]

FIRST_NAMES_M = ["Arjun", "Vikram", "Rohit", "Karthik", "Suresh", "Ganesh", "Manoj",
                  "Praveen", "Sanjay", "Anand", "Ravi", "Dinesh", "Naveen", "Ashok",
                  "Vijay", "Prakash", "Ramesh", "Senthil", "Balaji", "Kumar"]

FIRST_NAMES_F = ["Anisha", "Priya", "Divya", "Meena", "Kavya", "Lakshmi", "Sneha",
                  "Pooja", "Swathi", "Deepa", "Anjali", "Nithya", "Radha", "Shalini",
                  "Kalpana", "Bhavani", "Revathi", "Uma", "Geetha", "Vidya"]

LAST_NAMES = ["Iyer", "Nair", "Menon", "Pillai", "Reddy", "Rao", "Naidu", "Chettiar",
              "Gupta", "Sharma", "Krishnan", "Subramaniam", "Raman", "Murthy", "Varma"]

CITIES = ["Chennai", "Coimbatore", "Madurai", "Trichy", "Salem", "Erode",
          "Tirunelveli", "Vellore", "Thanjavur", "Tiruppur"]

BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]

SPECIALIZATIONS = {
    "Cardiology": "Cardiologist",
    "Orthopedics": "Orthopedic Surgeon",
    "Pediatrics": "Pediatrician",
    "General Medicine": "General Physician",
    "ENT": "ENT Specialist",
}

WARD_TYPES = [("General", 40, 800), ("ICU", 10, 4500), ("Private", 15, 2500)]
# (ward_type, total_beds, per_day_charge)

TIME_SLOTS = ["09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM", "11:00 AM",
              "11:30 AM", "02:00 PM", "02:30 PM", "03:00 PM", "03:30 PM",
              "04:00 PM", "04:30 PM"]

PAYMENT_MODES = ["Cash", "Insurance", "Card"]
APPT_STATUS_WEIGHTS = [("Completed", 0.65), ("Scheduled", 0.15),
                        ("Cancelled", 0.10), ("No-Show", 0.10)]

TESTS = {
    "Cardiology": ["ECG", "Echo Test", "Lipid Profile", "Stress Test"],
    "Orthopedics": ["X-Ray", "MRI Scan", "Bone Density Test"],
    "Pediatrics": ["Blood Test", "Growth Screening", "Vaccination Panel"],
    "General Medicine": ["Blood Test", "Urine Test", "Diabetes Panel"],
    "ENT": ["Hearing Test", "Endoscopy", "Allergy Test"],
}

random_name_used = set()


def make_name():
    while True:
        gender = random.choice(["M", "F"])
        first = random.choice(FIRST_NAMES_M if gender == "M" else FIRST_NAMES_F)
        last = random.choice(LAST_NAMES)
        full = f"{first} {last}"
        key = full + gender
        if key not in random_name_used:
            random_name_used.add(key)
            return full, "Male" if gender == "M" else "Female"


def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))


# ---------------------------------------------------------
# 2. DATABASE SETUP
# ---------------------------------------------------------

conn = sqlite3.connect("hospital.db")
cur = conn.cursor()

cur.executescript("""
DROP TABLE IF EXISTS bed_allocations;
DROP TABLE IF EXISTS bills;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS patients;
DROP TABLE IF EXISTS doctors;
DROP TABLE IF EXISTS wards;

CREATE TABLE patients (
    patient_id      TEXT PRIMARY KEY,
    name            TEXT,
    age             INTEGER,
    gender          TEXT,
    contact         TEXT,
    blood_group     TEXT,
    department      TEXT,
    city            TEXT,
    registration_date TEXT
);

CREATE TABLE doctors (
    doctor_id       TEXT PRIMARY KEY,
    name            TEXT,
    department      TEXT,
    specialization  TEXT,
    consultation_fee INTEGER,
    experience_years INTEGER,
    phone           TEXT
);

CREATE TABLE appointments (
    appointment_id  TEXT PRIMARY KEY,
    patient_id      TEXT,
    doctor_id       TEXT,
    department      TEXT,
    appt_date       TEXT,
    time_slot       TEXT,
    status          TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
);

CREATE TABLE bills (
    bill_id             TEXT PRIMARY KEY,
    patient_id          TEXT,
    appointment_id      TEXT,
    department          TEXT,
    consultation_fee    INTEGER,
    test_charges        INTEGER,
    medicine_charges    INTEGER,
    room_charges        INTEGER,
    total_amount        INTEGER,
    payment_mode        TEXT,
    bill_date           TEXT
);

CREATE TABLE wards (
    ward_id     TEXT PRIMARY KEY,
    ward_type   TEXT,
    total_beds  INTEGER,
    per_day_charge INTEGER
);

CREATE TABLE bed_allocations (
    allocation_id   TEXT PRIMARY KEY,
    patient_id      TEXT,
    ward_id         TEXT,
    ward_type       TEXT,
    admit_date      TEXT,
    discharge_date  TEXT,
    bed_status      TEXT
);
""")

# ---------------------------------------------------------
# 3. DOCTORS  (5 doctors per department = 25 doctors)
# ---------------------------------------------------------

doctors = []
doc_counter = 1
for dept in DEPARTMENTS:
    for _ in range(5):
        name, gender = make_name()
        doc_id = f"DOC{doc_counter:03d}"
        doctors.append((
            doc_id,
            "Dr. " + name,
            dept,
            SPECIALIZATIONS[dept],
            random.choice([400, 500, 600, 700, 800, 900]),
            random.randint(2, 25),
            f"9{random.randint(100000000, 999999999)}"
        ))
        doc_counter += 1

cur.executemany("INSERT INTO doctors VALUES (?,?,?,?,?,?,?)", doctors)

# ---------------------------------------------------------
# 4. PATIENTS  (120 patients across 5 departments)
# ---------------------------------------------------------

TODAY = datetime(2026, 7, 14)
MONTH_START = TODAY - timedelta(days=29)

patients = []
for i in range(1, 121):
    name, gender = make_name()
    patient_id = f"PAT{i:04d}"
    dept = random.choice(DEPARTMENTS)
    reg_date = random_date(MONTH_START, TODAY)
    patients.append((
        patient_id,
        name,
        random.randint(1, 85),
        gender,
        f"9{random.randint(100000000, 999999999)}",
        random.choice(BLOOD_GROUPS),
        dept,
        random.choice(CITIES),
        reg_date.strftime("%Y-%m-%d")
    ))

cur.executemany("INSERT INTO patients VALUES (?,?,?,?,?,?,?,?,?)", patients)

# ---------------------------------------------------------
# 5. APPOINTMENTS  (~320 appointments over the last 30 days)
#    with double-booking prevention (doctor+date+time_slot unique)
# ---------------------------------------------------------

appointments = []
booked_slots = set()  # (doctor_id, date, time_slot)
appt_counter = 1
target_appts = 320
attempts = 0

doctors_by_dept = {}
for d in doctors:
    doctors_by_dept.setdefault(d[2], []).append(d[0])

while len(appointments) < target_appts and attempts < target_appts * 10:
    attempts += 1
    patient = random.choice(patients)
    dept = patient[6]
    doctor_id = random.choice(doctors_by_dept[dept])
    appt_date = random_date(MONTH_START, TODAY)
    time_slot = random.choice(TIME_SLOTS)
    key = (doctor_id, appt_date.strftime("%Y-%m-%d"), time_slot)

    if key in booked_slots:
        continue  # prevents double-booking a doctor for same date+slot
    booked_slots.add(key)

    status = random.choices(
        [s for s, w in APPT_STATUS_WEIGHTS],
        weights=[w for s, w in APPT_STATUS_WEIGHTS]
    )[0]
    # future-dated appointments can only be "Scheduled"
    if appt_date > TODAY:
        status = "Scheduled"

    appt_id = f"APT{appt_counter:04d}"
    appointments.append((
        appt_id, patient[0], doctor_id, dept,
        appt_date.strftime("%Y-%m-%d"), time_slot, status
    ))
    appt_counter += 1

cur.executemany("INSERT INTO appointments VALUES (?,?,?,?,?,?,?)", appointments)

# ---------------------------------------------------------
# 6. BILLS  (generated for Completed appointments only)
# ---------------------------------------------------------

doctor_fee_lookup = {d[0]: d[4] for d in doctors}
bills = []
bill_counter = 1
for appt in appointments:
    appt_id, patient_id, doctor_id, dept, appt_date, slot, status = appt
    if status != "Completed":
        continue

    consultation_fee = doctor_fee_lookup[doctor_id]
    num_tests = random.randint(0, 2)
    test_charges = sum(random.choice([250, 400, 600, 900, 1200]) for _ in range(num_tests))
    medicine_charges = random.choice([0, 150, 300, 450, 600, 800])
    room_charges = 0  # room charges handled separately via bed_allocations
    total = consultation_fee + test_charges + medicine_charges + room_charges

    bills.append((
        f"BILL{bill_counter:04d}",
        patient_id,
        appt_id,
        dept,
        consultation_fee,
        test_charges,
        medicine_charges,
        room_charges,
        total,
        random.choices(PAYMENT_MODES, weights=[0.35, 0.40, 0.25])[0],
        appt_date
    ))
    bill_counter += 1

cur.executemany("INSERT INTO bills VALUES (?,?,?,?,?,?,?,?,?,?,?)", bills)

# ---------------------------------------------------------
# 7. WARDS
# ---------------------------------------------------------

wards = []
for idx, (wtype, capacity, charge) in enumerate(WARD_TYPES, start=1):
    wards.append((f"WARD{idx}", wtype, capacity, charge))
cur.executemany("INSERT INTO wards VALUES (?,?,?,?)", wards)

# ---------------------------------------------------------
# 8. BED ALLOCATIONS
#    Respect ward capacity; ~55 patients get admitted at some point
#    Some are still admitted (discharge_date = NULL), rest discharged
# ---------------------------------------------------------

ward_capacity = {w[1]: w[2] for w in wards}
ward_id_lookup = {w[1]: w[0] for w in wards}
current_occupancy = {w[1]: 0 for w in wards}

admit_candidates = random.sample(patients, 55)
allocations = []
alloc_counter = 1

for patient in admit_candidates:
    ward_type = random.choices(
        ["General", "ICU", "Private"], weights=[0.6, 0.15, 0.25]
    )[0]

    if current_occupancy[ward_type] >= ward_capacity[ward_type]:
        # ward full -> try another ward type
        alt = [w for w in ["General", "ICU", "Private"]
               if current_occupancy[w] < ward_capacity[w]]
        if not alt:
            continue
        ward_type = random.choice(alt)

    admit_date = random_date(MONTH_START, TODAY)
    stay_days = random.randint(1, 10)
    discharge_date = admit_date + timedelta(days=stay_days)

    if discharge_date > TODAY:
        discharge_date_str = None
        bed_status = "Occupied"
        current_occupancy[ward_type] += 1
    else:
        discharge_date_str = discharge_date.strftime("%Y-%m-%d")
        bed_status = "Discharged"

    allocations.append((
        f"BED{alloc_counter:04d}",
        patient[0],
        ward_id_lookup[ward_type],
        ward_type,
        admit_date.strftime("%Y-%m-%d"),
        discharge_date_str,
        bed_status
    ))
    alloc_counter += 1

cur.executemany("INSERT INTO bed_allocations VALUES (?,?,?,?,?,?,?)", allocations)

# ---------------------------------------------------------
# 9. ADD ROOM CHARGES TO BILLS FOR DISCHARGED (ADMITTED) PATIENTS
#    (extends a matching bill if one exists for that patient, else creates one)
# ---------------------------------------------------------

ward_charge_lookup = {w[1]: w[3] for w in wards}
extra_bills = []
for alloc in allocations:
    _, patient_id, ward_id, ward_type, admit_date, discharge_date, status = alloc
    if status != "Discharged":
        continue
    stay_days = (datetime.strptime(discharge_date, "%Y-%m-%d") -
                 datetime.strptime(admit_date, "%Y-%m-%d")).days
    room_total = stay_days * ward_charge_lookup[ward_type]

    dept = next(p[6] for p in patients if p[0] == patient_id)
    extra_bills.append((
        f"BILL{bill_counter:04d}",
        patient_id,
        None,
        dept,
        0, 0, 0,
        room_total,
        room_total,
        random.choices(PAYMENT_MODES, weights=[0.35, 0.40, 0.25])[0],
        discharge_date
    ))
    bill_counter += 1

cur.executemany("INSERT INTO bills VALUES (?,?,?,?,?,?,?,?,?,?,?)", extra_bills)

conn.commit()

# ---------------------------------------------------------
# 10. SUMMARY
# ---------------------------------------------------------

print("Database 'hospital.db' created successfully.\n")
print(f"Patients        : {len(patients)}")
print(f"Doctors         : {len(doctors)}")
print(f"Appointments    : {len(appointments)}")
print(f"Bills           : {len(bills) + len(extra_bills)}")
print(f"Wards           : {len(wards)}")
print(f"Bed Allocations : {len(allocations)}")

conn.close()
