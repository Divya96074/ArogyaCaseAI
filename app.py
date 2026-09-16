from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os


# ============================================================
# FLASK APP
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

<<<<<<< HEAD
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")
=======
app.secret_key = "aarogya_caseai_secret_key"
>>>>>>> 7cd2fed (Initial commit)

DATABASE = os.path.join(BASE_DIR, "database.db")


# ============================================================
# DATABASE
# ============================================================

def get_db():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


def init_db():

    conn = get_db()

    # --------------------------------------------------------
    # PATIENTS TABLE
    # --------------------------------------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            patient_type TEXT,
            phone TEXT
        )
    """)

    # --------------------------------------------------------
    # CONVERSATIONS TABLE
    # --------------------------------------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            role TEXT,
            message TEXT
        )
    """)

    # --------------------------------------------------------
    # APPOINTMENTS TABLE
    # --------------------------------------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            consultation_type TEXT NOT NULL,
            queue_number INTEGER NOT NULL,
            waiting_time INTEGER NOT NULL,
            status TEXT DEFAULT 'Waiting'
        )
    """)

    conn.commit()

    conn.close()


# ============================================================
# HOME / LOGIN
# ============================================================
# ============================================================
# HOME / LOGIN
# ============================================================

@app.route("/")
def home():

    return render_template(
        "login.html"
    )


@app.route(
    "/login",
    methods=["POST"]
)
def login():

    username = request.form.get(
        "username",
        ""
    ).strip()

    password = request.form.get(
        "password",
        ""
    ).strip()

    role = request.form.get(
        "role",
        ""
    ).strip().lower()


    # ========================================================
    # DEMO USER ACCOUNTS
    # ========================================================

    users = {

        # -------------------------
        # DOCTOR ACCOUNTS
        # -------------------------

        "doctor": {
            "password": "1234",
            "role": "doctor",
            "name": "Dr. Demo"
        },

        "doctor2": {
            "password": "1234",
            "role": "doctor",
            "name": "Dr. Sharma"
        },

        "doctor3": {
            "password": "1234",
            "role": "doctor",
            "name": "Dr. Verma"
        },


        # -------------------------
        # PATIENT ACCOUNTS
        # -------------------------

        "patient": {
            "password": "1234",
            "role": "patient",
            "name": "Demo Patient"
        },

        "patient2": {
            "password": "1234",
            "role": "patient",
            "name": "Rahul Kumar"
        },

        "patient3": {
            "password": "1234",
            "role": "patient",
            "name": "Priya Sharma"
        }

    }


    # ========================================================
    # CHECK LOGIN
    # ========================================================

    if username in users:

        user = users[username]

        if (
            password == user["password"]
            and role == user["role"]
        ):

            # Clear previous session
            session.clear()

            # Save current user
            session["user"] = username

            session["role"] = user["role"]

            session["name"] = user["name"]


            # -------------------------
            # DOCTOR
            # -------------------------

            if user["role"] == "doctor":

                return redirect(
                    url_for("dashboard")
                )


            # -------------------------
            # PATIENT
            # -------------------------

            elif user["role"] == "patient":

                return redirect(
                    url_for("patient_portal")
                )


    # ========================================================
    # INVALID LOGIN
    # ========================================================

    return render_template(
        "login.html",
        error="Invalid username, password, or account type."
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("home")
    )


# ============================================================
# PATIENT PORTAL
# ============================================================

@app.route("/patient-portal")
def patient_portal():

    if "user" not in session:

        return redirect(
            url_for("home")
        )


    if session.get("role") != "patient":

        return redirect(
            url_for("dashboard")
        )


    return render_template(
        "patient_portal.html",
        name=session.get(
            "name",
            "Patient"
        ),
        username=session.get(
            "user"
        )
    )

# ============================================================
# DASHBOARD
# ============================================================
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("home"))

    conn = get_db()

    # -----------------------------------------
    # GET ALL PATIENTS
    # -----------------------------------------

    patients = conn.execute(
        "SELECT * FROM patients ORDER BY id DESC"
    ).fetchall()


    # -----------------------------------------
    # GET APPOINTMENTS
    # -----------------------------------------

    appointments = []

    try:

        appointment_rows = conn.execute(
            "SELECT * FROM appointments ORDER BY id ASC"
        ).fetchall()

        for row in appointment_rows:

            row_data = dict(row)

            patient_name = "Unknown Patient"


            # -----------------------------------------
            # TRY TO FIND PATIENT
            # -----------------------------------------

            patient_id = row_data.get("patient_id")

            patient = None


            # METHOD 1:
            # appointment contains patient's database ID

            if patient_id:

                try:
                    patient = conn.execute(
                        "SELECT * FROM patients WHERE id = ?",
                        (patient_id,)
                    ).fetchone()
                except Exception:
                    patient = None


            # METHOD 2:
            # appointment contains patient's patient_id
            # such as P001, P002 etc.

            if patient is None and patient_id:

                try:
                    patient = conn.execute(
                        "SELECT * FROM patients WHERE patient_id = ?",
                        (patient_id,)
                    ).fetchone()
                except Exception:
                    patient = None


            # METHOD 3:
            # appointment may already contain patient name

            if patient is not None:

                patient_name = patient["name"]

            elif row_data.get("patient_name"):

                patient_name = row_data["patient_name"]

            elif row_data.get("name"):

                patient_name = row_data["name"]


            # -----------------------------------------
            # APPOINTMENT DATE
            # -----------------------------------------

            appointment_date = (
                row_data.get("appointment_date")
                or row_data.get("date")
                or "Not specified"
            )


            # -----------------------------------------
            # APPOINTMENT TIME
            # -----------------------------------------

            appointment_time = (
                row_data.get("appointment_time")
                or row_data.get("time")
                or "Not specified"
            )


            # -----------------------------------------
            # CONSULTATION TYPE
            # -----------------------------------------

            consultation_type = (
                row_data.get("consultation_type")
                or row_data.get("type")
                or "General Consultation"
            )


            # -----------------------------------------
            # STATUS
            # -----------------------------------------

            status = (
                row_data.get("status")
                or "Waiting"
            )


            # -----------------------------------------
            # QUEUE NUMBER
            # -----------------------------------------

            queue_number = len(appointments) + 1


            # -----------------------------------------
            # ESTIMATED WAITING TIME
            # -----------------------------------------

            waiting_time = queue_number * 10


            # -----------------------------------------
            # SAVE APPOINTMENT
            # -----------------------------------------

            appointments.append({
                "queue_number": queue_number,
                "patient_name": patient_name,
                "appointment_date": appointment_date,
                "appointment_time": appointment_time,
                "consultation_type": consultation_type,
                "status": status,
                "waiting_time": waiting_time
            })


    except Exception:

        appointments = []


    # -----------------------------------------
    # COUNTS
    # -----------------------------------------

    appointment_count = len(appointments)

    waiting_count = 0

    for appointment in appointments:

        status = str(
            appointment["status"]
        ).lower()

        if status in [
            "waiting",
            "pending",
            "confirmed",
            "booked"
        ]:

            waiting_count += 1


    conn.close()


    # -----------------------------------------
    # DASHBOARD
    # -----------------------------------------

    return render_template(
        "dashboard.html",
        patients=patients,
        appointments=appointments,
        appointment_count=appointment_count,
        waiting_count=waiting_count
    )
    # -----------------------------------------
    # GET ALL PATIENTS
    # -----------------------------------------

    patients = conn.execute(
        "SELECT * FROM patients ORDER BY id DESC"
    ).fetchall()


    # -----------------------------------------
    # GET APPOINTMENTS
    # -----------------------------------------

    appointments = []

    try:

        appointment_rows = conn.execute(
            "SELECT * FROM appointments ORDER BY id ASC"
        ).fetchall()

        for row in appointment_rows:

            row_data = dict(row)

            # Find patient name
            patient_name = "Unknown Patient"

            patient_id = (
                row_data.get("patient_id")
                or row_data.get("patient")
            )

            if patient_id:

                patient = conn.execute(
                    "SELECT name FROM patients WHERE id = ?",
                    (patient_id,)
                ).fetchone()

                if patient:
                    patient_name = patient["name"]


            # Find date
            appointment_date = (
                row_data.get("appointment_date")
                or row_data.get("date")
                or "Not specified"
            )


            # Find time
            appointment_time = (
                row_data.get("appointment_time")
                or row_data.get("time")
                or "Not specified"
            )


            # Find consultation type
            consultation_type = (
                row_data.get("consultation_type")
                or row_data.get("type")
                or "General Consultation"
            )


            # Find status
            status = (
                row_data.get("status")
                or "Waiting"
            )


            # Calculate queue number
            queue_number = len(appointments) + 1


            # Estimated waiting time
            waiting_time = queue_number * 10


            appointments.append({
                "queue_number": queue_number,
                "patient_name": patient_name,
                "appointment_date": appointment_date,
                "appointment_time": appointment_time,
                "consultation_type": consultation_type,
                "status": status,
                "waiting_time": waiting_time
            })


    except Exception:

        # If the appointments table does not exist,
        # keep the dashboard working normally.
        appointments = []


    # -----------------------------------------
    # APPOINTMENT COUNT
    # -----------------------------------------

    appointment_count = len(appointments)


    # -----------------------------------------
    # WAITING QUEUE COUNT
    # -----------------------------------------

    waiting_count = 0

    for appointment in appointments:

        status = str(
            appointment["status"]
        ).lower()

        if status in [
            "waiting",
            "pending",
            "confirmed",
            "booked"
        ]:

            waiting_count += 1


    conn.close()


    # -----------------------------------------
    # LOAD DASHBOARD
    # -----------------------------------------

    return render_template(
        "dashboard.html",
        patients=patients,
        appointments=appointments,
        appointment_count=appointment_count,
        waiting_count=waiting_count
    )
# ============================================================
# PATIENT REGISTRATION
# ============================================================

@app.route(
    "/patient-registration",
    methods=["GET", "POST"]
)
def patient_registration():

    if "user" not in session:

        return redirect(url_for("home"))

    if request.method == "POST":

        name = request.form.get("name")

        age = request.form.get("age")

        gender = request.form.get("gender")

        patient_type = request.form.get("patient_type")

        phone = request.form.get("phone")

        conn = get_db()

        # ----------------------------------------------------
        # Generate Patient ID
        # ----------------------------------------------------

        last_patient = conn.execute("""
            SELECT patient_id
            FROM patients
            WHERE patient_id IS NOT NULL
            ORDER BY id DESC
            LIMIT 1
        """).fetchone()

        patient_number = 1

        if last_patient:

            old_id = last_patient["patient_id"]

            try:

                patient_number = (
                    int(old_id.split("-")[-1]) + 1
                )

            except:

                patient_number = 1

        new_patient_id = (
            f"AYU-{patient_number:05d}"
        )

        # ----------------------------------------------------
        # Insert Patient
        # ----------------------------------------------------

        cursor = conn.execute("""
            INSERT INTO patients
            (
                patient_id,
                name,
                age,
                gender,
                patient_type,
                phone
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            new_patient_id,
            name,
            age,
            gender,
            patient_type,
            phone
        ))

        database_id = cursor.lastrowid

        conn.commit()

        conn.close()

        return redirect(
            url_for(
                "case_taking",
                patient_id=database_id
            )
        )

    return render_template(
        "patient_registration.html"
    )


# ============================================================
# CASE TAKING
# ============================================================

@app.route("/case-taking/<int:patient_id>")
def case_taking(patient_id):

    if "user" not in session:

        return redirect(url_for("home"))

    conn = get_db()

    patient = conn.execute(
        """
        SELECT *
        FROM patients
        WHERE id = ?
        """,
        (patient_id,)
    ).fetchone()

    conversations = conn.execute(
        """
        SELECT *
        FROM conversations
        WHERE patient_id = ?
        ORDER BY id
        """,
        (patient_id,)
    ).fetchall()

    conn.close()

    if not patient:

        return "Patient not found"

    red_flags = []

    for message in conversations:

        if message["role"] == "red_flag":

            red_flags.append(
                message["message"]
            )

    return render_template(
        "case_taking.html",
        patient=patient,
        conversations=conversations,
        messages=conversations,
        red_flags=red_flags
    )


# ============================================================
# ADAPTIVE QUESTIONING
# ============================================================

@app.route(
    "/case-taking/<int:patient_id>/message",
    methods=["POST"]
)
def case_taking_message(patient_id):

    if "user" not in session:

        return redirect(url_for("home"))

    message = request.form.get(
        "message",
        ""
    ).strip()

    if not message:

        return redirect(
            url_for(
                "case_taking",
                patient_id=patient_id
            )
        )

    conn = get_db()

    patient = conn.execute(
        """
        SELECT *
        FROM patients
        WHERE id = ?
        """,
        (patient_id,)
    ).fetchone()

    if not patient:

        conn.close()

        return "Patient not found"

    # --------------------------------------------------------
    # Save Patient Response
    # --------------------------------------------------------

    conn.execute(
        """
        INSERT INTO conversations
        (
            patient_id,
            role,
            message
        )
        VALUES (?, ?, ?)
        """,
        (
            patient_id,
            "patient",
            message
        )
    )

    # --------------------------------------------------------
    # RED FLAG DETECTION
    # --------------------------------------------------------

    lower_message = message.lower()

    red_flag_keywords = [

        "difficulty breathing",

        "trouble breathing",

        "can't breathe",

        "cannot breathe",

        "chest pain",

        "unconscious",

        "unresponsive",

        "seizure",

        "convulsion",

        "severe bleeding",

        "heavy bleeding"

    ]

    detected_flag = None

    for keyword in red_flag_keywords:

        if keyword in lower_message:

            detected_flag = keyword

            break

    if detected_flag:

        warning = (
            "⚠️ RED FLAG DETECTED: "
            + detected_flag
            + ". Immediate medical attention is recommended."
        )

        conn.execute(
            """
            INSERT INTO conversations
            (
                patient_id,
                role,
                message
            )
            VALUES (?, ?, ?)
            """,
            (
                patient_id,
                "red_flag",
                warning
            )
        )

        conn.execute(
            """
            INSERT INTO conversations
            (
                patient_id,
                role,
                message
            )
            VALUES (?, ?, ?)
            """,
            (
                patient_id,
                "assistant",
                "Please inform the doctor immediately."
            )
        )

        conn.commit()

        conn.close()

        return redirect(
            url_for(
                "case_taking",
                patient_id=patient_id
            )
        )

    # --------------------------------------------------------
    # COUNT PATIENT RESPONSES
    # --------------------------------------------------------

    patient_messages = conn.execute(
        """
        SELECT *
        FROM conversations
        WHERE patient_id = ?
        AND role = 'patient'
        ORDER BY id
        """,
        (patient_id,)
    ).fetchall()

    count = len(patient_messages)

    # ========================================================
    # PEDIATRIC / TODDLER
    # ========================================================

    if patient["patient_type"] in [
        "Pediatric",
        "Toddler"
    ]:

        if count == 1:

            question = (
                "How long has the problem been present, "
                "and what was the highest temperature "
                "if there is fever?"
            )

        elif count == 2:

            question = (
                "How is the child's appetite, sleep, "
                "activity level, or behaviour compared "
                "with normal?"
            )

        elif count == 3:

            question = (
                "Are the child's vaccinations up to date? "
                "Does the child have any known allergies "
                "or medical conditions?"
            )

        elif count == 4:

            question = (
                "Is the child currently taking any medicines, "
                "supplements, or other treatments?"
            )

        else:

            question = (
                "Thank you. The pediatric case history "
                "is now ready for doctor review."
            )

    # ========================================================
    # ADULT
    # ========================================================

    else:

        if count == 1:

            question = (
                "How long have you been experiencing "
                "this problem?"
            )

        elif count == 2:

            question = (
                "Are you experiencing any other symptoms "
                "along with this problem?"
            )

        elif count == 3:

            question = (
                "Do you have any previous medical conditions, "
                "allergies, or significant medical history?"
            )

        elif count == 4:

            question = (
                "Are you currently taking any medicines "
                "or supplements?"
            )

        else:

            question = (
                "Thank you. Your case history is now ready "
                "for doctor review."
            )

    # --------------------------------------------------------
    # Save AI Question
    # --------------------------------------------------------

    conn.execute(
        """
        INSERT INTO conversations
        (
            patient_id,
            role,
            message
        )
        VALUES (?, ?, ?)
        """,
        (
            patient_id,
            "assistant",
            question
        )
    )

    conn.commit()

    conn.close()

    return redirect(
        url_for(
            "case_taking",
            patient_id=patient_id
        )
    )


# ============================================================
# DOCTOR SUMMARY
# ============================================================

@app.route("/doctor-summary/<int:patient_id>")
def doctor_summary(patient_id):

    if "user" not in session:

        return redirect(url_for("home"))

    conn = get_db()

    patient = conn.execute(
        """
        SELECT *
        FROM patients
        WHERE id = ?
        """,
        (patient_id,)
    ).fetchone()

    conversations = conn.execute(
        """
        SELECT *
        FROM conversations
        WHERE patient_id = ?
        ORDER BY id
        """,
        (patient_id,)
    ).fetchall()

    conn.close()

    if not patient:

        return "Patient not found"

    patient_messages = [

        c["message"]

        for c in conversations

        if c["role"] == "patient"

    ]

    red_flags = [

        c["message"]

        for c in conversations

        if c["role"] == "red_flag"

    ]

    chief_complaint = (

        patient_messages[0]

        if len(patient_messages) > 0

        else "Not provided"

    )

    duration = (

        patient_messages[1]

        if len(patient_messages) > 1

        else "Not provided"

    )

    associated_symptoms = (

        patient_messages[2]

        if len(patient_messages) > 2

        else "Not provided"

    )

    medical_history = (

        patient_messages[3]

        if len(patient_messages) > 3

        else "Not provided"

    )

    medicines = (

        patient_messages[4]

        if len(patient_messages) > 4

        else "Not provided"

    )

    return render_template(
        "doctor_summary.html",
        patient=patient,
        chief_complaint=chief_complaint,
        duration=duration,
        associated_symptoms=associated_symptoms,
        medical_history=medical_history,
        medicines=medicines,
        red_flags=red_flags
    )


# ============================================================
# MEDICAL DOCUMENT EXTRACTION
# ============================================================

@app.route(
    "/document-extraction",
    methods=["GET", "POST"]
)
def document_extraction():

    extracted_text = None

    if request.method == "POST":

        document = request.files.get(
            "document"
        )

        if document and document.filename:

            filename = document.filename.lower()

            # ------------------------------------------------
            # TXT
            # ------------------------------------------------

            if filename.endswith(".txt"):

                try:

                    extracted_text = (
                        document.read()
                        .decode(
                            "utf-8",
                            errors="ignore"
                        )
                    )

                except Exception:

                    extracted_text = (
                        "Unable to read the text document."
                    )

            # ------------------------------------------------
            # PDF
            # ------------------------------------------------

            elif filename.endswith(".pdf"):

                try:

                    import PyPDF2

                    reader = PyPDF2.PdfReader(
                        document
                    )

                    pages = []

                    for page in reader.pages:

                        text = page.extract_text()

                        if text:

                            pages.append(text)

                    extracted_text = "\n\n".join(
                        pages
                    )

                    if not extracted_text.strip():

                        extracted_text = (
                            "The PDF was uploaded successfully, "
                            "but no readable text was found."
                        )

                except ImportError:

                    extracted_text = (
                        "PDF reader is not installed. "
                        "Run: pip install PyPDF2"
                    )

                except Exception as e:

                    extracted_text = (
                        "Unable to extract text from this PDF.\n\n"
                        + str(e)
                    )

            else:

                extracted_text = (
                    "Unsupported file format. "
                    "Please upload a PDF or TXT file."
                )

    return render_template(
        "document_extraction.html",
        extracted_text=extracted_text
    )


# ============================================================
# MEDICINE AVAILABILITY
# ============================================================

# ============================================================
# MEDICINE AVAILABILITY
# ============================================================
# ============================================================
# MEDICINE AVAILABILITY
# ============================================================

@app.route(
    "/medicine-availability",
    methods=["GET", "POST"]
)
def medicine_availability():

    medicine = None
    searched = False
    search_term = ""

    # --------------------------------------------------------
    # DEMO CLINIC MEDICINE INVENTORY
    # Ayurvedic + Allopathic + OTC Medicines
    # --------------------------------------------------------

    medicines = [

        # =========================
        # AYURVEDIC MEDICINES
        # =========================

        {
            "name": "Ashwagandha",
            "category": "Ayurvedic Medicine",
            "available": True,
            "quantity": 25,
            "location": "Ayurvedic Pharmacy - Counter 1"
        },

        {
            "name": "Triphala",
            "category": "Ayurvedic Medicine",
            "available": True,
            "quantity": 18,
            "location": "Ayurvedic Pharmacy - Counter 1"
        },

        {
            "name": "Giloy",
            "category": "Ayurvedic Medicine",
            "available": True,
            "quantity": 12,
            "location": "Ayurvedic Pharmacy - Counter 2"
        },

        {
            "name": "Brahmi",
            "category": "Ayurvedic Medicine",
            "available": True,
            "quantity": 15,
            "location": "Ayurvedic Pharmacy - Counter 2"
        },

        {
            "name": "Chyawanprash",
            "category": "Ayurvedic Supplement",
            "available": True,
            "quantity": 30,
            "location": "Ayurvedic Pharmacy - Counter 2"
        },

        {
            "name": "Tulsi",
            "category": "Ayurvedic Medicine",
            "available": True,
            "quantity": 20,
            "location": "Ayurvedic Pharmacy - Counter 1"
        },

        {
            "name": "Neem",
            "category": "Ayurvedic Medicine",
            "available": True,
            "quantity": 14,
            "location": "Ayurvedic Pharmacy - Counter 1"
        },

        {
            "name": "Turmeric",
            "category": "Ayurvedic Medicine",
            "available": True,
            "quantity": 22,
            "location": "Ayurvedic Pharmacy - Counter 2"
        },

        {
            "name": "Arjuna",
            "category": "Ayurvedic Medicine",
            "available": False,
            "quantity": 0,
            "location": "Currently unavailable"
        },

        {
            "name": "Amla",
            "category": "Ayurvedic Medicine",
            "available": True,
            "quantity": 17,
            "location": "Ayurvedic Pharmacy - Counter 1"
        },


        # =========================
        # COMMON OTC MEDICINES
        # =========================

        {
            "name": "Paracetamol",
            "category": "Allopathic / OTC",
            "available": True,
            "quantity": 50,
            "location": "General Pharmacy - Counter 1"
        },

        {
            "name": "Ibuprofen",
            "category": "Allopathic / OTC",
            "available": True,
            "quantity": 35,
            "location": "General Pharmacy - Counter 1"
        },

        {
            "name": "Cetirizine",
            "category": "Allopathic / OTC",
            "available": True,
            "quantity": 40,
            "location": "General Pharmacy - Counter 1"
        },

        {
            "name": "ORS",
            "category": "Oral Rehydration",
            "available": True,
            "quantity": 60,
            "location": "General Pharmacy - Counter 1"
        },

        {
            "name": "Antacid",
            "category": "Allopathic / OTC",
            "available": True,
            "quantity": 30,
            "location": "General Pharmacy - Counter 1"
        },

        {
            "name": "Calcium",
            "category": "Supplement",
            "available": True,
            "quantity": 25,
            "location": "General Pharmacy - Counter 2"
        },

        {
            "name": "Vitamin C",
            "category": "Vitamin Supplement",
            "available": True,
            "quantity": 32,
            "location": "General Pharmacy - Counter 2"
        },

        {
            "name": "Vitamin D3",
            "category": "Vitamin Supplement",
            "available": True,
            "quantity": 28,
            "location": "General Pharmacy - Counter 2"
        },


        # =========================
        # COMMON PRESCRIPTION MEDICINES
        # =========================

        {
            "name": "Omeprazole",
            "category": "Gastrointestinal Medicine",
            "available": True,
            "quantity": 24,
            "location": "General Pharmacy - Counter 2"
        },

        {
            "name": "Pantoprazole",
            "category": "Gastrointestinal Medicine",
            "available": True,
            "quantity": 20,
            "location": "General Pharmacy - Counter 2"
        },

        {
            "name": "Metformin",
            "category": "Diabetes Medicine",
            "available": True,
            "quantity": 18,
            "location": "General Pharmacy - Counter 3"
        },

        {
            "name": "Amlodipine",
            "category": "Blood Pressure Medicine",
            "available": True,
            "quantity": 16,
            "location": "General Pharmacy - Counter 3"
        },

        {
            "name": "Atorvastatin",
            "category": "Cholesterol Medicine",
            "available": True,
            "quantity": 14,
            "location": "General Pharmacy - Counter 3"
        },

        {
            "name": "Levothyroxine",
            "category": "Thyroid Medicine",
            "available": True,
            "quantity": 12,
            "location": "General Pharmacy - Counter 3"
        },

        {
            "name": "Amoxicillin",
            "category": "Antibiotic",
            "available": True,
            "quantity": 10,
            "location": "General Pharmacy - Counter 3"
        },

        {
            "name": "Azithromycin",
            "category": "Antibiotic",
            "available": True,
            "quantity": 8,
            "location": "General Pharmacy - Counter 3"
        },

        {
            "name": "Diclofenac",
            "category": "Pain Relief Medicine",
            "available": True,
            "quantity": 15,
            "location": "General Pharmacy - Counter 1"
        },

        {
            "name": "Montelukast",
            "category": "Allergy / Respiratory Medicine",
            "available": True,
            "quantity": 13,
            "location": "General Pharmacy - Counter 2"
        },

        {
            "name": "Salbutamol",
            "category": "Respiratory Medicine",
            "available": True,
            "quantity": 9,
            "location": "General Pharmacy - Counter 2"
        },

        {
            "name": "Loratadine",
            "category": "Anti-Allergy Medicine",
            "available": True,
            "quantity": 21,
            "location": "General Pharmacy - Counter 1"
        },

        {
            "name": "Domperidone",
            "category": "Gastrointestinal Medicine",
            "available": False,
            "quantity": 0,
            "location": "Currently unavailable"
        },

        {
            "name": "Ondansetron",
            "category": "Anti-Nausea Medicine",
            "available": True,
            "quantity": 11,
            "location": "General Pharmacy - Counter 2"
        }

    ]


    # --------------------------------------------------------
    # SEARCH MEDICINE
    # --------------------------------------------------------

    if request.method == "POST":

        searched = True

        search_term = request.form.get(
            "medicine_name",
            ""
        ).strip()


        # Exact or partial case-insensitive search
        for item in medicines:

            if search_term.lower() in item["name"].lower():

                medicine = item

                break


    # --------------------------------------------------------
    # DISPLAY PAGE
    # --------------------------------------------------------

    return render_template(
        "medicine_availability.html",
        medicine=medicine,
        searched=searched,
        search_term=search_term
    )

# ============================================================
# APPOINTMENT & QUEUE
# ============================================================

@app.route(
    "/appointment",
    methods=["GET", "POST"]
)
def appointment():

    conn = get_db()

    appointment_data = None

    if request.method == "POST":

        patient_name = request.form.get(
            "patient_name"
        )

        appointment_date = request.form.get(
            "appointment_date"
        )

        appointment_time = request.form.get(
            "appointment_time"
        )

        consultation_type = request.form.get(
            "consultation_type"
        )

        # ----------------------------------------------------
        # Queue Number
        # ----------------------------------------------------

        queue_number = conn.execute(
            """
            SELECT COUNT(*)
            FROM appointments
            WHERE appointment_date = ?
            """,
            (appointment_date,)
        ).fetchone()[0] + 1

        # ----------------------------------------------------
        # Waiting Time
        # ----------------------------------------------------

        waiting_time = (
            queue_number - 1
        ) * 15

        # ----------------------------------------------------
        # Save Appointment
        # ----------------------------------------------------

        conn.execute(
            """
            INSERT INTO appointments
            (
                patient_name,
                appointment_date,
                appointment_time,
                consultation_type,
                queue_number,
                waiting_time,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                patient_name,
                appointment_date,
                appointment_time,
                consultation_type,
                queue_number,
                waiting_time,
                "Waiting"
            )
        )

        conn.commit()

        appointment_data = {

            "patient_name": patient_name,

            "appointment_date":
                appointment_date,

            "appointment_time":
                appointment_time,

            "consultation_type":
                consultation_type,

            "queue_number":
                queue_number,

            "waiting_time":
                waiting_time

        }

    conn.close()

    return render_template(
        "appointment.html",
        patient=None,
        appointment=appointment_data
    )


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    init_db()

    app.run(
        debug=True
    )