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



