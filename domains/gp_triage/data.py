"""
Tools for the NHS GP surgery triage assistant.

Each tool is a plain Python function that takes parameters and returns a string.
The agent calls these tools during its reasoning loop.

Mock data simulates a real patient database and clinical guidance system.
"""

# ── Mock Data ──────────────────────────────────────────────────────────────────

PATIENTS = {
    "PAT-001": {
        "patient_id": "PAT-001",
        "name": "Margaret Thornton",
        "date_of_birth": "1958-04-12",
        "nhs_number": "943 812 4567",
        "email": "m.thornton@email.com",
        "registered_gp": "Dr Amara Osei",
        "medical_notes": "Asthma, managed. Annual flu jab. Last review: Oct 2025.",
        "allergies": ["Penicillin"],
        "current_medications": ["Salbutamol inhaler (as needed)", "Beclometasone inhaler (twice daily)"],
    },
    "PAT-002": {
        "patient_id": "PAT-002",
        "name": "James Hargreaves",
        "date_of_birth": "1971-09-23",
        "nhs_number": "612 437 8901",
        "email": "j.hargreaves@email.com",
        "registered_gp": "Dr Amara Osei",
        "medical_notes": "Type 2 diabetes, well controlled. HbA1c 48 (Nov 2025). Hypertension.",
        "allergies": [],
        "current_medications": ["Metformin 500mg (twice daily)", "Ramipril 5mg (once daily)"],
    },
    "PAT-003": {
        "patient_id": "PAT-003",
        "name": "Sophie Williams",
        "date_of_birth": "1995-01-08",
        "nhs_number": "287 654 3120",
        "email": "sophie.w@email.com",
        "registered_gp": "Dr Rajesh Patel",
        "medical_notes": "No significant history. Contraceptive pill review due Apr 2026.",
        "allergies": ["Latex"],
        "current_medications": ["Rigevidon (oral contraceptive)"],
    },
    "PAT-004": {
        "patient_id": "PAT-004",
        "name": "David Kowalski",
        "date_of_birth": "1983-06-30",
        "nhs_number": "734 219 8654",
        "email": "d.kowalski@email.com",
        "registered_gp": "Dr Rajesh Patel",
        "medical_notes": "Depression — on SSRI since 2024, stable. CBT completed Jul 2025. Review due Mar 2026.",
        "allergies": [],
        "current_medications": ["Sertraline 100mg (once daily)"],
    },
    "PAT-005": {
        "patient_id": "PAT-005",
        "name": "Fatima Al-Rashid",
        "date_of_birth": "1967-11-15",
        "nhs_number": "451 876 2340",
        "email": "f.alrashid@email.com",
        "registered_gp": "Dr Amara Osei",
        "medical_notes": "Osteoarthritis (knees), managed with physio. High cholesterol — statin started Sep 2025.",
        "allergies": ["Ibuprofen", "Aspirin"],
        "current_medications": ["Paracetamol 1g (up to 4x daily)", "Atorvastatin 20mg (once daily)"],
    },
    "PAT-006": {
        "patient_id": "PAT-006",
        "name": "Ryan O'Brien",
        "date_of_birth": "1990-03-22",
        "nhs_number": "568 143 7892",
        "email": "ryan.obrien@email.com",
        "registered_gp": "Dr Rajesh Patel",
        "medical_notes": "Eczema, intermittent flare-ups. Last flare-up Nov 2025.",
        "allergies": [],
        "current_medications": ["Eumovate cream (as needed)"],
    },
    "PAT-007": {
        "patient_id": "PAT-007",
        "name": "Patricia Chen",
        "date_of_birth": "1945-08-03",
        "nhs_number": "892 310 5467",
        "email": "p.chen@email.com",
        "registered_gp": "Dr Amara Osei",
        "medical_notes": "COPD, moderate. Ex-smoker (quit 2010). Annual spirometry. Flu + COVID boosters up to date.",
        "allergies": ["Codeine"],
        "current_medications": ["Tiotropium inhaler (once daily)", "Carbocisteine 750mg (3x daily)"],
    },
    "PAT-008": {
        "patient_id": "PAT-008",
        "name": "Ben Carter",
        "date_of_birth": "2001-12-19",
        "nhs_number": "123 678 4590",
        "email": "ben.carter@email.com",
        "registered_gp": "Dr Rajesh Patel",
        "medical_notes": "No significant history. Last seen: sports injury (ankle sprain) Aug 2025.",
        "allergies": [],
        "current_medications": [],
    },
    "PAT-009": {
        "patient_id": "PAT-009",
        "name": "Linda Pearson",
        "date_of_birth": "1979-07-11",
        "nhs_number": "345 912 6781",
        "email": "l.pearson@email.com",
        "registered_gp": "Dr Amara Osei",
        "medical_notes": "Anxiety disorder, managed. GAD-7 score 8 (mild, Jan 2026). Declined medication — uses self-help resources.",
        "allergies": ["Erythromycin"],
        "current_medications": [],
    },
}

CLINICAL_GUIDELINES = {
    "respiratory": {
        "category": "respiratory",
        "triage_level": "routine",
        "guidance": (
            "Coughs lasting less than 3 weeks are usually viral and self-limiting. "
            "Advise rest, fluids, honey for soothing. Coughs persisting beyond 3 weeks "
            "require a GP appointment to rule out underlying causes. Productive coughs "
            "with green/yellow sputum lasting over 7 days may indicate bacterial infection "
            "— book routine GP appointment. Antibiotics are NOT first-line for most coughs."
        ),
        "red_flags": [
            "Coughing up blood",
            "Severe breathlessness at rest",
            "Chest pain with breathing",
            "Persistent fever over 38.5°C for more than 3 days",
            "Inability to complete sentences due to breathlessness",
        ],
        "referral_pathway": "Routine GP appointment. If red flags present, escalate to urgent same-day.",
    },
    "dermatology": {
        "category": "dermatology",
        "triage_level": "routine",
        "guidance": (
            "Most rashes are non-urgent. New rashes without systemic symptoms (fever, "
            "malaise) can be assessed at a routine appointment. Eczema flare-ups: advise "
            "emollients and existing prescribed treatment. For new or changing moles, book "
            "a 2-week wait referral pathway appointment. Widespread rash with fever requires "
            "same-day assessment."
        ),
        "red_flags": [
            "Non-blanching rash (does not fade when pressed with a glass)",
            "Rapid spread with fever",
            "Blistering covering large body area",
            "Rash following a tick bite (bull's-eye pattern)",
            "New or changing mole with irregular borders",
        ],
        "referral_pathway": "Routine GP appointment. Non-blanching rash: call 999 immediately.",
    },
    "musculoskeletal": {
        "category": "musculoskeletal",
        "triage_level": "routine",
        "guidance": (
            "Most back pain resolves within 6 weeks. Advise staying active, avoiding "
            "prolonged bed rest, over-the-counter pain relief (paracetamol, ibuprofen if "
            "tolerated). Joint pain without trauma: routine appointment for assessment. "
            "Post-injury swelling and pain: RICE protocol (Rest, Ice, Compression, Elevation) "
            "and routine appointment if not improving after 5 days."
        ),
        "red_flags": [
            "Loss of bladder or bowel control with back pain",
            "Numbness in saddle area (inner thighs, buttocks)",
            "Sudden severe joint swelling with fever (possible septic arthritis)",
            "Inability to bear weight after injury",
            "Progressive weakness in legs",
        ],
        "referral_pathway": "Routine GP appointment. Cauda equina symptoms (saddle numbness, bladder issues): A&E immediately.",
    },
    "mental_health": {
        "category": "mental_health",
        "triage_level": "urgent",
        "guidance": (
            "Low mood lasting more than 2 weeks warrants a GP appointment. Screen for: "
            "sleep disruption, appetite changes, loss of interest, concentration difficulties. "
            "Offer self-help resources (NHS Every Mind Matters). For worsening anxiety or "
            "panic attacks, book urgent appointment within 48 hours. NEVER attempt to assess "
            "severity — always refer to a clinician."
        ),
        "red_flags": [
            "Mention of self-harm or suicidal thoughts",
            "Expressing hopelessness or feeling like a burden",
            "Hearing voices or experiencing paranoia",
            "Sudden personality or behaviour changes",
            "Mention of a plan to end their life",
        ],
        "referral_pathway": "Urgent GP appointment within 48 hours. If self-harm/suicidal ideation: escalate to clinician IMMEDIATELY. Provide Samaritans (116 123) and Crisis Line.",
    },
    "gastrointestinal": {
        "category": "gastrointestinal",
        "triage_level": "routine",
        "guidance": (
            "Acute diarrhoea and vomiting: usually viral, self-limiting in 2-3 days. "
            "Advise clear fluids, small bland meals, oral rehydration sachets if needed. "
            "Persistent symptoms beyond 7 days: routine GP appointment. Recurrent heartburn "
            "or acid reflux: routine appointment, may need review of diet and medication. "
            "Change in bowel habit lasting more than 3 weeks in over-50s requires urgent referral."
        ),
        "red_flags": [
            "Blood in stool or vomit",
            "Severe abdominal pain (unable to move or stand)",
            "Signs of dehydration (no urine for 12+ hours, dizziness on standing)",
            "Unexplained weight loss with changed bowel habit",
            "Persistent vomiting unable to keep fluids down for 24+ hours",
        ],
        "referral_pathway": "Routine GP appointment. Blood in stool with weight loss: 2-week wait referral. Severe pain: A&E.",
    },
    "urgent_symptoms": {
        "category": "urgent_symptoms",
        "triage_level": "emergency",
        "guidance": (
            "ALWAYS ESCALATE IMMEDIATELY. The following symptoms require immediate clinical "
            "assessment and MUST NOT be triaged by this system: chest pain, sudden severe "
            "headache, stroke symptoms (FAST — Face drooping, Arm weakness, Speech difficulty, "
            "Time to call 999), difficulty breathing at rest, loss of consciousness, severe "
            "allergic reaction (anaphylaxis), heavy uncontrolled bleeding."
        ),
        "red_flags": [
            "Chest pain or tightness",
            "Sudden severe headache ('worst headache of my life')",
            "Facial drooping, arm weakness, slurred speech (stroke)",
            "Severe difficulty breathing",
            "Loss of consciousness or unresponsiveness",
            "Signs of anaphylaxis (swelling of face/throat, difficulty breathing after exposure)",
        ],
        "referral_pathway": "DO NOT TRIAGE. Escalate to clinician immediately. Advise patient to call 999 if symptoms are acute.",
    },
}

# ── Hard guardrail: emergency auto-escalation ─────────────────────────────────

EMERGENCY_AUTO_ESCALATE = True  # When True, any "emergency" triage level auto-escalates to clinician


# ── Tool Functions ─────────────────────────────────────────────────────────────

def lookup_patient(patient_id: str) -> str:
    """Look up a patient by their ID. Returns patient details or an error."""
    patient = PATIENTS.get(patient_id.upper())
    if not patient:
        return f"Error: Patient '{patient_id}' not found. Please check the patient ID and try again."
    allergies = ", ".join(patient["allergies"]) if patient["allergies"] else "None recorded"
    medications = ", ".join(patient["current_medications"]) if patient["current_medications"] else "None"
    return (
        f"Patient {patient['patient_id']}:\n"
        f"  Name: {patient['name']}\n"
        f"  DOB: {patient['date_of_birth']}\n"
        f"  NHS Number: {patient['nhs_number']}\n"
        f"  Email: {patient['email']}\n"
        f"  Registered GP: {patient['registered_gp']}\n"
        f"  Medical Notes: {patient['medical_notes']}\n"
        f"  Allergies: {allergies}\n"
        f"  Current Medications: {medications}"
    )


def check_clinical_guidelines(category: str) -> str:
    """Check clinical triage guidelines for a symptom category."""
    guideline = CLINICAL_GUIDELINES.get(category.lower())
    if not guideline:
        return f"Error: No clinical guidelines found for category '{category}'."
    red_flags = "\n    - ".join(guideline["red_flags"])
    return (
        f"Clinical Guidelines — {guideline['category']}:\n"
        f"  Triage Level: {guideline['triage_level']}\n"
        f"  Guidance: {guideline['guidance']}\n"
        f"  Red Flags:\n    - {red_flags}\n"
        f"  Referral Pathway: {guideline['referral_pathway']}"
    )


def book_appointment(patient_id: str, appointment_type: str, urgency: str, guardrails_enabled: bool = True) -> str:
    """
    Book an appointment for a patient.

    HARD GUARDRAIL: If guardrails are enabled and the urgency is "emergency",
    the booking is blocked — emergencies must be escalated to a clinician, not booked.
    """
    patient = PATIENTS.get(patient_id.upper())
    if not patient:
        return f"Error: Patient '{patient_id}' not found."

    if guardrails_enabled and urgency.lower() == "emergency":
        return (
            "BLOCKED: Emergency cases cannot be booked as appointments. "
            "This patient requires immediate clinical assessment. "
            "Please escalate to a clinician immediately using escalate_to_clinician."
        )

    urgency_slots = {
        "routine": "next available (typically 3-5 working days)",
        "urgent": "same-day or next working day",
    }
    slot = urgency_slots.get(urgency.lower(), "next available")

    return (
        f"Appointment booked successfully:\n"
        f"  Patient: {patient['name']} ({patient_id})\n"
        f"  Type: {appointment_type}\n"
        f"  Urgency: {urgency}\n"
        f"  Slot: {slot}\n"
        f"  The patient will receive a confirmation text and email."
    )


def send_patient_message(email: str, subject: str, body: str) -> str:
    """Send a message to a patient. (Simulated — does not actually send.)"""
    return (
        f"Message sent successfully:\n"
        f"  To: {email}\n"
        f"  Subject: {subject}\n"
        f"  Body preview: {body[:100]}..."
    )


def escalate_to_clinician(patient_id: str, reason: str, urgency: str = "urgent") -> str:
    """Escalate a case to a clinician for clinical review."""
    patient = PATIENTS.get(patient_id.upper())
    patient_name = patient["name"] if patient else "Unknown"

    urgency_response = {
        "routine": "within 24 hours",
        "urgent": "within 2 hours",
        "emergency": "IMMEDIATELY — clinician alerted now",
    }
    response_time = urgency_response.get(urgency.lower(), "within 2 hours")

    return (
        f"Case escalated to clinician:\n"
        f"  Patient: {patient_name} ({patient_id})\n"
        f"  Urgency: {urgency}\n"
        f"  Reason: {reason}\n"
        f"  Response: A clinician will review this case {response_time}."
    )


# ── FAQ Knowledge Base (simulated) ────────────────────────────────────────────

FAQ_ENTRIES = {
    "booking": {
        "question": "How do I book an appointment?",
        "answer": "You can book appointments online via the NHS App or our surgery website, by calling reception (Mon-Fri 8am-6:30pm), or in person. Same-day urgent appointments are released at 8am each morning. Routine appointments can be booked up to 4 weeks in advance.",
        "keywords": ["book", "appointment", "see doctor", "GP", "schedule", "available"],
    },
    "prescriptions": {
        "question": "How do I order a repeat prescription?",
        "answer": "Repeat prescriptions can be ordered via the NHS App, our website, by dropping a slip at reception, or by asking your pharmacy to request it on your behalf. Please allow 48 working hours for processing. We cannot take prescription requests over the phone.",
        "keywords": ["prescription", "repeat", "medication", "medicine", "refill", "renew"],
    },
    "out_of_hours": {
        "question": "What do I do outside surgery hours?",
        "answer": "For urgent medical issues outside surgery hours (after 6:30pm weekdays, weekends, bank holidays), call NHS 111. For life-threatening emergencies, call 999 or go to A&E. Our out-of-hours service is provided by the local NHS 111 clinical assessment service.",
        "keywords": ["out of hours", "evening", "weekend", "night", "emergency", "111", "closed"],
    },
    "test_results": {
        "question": "How do I get my test results?",
        "answer": "Blood test results are usually available within 5 working days. You can view results via the NHS App or call reception after 2pm. If results require action, we will contact you directly. No news is usually good news, but do check if you haven't heard back within 7 days.",
        "keywords": ["results", "blood test", "test", "lab", "when", "how long"],
    },
    "registration": {
        "question": "How do I register as a new patient?",
        "answer": "To register, complete a GMS1 registration form (available at reception or on our website). Bring photo ID and proof of address. You do not need an NHS number to register — we can look this up. Registration is usually processed within 48 hours.",
        "keywords": ["register", "new patient", "join", "sign up", "move", "registration"],
    },
    "home_visits": {
        "question": "Can I request a home visit?",
        "answer": "Home visits are available for patients who are housebound or too unwell to attend the surgery. Call reception before 10:30am to request a same-day home visit. A clinician will call you back to assess whether a home visit is necessary or if your needs can be met by phone or video consultation.",
        "keywords": ["home visit", "housebound", "can't travel", "come to me", "too ill"],
    },
    "repeat_prescriptions": {
        "question": "How do repeat prescriptions work?",
        "answer": "Your GP sets up a repeat prescription list during your appointment. You can then order these items without seeing the GP each time. Repeats are reviewed annually — you'll be invited for a medication review. If a medication is not on your repeat list, you'll need a GP appointment to have it added.",
        "keywords": ["repeat", "how does it work", "automatic", "regular medication", "review"],
    },
    "vaccinations": {
        "question": "How do I book a vaccination?",
        "answer": "Routine vaccinations (flu, COVID booster, shingles, pneumonia) are offered seasonally — we'll contact eligible patients by text or letter. Travel vaccinations require a consultation first — book a travel health appointment at least 6 weeks before your trip. Some travel vaccines are not available on the NHS and may incur a charge.",
        "keywords": ["vaccine", "vaccination", "flu jab", "COVID", "booster", "travel", "immunisation"],
    },
}


def search_faq(query: str) -> str:
    """Search the surgery knowledge base for answers to common questions."""
    query_lower = query.lower()
    scored = []
    for key, entry in FAQ_ENTRIES.items():
        score = sum(1 for kw in entry["keywords"] if kw in query_lower)
        if score > 0:
            scored.append((score, entry))

    if not scored:
        return "No FAQ results found. The patient's question may need to be handled by reception staff."

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:2]  # Return top 2 matches
    results = []
    for _, entry in top:
        results.append(f"Q: {entry['question']}\nA: {entry['answer']}")
    return "\n\n".join(results)


# ── Failure Injection (chaos testing for agents) ─────────────────────────────

FAILURE_MODES = {
    "service_unavailable": "Error: Service temporarily unavailable. Please try again later.",
    "timeout": "Error: Request timed out after 30 seconds. The service may be experiencing high load.",
    "server_error": "Error: Internal server error (500). An unexpected error occurred.",
    "permission_denied": "Error: Access denied. Authentication token expired.",
}


def inject_failure(tool_name: str, failure_config: dict) -> str | None:
    """
    Check if a tool should fail based on the failure config.

    Args:
        tool_name: Name of the tool being called.
        failure_config: Dict mapping tool names to failure mode keys.
            e.g. {"lookup_patient": "service_unavailable", "book_appointment": "timeout"}

    Returns:
        Error string if the tool should fail, None if it should work normally.
    """
    failure_mode = failure_config.get(tool_name)
    if failure_mode and failure_mode in FAILURE_MODES:
        return FAILURE_MODES[failure_mode]
    return None


# ── Tool registry (used by the agent to know what's available) ─────────────────

# ── Domain metadata (used by domain loader) ──────────────────────────────────

DOMAIN_META = {
    "name": "Greenfield Surgery",
    "tagline": "NHS GP surgery — patient triage",
    "description": (
        "An NHS GP surgery in the West Midlands with two GPs (Dr Amara Osei and "
        "Dr Rajesh Patel). Provides standard primary care services to registered patients."
    ),
    "stakes": "High (health)",
    "colour": "#4A90D9",
    "company_context": (
        "NHS GP surgery offering routine and urgent appointments, telephone consultations, "
        "repeat prescriptions, vaccinations, and blood tests. Free at point of care. "
        "Appointments via phone (Mon-Fri 8am-6:30pm) or in person. Same-day urgent slots "
        "released at 8am. Out-of-hours: NHS 111 for urgent issues, 999 for emergencies."
    ),
    "agent_role": (
        "Patient triage assistant that helps patients book appointments and provides "
        "general practice information — not a medical professional"
    ),
    "hard_guardrail_name": "Emergency auto-escalation",
    "hard_guardrail_description": (
        "When emergency keywords are detected (chest pain, breathing difficulty, self-harm), "
        "the agent immediately escalates to emergency services. This is a code-level "
        "guardrail the agent cannot override."
    ),
}


TOOLS = {
    "lookup_patient": {
        "function": lookup_patient,
        "description": "Look up a patient by their ID. Returns name, DOB, NHS number, GP, medical notes, allergies, and current medications.",
        "parameters": {"patient_id": "The patient ID (e.g. PAT-001)"},
    },
    "check_clinical_guidelines": {
        "function": check_clinical_guidelines,
        "description": "Check clinical triage guidelines for a symptom category. Returns triage level, guidance, red flags, and referral pathway.",
        "parameters": {"category": "Symptom category (e.g. respiratory, dermatology, musculoskeletal, mental_health, gastrointestinal, urgent_symptoms)"},
    },
    "book_appointment": {
        "function": book_appointment,
        "description": "Book an appointment for a patient. Requires patient ID, appointment type, and urgency level.",
        "parameters": {
            "patient_id": "The patient ID",
            "appointment_type": "Type of appointment (e.g. GP consultation, nurse review, telephone consultation)",
            "urgency": "Urgency level: 'routine', 'urgent', or 'emergency'",
        },
    },
    "send_patient_message": {
        "function": send_patient_message,
        "description": "Send a message to a patient with a subject and body.",
        "parameters": {
            "email": "Patient's email address",
            "subject": "Message subject line",
            "body": "Message body text",
        },
    },
    "escalate_to_clinician": {
        "function": escalate_to_clinician,
        "description": "Escalate a case to a clinician for clinical review. Use for any situation requiring medical judgement.",
        "parameters": {
            "patient_id": "The patient ID",
            "reason": "Why this case needs clinician attention",
            "urgency": "Urgency level: 'routine', 'urgent', or 'emergency' (optional, defaults to urgent)",
        },
    },
    "search_faq": {
        "function": search_faq,
        "description": "Search the surgery knowledge base for answers to common questions about appointments, prescriptions, test results, registration, and services.",
        "parameters": {"query": "The patient's question or keywords to search for"},
    },
}
