System Architechture
                    
                    
                    ┌──────────────────────────┐
                    │       USER LAYER         │
                    │                          │
                    │  Patient │ Doctor        │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │     FRONTEND / UI        │
                    │                          │
                    │ HTML │ CSS │ Jinja2       │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │      FLASK BACKEND       │
                    │                          │
                    │ Authentication            │
                    │ Patient Management        │
                    │ Appointment & Queue       │
                    │ Case Taking               │
                    │ Medicine Availability     │
                    └────────────┬─────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
      ┌──────────────┐   ┌───────────────┐   ┌──────────────┐
      │ AI CASE      │   │ DOCUMENT      │   │ RED-FLAG     │
      │ ENGINE       │   │ PROCESSING    │   │ SCREENING    │
      │              │   │               │   │              │
      │ Adaptive     │   │ Medical       │   │ Symptom      │
      │ Questioning  │   │ Documents     │   │ Detection    │
      └──────┬───────┘   └───────┬───────┘   └──────┬───────┘
             │                   │                  │
             └───────────────────┼──────────────────┘
                                 ▼
                    ┌──────────────────────────┐
                    │      CASE PROCESSING     │
                    │                          │
                    │ Doctor-Ready Summary     │
                    │ Patient History           │
                    │ Important Findings       │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │       DATABASE           │
                    │                          │
                    │ SQLite                   │
                    │ Patients                 │
                    │ Appointments             │
                    │ Cases / Messages         │
                    │ Medicine Inventory       │
                    └─────────────────────────


System Flowchart

START
  │
  ▼
Login / Registration
  │
  ▼
Select User Type
  │
 ┌┴───────────────┐
 ▼                ▼
PATIENT          DOCTOR
 │                │
 ▼                ▼
Patient Portal   Doctor Dashboard
 │                │
 ├─────────┐      ├──► View Patients
 │         │      │
 ▼         ▼      ▼
AI Case   Book   View Patient Case
Taking    Appt.      │
 │         │         ▼
 ▼         ▼    Document Extraction
Symptoms  Queue       │
 │         │          ▼
 ▼         ▼    Red-Flag Screening
Adaptive  Estimated    │
Questions Wait Time    │
 │                    ▼
 ▼              Doctor-Ready
Red Flag?       Case Summary
 │                    │
 ├── YES ─────────────┤
 │                    │
 ▼                    ▼
Alert Doctor     Doctor Consultation
 │                    │
 └──────────┬─────────┘
            ▼
    Medicine Availability
            │
            ▼
     Consultation Complete
            │
            ▼
     Digital Case Record
            │
            ▼
           END
