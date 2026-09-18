import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

app.secret_key = os.environ.get("SECRET_KEY", "aarogya_caseai_secret_key")
DATABASE = os.path.join(BASE_DIR, "database.db")


# ============================================================
# MULTILINGUAL DICTIONARY
# ============================================================

TRANSLATIONS = {
    "en": {
        "welcome": "Hello! I am AarogyaCase AI. I will ask you a few questions to understand your health concern.",
        "initial_q": "What brings you to the clinic today?",
        "adult_q1": "How long have you been experiencing this problem?",
        "adult_q2": "Are you experiencing any other symptoms along with this problem?",
        "adult_q3": "Do you have any previous medical conditions, allergies, or significant medical history?",
        "adult_q4": "Are you currently taking any medicines or supplements?",
        "adult_done": "Thank you. Your case history is now ready for doctor review.",
        "pedia_q1": "How long has the problem been present, and what was the highest temperature if there is fever?",
        "pedia_q2": "How is the child's appetite, sleep, activity level, or behaviour compared with normal?",
        "pedia_q3": "Are the child's vaccinations up to date? Does the child have any known allergies or medical conditions?",
        "pedia_q4": "Is the child currently taking any medicines, supplements, or other treatments?",
        "pedia_done": "Thank you. The pediatric case history is now ready for doctor review.",
        "red_flag_alert": "⚠️ RED FLAG DETECTED: {flag}. Immediate medical attention is recommended.",
        "doctor_notify": "Please inform the doctor immediately."
    },
    "hi": {
        "welcome": "नमस्ते! मैं आरोग्यकेस एआई हूँ। आपकी स्वास्थ्य समस्या को समझने के लिए मैं आपसे कुछ सवाल पूछूँगा।",
        "initial_q": "आज आप क्लिनिक में किस समस्या के लिए आए हैं?",
        "adult_q1": "आप इस समस्या का सामना कितने समय से कर रहे हैं?",
        "adult_q2": "क्या आपको इस समस्या के साथ कोई अन्य लक्षण भी महसूस हो रहे हैं?",
        "adult_q3": "क्या आपकी कोई पुरानी बीमारी, एलर्जी या कोई अन्य मेडिकल हिस्ट्री है?",
        "adult_q4": "क्या आप वर्तमान में कोई दवाइयां या सप्लीमेंट्स ले रहे हैं?",
        "adult_done": "धन्यवाद। आपका केस विवरण डॉक्टर की समीक्षा के लिए तैयार है।",
        "pedia_q1": "बच्चे को यह समस्या कितने समय से है, और यदि बुखार है तो अधिकतम तापमान कितना था?",
        "pedia_q2": "सामान्य दिनों की तुलना में बच्चे की भूख, नींद, गतिविधि या व्यवहार में क्या बदलाव है?",
        "pedia_q3": "क्या बच्चे के सभी टीके लग चुके हैं? क्या कोई एलर्जी या पुरानी बीमारी है?",
        "pedia_q4": "क्या बच्चा वर्तमान में कोई दवाई या सप्लीमेंट ले रहा है?",
        "pedia_done": "धन्यवाद। बच्चे का केस विवरण डॉक्टर की समीक्षा के लिए तैयार है।",
        "red_flag_alert": "⚠️ आपातकालीन चेतावनी: {flag}। तुरंत डॉक्टर से संपर्क करने की सलाह दी जाती है।",
        "doctor_notify": "कृपया तुरंत डॉक्टर को सूचित करें।"
    },
    "bn": {
        "welcome": "নমস্কার! আমি আরোগ্যকেস এআই। আপনার স্বাস্থ্য সমস্যা বোঝার জন্য আপনাকে কিছু প্রশ্ন জিজ্ঞাসা করব।",
        "initial_q": "আজ আপনি কী সমস্যার জন্য ক্লিনিকে এসেছেন?",
        "adult_q1": "আপনি কত দিন ধরে এই সমস্যা অনুভব করছেন?",
        "adult_q2": "এই সমস্যার সাথে আপনার কি অন্য কোনো লক্ষণ দেখা যাচ্ছে?",
        "adult_q3": "আপনার কি আগে থেকে কোনো রোগ, অ্যালার্জি বা উল্লেখযোগ্য চিকিৎসার ইতিহাস আছে?",
        "adult_q4": "আপনি কি বর্তমানে কোনো ওষুধ বা সাপ্লিমেন্ট নিচ্ছেন?",
        "adult_done": "ধন্যবাদ। আপনার কেস হিস্ট্রি ডাক্তারের পর্যালোচনার জন্য প্রস্তুত।",
        "pedia_q1": "শিশুর এই সমস্যা কত দিন ধরে এবং জ্বর থাকলে সর্বোচ্চ তাপমাত্রা কত ছিল?",
        "pedia_q2": "স্বাভাবিকের তুলনায় শিশুর ক্ষুধা, ঘুম, খেলাধূলা বা আচরণে কোনো পরিবর্তন আছে কি?",
        "pedia_q3": "শিশুর সব টিকা কি দেওয়া হয়েছে? কোনো জানা অ্যালার্জি বা শারীরিক সমস্যা আছে কি?",
        "pedia_q4": "শিশু কি বর্তমানে কোনো ওষুধ বা চিকিৎসার মধ্যে রয়েছে?",
        "pedia_done": "ধন্যবাদ। শিশুর কেস বিবরণ ডাক্তারের পর্যালোচনার জন্য প্রস্তুত।",
        "red_flag_alert": "⚠️ জরুরি সতর্কতা: {flag}। অবিলম্বে ডাক্তারের সাথে যোগাযোগ করার পরামর্শ দেওয়া হচ্ছে।",
        "doctor_notify": "অনুগ্রহ করে সাথে সাথে ডাক্তারকে জানান।"
    }
}

RED_FLAGS = {
    "difficulty breathing": "Difficulty Breathing / শ্বাসকষ্ট / सांस लेने में तकलीफ",
    "trouble breathing": "Trouble Breathing / सांस लेने में कठिनाई",
    "can't breathe": "Cannot Breathe",
    "cannot breathe": "Cannot Breathe",
    "chest pain": "Chest Pain / বুকে ব্যথা / सीने में दर्द",
    "unconscious": "Loss of Consciousness / बेहोशी / অজ্ঞান",
    "unresponsive": "Unresponsive State",
    "seizure": "Seizure / दौरा / খিঁচুনি",
    "convulsion": "Convulsion",
    "severe bleeding": "Severe Bleeding / अत्यधिक रक्तस्राव / অতিরিক্ত রক্তক্ষরণ",
    "heavy bleeding": "Heavy Bleeding",
    "सांस लेने में दिक्कत": "Difficulty Breathing",
    "सीने में दर्द": "Chest Pain",
    "बेहोश": "Loss of Consciousness",
    "खून": "Bleeding",
    "শ্বাসকষ্ট": "Difficulty Breathing",
    "বুকে ব্যথা": "Chest Pain"
}


# ============================================================
# DATABASE SETUP
# ============================================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT UNIQUE,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            patient_type TEXT,
            phone TEXT,
            preferred_lang TEXT DEFAULT 'en'
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            role TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
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
    cursor = conn.execute("PRAGMA table_info(patients)")
    columns = [col[1] for col in cursor.fetchall()]
    if "preferred_lang" not in columns:
        conn.execute("ALTER TABLE patients ADD COLUMN preferred_lang TEXT DEFAULT 'en'")

    conn.commit()
    conn.close()


# ============================================================
# AUTHENTICATION ACCOUNTS
# ============================================================

USERS = {
    "doctor": {"password": "1234", "role": "doctor", "name": "Dr. Sharma"},
    "doctor2": {"password": "1234", "role": "doctor", "name": "Dr. Verma"},
    "patient": {"password": "1234", "role": "patient", "name": "AYU-00001"},
    "patient2": {"password": "1234", "role": "patient", "name": "AYU-00002"}
}


@app.route("/")
def home():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    role = request.form.get("role", "").strip().lower()

    user = USERS.get(username)
    if user and password == user["password"] and role == user["role"]:
        session.clear()
        session["user"] = username
        session["role"] = user["role"]
        session["name"] = user["name"]

        if user["role"] == "doctor":
            return redirect(url_for("dashboard"))
        elif user["role"] == "patient":
            return redirect(url_for("patient_portal"))

    return render_template("login.html", error="Invalid username, password, or account type.")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# ============================================================
# DASHBOARD & PORTAL
# ============================================================

@app.route("/patient-portal")
def patient_portal():
    if "user" not in session:
        return redirect(url_for("home"))
    if session.get("role") != "patient":
        return redirect(url_for("dashboard"))

    return render_template(
        "patient_portal.html",
        name=session.get("name", "AYU-00001"),
        username=session.get("user")
    )


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("home"))

    conn = get_db()
    patients = conn.execute("SELECT * FROM patients ORDER BY id DESC").fetchall()

    appointments = []
    try:
        rows = conn.execute("SELECT * FROM appointments ORDER BY id ASC").fetchall()
        for idx, row in enumerate(rows):
            r = dict(row)
            queue_no = idx + 1
            appointments.append({
                "queue_number": queue_no,
                "patient_name": r.get("patient_name") or "Unknown Patient",
                "appointment_date": r.get("appointment_date", "Not specified"),
                "appointment_time": r.get("appointment_time", "Not specified"),
                "consultation_type": r.get("consultation_type", "General Consultation"),
                "status": r.get("status", "Waiting"),
                "waiting_time": queue_no * 10
            })
    except sqlite3.OperationalError:
        appointments = []

    waiting_count = sum(
        1 for a in appointments
        if str(a["status"]).lower() in ["waiting", "pending", "confirmed", "booked"]
    )
    conn.close()

    return render_template(
        "dashboard.html",
        patients=patients,
        appointments=appointments,
        appointment_count=len(appointments),
        waiting_count=waiting_count
    )


# ============================================================
# PATIENT REGISTRATION & CASE TAKING
# ============================================================

@app.route("/patient-registration", methods=["GET", "POST"])
def patient_registration():
    if "user" not in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        name = request.form.get("name")
        age = request.form.get("age")
        gender = request.form.get("gender")
        patient_type = request.form.get("patient_type")
        phone = request.form.get("phone")
        preferred_lang = request.form.get("preferred_lang", "en")

        conn = get_db()
        last_patient = conn.execute(
            "SELECT patient_id FROM patients WHERE patient_id IS NOT NULL ORDER BY id DESC LIMIT 1"
        ).fetchone()

        patient_num = 1
        if last_patient and last_patient["patient_id"]:
            try:
                patient_num = int(last_patient["patient_id"].split("-")[-1]) + 1
            except (ValueError, IndexError):
                patient_num = 1

        new_pid = f"AYU-{patient_num:05d}"
        cursor = conn.execute("""
            INSERT INTO patients (patient_id, name, age, gender, patient_type, phone, preferred_lang)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (new_pid, name, age, gender, patient_type, phone, preferred_lang))

        new_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return redirect(url_for("case_taking", patient_id=new_id))

    return render_template("patient_registration.html")


@app.route("/case-taking/<int:patient_id>")
def case_taking(patient_id):
    if "user" not in session:
        return redirect(url_for("home"))

    conn = get_db()
    patient = conn.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
    conversations = conn.execute(
        "SELECT * FROM conversations WHERE patient_id = ? ORDER BY id", (patient_id,)
    ).fetchall()
    conn.close()

    if not patient:
        return "Patient not found", 404

    lang = patient["preferred_lang"] if patient["preferred_lang"] in TRANSLATIONS else "en"
    i18n = TRANSLATIONS[lang]
    red_flags = [c["message"] for c in conversations if c["role"] == "red_flag"]

    return render_template(
        "case_taking.html",
        patient=patient,
        messages=conversations,
        red_flags=red_flags,
        lang=lang,
        i18n=i18n
    )


@app.route("/case-taking/<int:patient_id>/set-language", methods=["POST"])
def set_patient_language(patient_id):
    lang = request.form.get("language", "en")
    conn = get_db()
    conn.execute("UPDATE patients SET preferred_lang = ? WHERE id = ?", (lang, patient_id))
    conn.commit()
    conn.close()
    return redirect(url_for("case_taking", patient_id=patient_id))


@app.route("/case-taking/<int:patient_id>/message", methods=["POST"])
def case_taking_message(patient_id):
    if "user" not in session:
        return redirect(url_for("home"))

    message = request.form.get("message", "").strip()
    if not message:
        return redirect(url_for("case_taking", patient_id=patient_id))

    conn = get_db()
    patient = conn.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
    if not patient:
        conn.close()
        return "Patient not found", 404

    lang = patient["preferred_lang"] if patient["preferred_lang"] in TRANSLATIONS else "en"
    i18n = TRANSLATIONS[lang]

    conn.execute(
        "INSERT INTO conversations (patient_id, role, message) VALUES (?, 'patient', ?)",
        (patient_id, message)
    )

    lower_msg = message.lower()
    detected_flag = None
    for keyword, label in RED_FLAGS.items():
        if keyword in lower_msg:
            detected_flag = label
            break

    if detected_flag:
        alert_text = i18n["red_flag_alert"].format(flag=detected_flag)
        conn.execute(
            "INSERT INTO conversations (patient_id, role, message) VALUES (?, 'red_flag', ?)",
            (patient_id, alert_text)
        )
        conn.execute(
            "INSERT INTO conversations (patient_id, role, message) VALUES (?, 'assistant', ?)",
            (patient_id, i18n["doctor_notify"])
        )
        conn.commit()
        conn.close()
        return redirect(url_for("case_taking", patient_id=patient_id))

    patient_responses = conn.execute(
        "SELECT * FROM conversations WHERE patient_id = ? AND role = 'patient'", (patient_id,)
    ).fetchall()
    count = len(patient_responses)

    if patient["patient_type"] in ["Pediatric", "Toddler"]:
        q_map = {
            1: i18n["pedia_q1"],
            2: i18n["pedia_q2"],
            3: i18n["pedia_q3"],
            4: i18n["pedia_q4"]
        }
        next_q = q_map.get(count, i18n["pedia_done"])
    else:
        q_map = {
            1: i18n["adult_q1"],
            2: i18n["adult_q2"],
            3: i18n["adult_q3"],
            4: i18n["adult_q4"]
        }
        next_q = q_map.get(count, i18n["adult_done"])

    conn.execute(
        "INSERT INTO conversations (patient_id, role, message) VALUES (?, 'assistant', ?)",
        (patient_id, next_q)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("case_taking", patient_id=patient_id))


@app.route("/doctor-summary/<int:patient_id>")
def doctor_summary(patient_id):
    if "user" not in session:
        return redirect(url_for("home"))

    conn = get_db()
    patient = conn.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
    conversations = conn.execute(
        "SELECT * FROM conversations WHERE patient_id = ? ORDER BY id", (patient_id,)
    ).fetchall()
    conn.close()

    if not patient:
        return "Patient not found", 404

    patient_messages = [c["message"] for c in conversations if c["role"] == "patient"]
    red_flags = [c["message"] for c in conversations if c["role"] == "red_flag"]

    def get_ans(idx):
        return patient_messages[idx] if len(patient_messages) > idx else "Not provided"

    return render_template(
        "doctor_summary.html",
        patient=patient,
        chief_complaint=get_ans(0),
        duration=get_ans(1),
        associated_symptoms=get_ans(2),
        medical_history=get_ans(3),
        medicines=get_ans(4),
        red_flags=red_flags
    )


# ============================================================
# CLINIC UTILITIES & APPOINTMENTS
# ============================================================

@app.route("/medicine-availability", methods=["GET", "POST"])
def medicine_availability():
    medicine = None
    searched = False
    search_term = ""

    inventory = [
        {"name": "Ashwagandha", "category": "Ayurvedic Medicine", "available": True, "quantity": 25, "location": "Ayurvedic Pharmacy - Counter 1"},
        {"name": "Triphala", "category": "Ayurvedic Medicine", "available": True, "quantity": 18, "location": "Ayurvedic Pharmacy - Counter 1"},
        {"name": "Giloy", "category": "Ayurvedic Medicine", "available": True, "quantity": 12, "location": "Ayurvedic Pharmacy - Counter 2"},
        {"name": "Tulsi", "category": "Ayurvedic Medicine", "available": True, "quantity": 20, "location": "Ayurvedic Pharmacy - Counter 1"},
        {"name": "Paracetamol", "category": "Allopathic / OTC", "available": True, "quantity": 50, "location": "General Pharmacy - Counter 1"},
        {"name": "Cetirizine", "category": "Allopathic / OTC", "available": True, "quantity": 40, "location": "General Pharmacy - Counter 1"},
        {"name": "ORS", "category": "Oral Rehydration", "available": True, "quantity": 60, "location": "General Pharmacy - Counter 1"},
        {"name": "Omeprazole", "category": "Gastrointestinal Medicine", "available": True, "quantity": 24, "location": "General Pharmacy - Counter 2"},
        {"name": "Amoxicillin", "category": "Antibiotic", "available": True, "quantity": 10, "location": "General Pharmacy - Counter 3"},
        {"name": "Arjuna", "category": "Ayurvedic Medicine", "available": False, "quantity": 0, "location": "Currently unavailable"}
    ]

    if request.method == "POST":
        searched = True
        search_term = request.form.get("medicine_name", "").strip()
        medicine = next((m for m in inventory if search_term.lower() in m["name"].lower()), None)

    return render_template(
        "medicine_availability.html",
        medicine=medicine,
        searched=searched,
        search_term=search_term
    )


@app.route("/document-extraction", methods=["GET", "POST"])
def document_extraction():
    extracted_text = None

    if request.method == "POST":
        document = request.files.get("document")
        if document and document.filename:
            fn = document.filename.lower()
            if fn.endswith(".txt"):
                try:
                    extracted_text = document.read().decode("utf-8", errors="ignore")
                except Exception:
                    extracted_text = "Unable to read the text document."
            elif fn.endswith(".pdf"):
                try:
                    import PyPDF2
                    reader = PyPDF2.PdfReader(document)
                    pages = [p.extract_text() for p in reader.pages if p.extract_text()]
                    extracted_text = "\n\n".join(pages) or "No text detected in this PDF."
                except ImportError:
                    extracted_text = "PyPDF2 is not installed. Run: pip install PyPDF2"
                except Exception as e:
                    extracted_text = f"Error reading PDF: {e}"
            else:
                extracted_text = "Unsupported file format. Please upload a PDF or TXT file."

    return render_template("document_extraction.html", extracted_text=extracted_text)


@app.route("/appointment", methods=["GET", "POST"])
def appointment():
    conn = get_db()
    appointment_data = None

    if request.method == "POST":
        patient_name = request.form.get("patient_name")
        appointment_date = request.form.get("appointment_date")
        appointment_time = request.form.get("appointment_time")
        consultation_type = request.form.get("consultation_type")

        count_row = conn.execute(
            "SELECT COUNT(*) FROM appointments WHERE appointment_date = ?", (appointment_date,)
        ).fetchone()
        queue_number = (count_row[0] if count_row else 0) + 1
        waiting_time = (queue_number - 1) * 15

        conn.execute("""
            INSERT INTO appointments (
                patient_name, appointment_date, appointment_time,
                consultation_type, queue_number, waiting_time, status
            ) VALUES (?, ?, ?, ?, ?, ?, 'Waiting')
        """, (patient_name, appointment_date, appointment_time, consultation_type, queue_number, waiting_time))
        conn.commit()

        appointment_data = {
            "patient_name": patient_name,
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
            "consultation_type": consultation_type,
            "queue_number": queue_number,
            "waiting_time": waiting_time
        }

    conn.close()
    return render_template("appointment.html", patient=None, appointment=appointment_data)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)