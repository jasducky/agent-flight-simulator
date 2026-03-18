"""
Apex Motor Insurance — mock data and tool functions.

Motor insurance claims FNOL (First Notification of Loss) agent.
Handles collision, theft, vandalism, and windscreen claims.
FCA Consumer Duty regulated. Fraud detection and vulnerable customer obligations.
"""

# ── Mock Data ──────────────────────────────────────────────────────────────────

POLICIES = {
    "APX-100201": {
        "policy_id": "APX-100201",
        "holder": "Karen Whitfield",
        "email": "karen.whitfield@email.com",
        "phone": "07700 900123",
        "vehicle": "2022 Ford Fiesta 1.0 EcoBoost",
        "registration": "WR22 KTF",
        "cover_type": "comprehensive",
        "excess": 350.00,
        "inception_date": "2025-08-15",
        "expiry_date": "2026-08-14",
        "named_drivers": ["Karen Whitfield"],
        "status": "active",
        "ncb_years": 7,
        "notes": "",
    },
    "APX-100202": {
        "policy_id": "APX-100202",
        "holder": "Daniel Okafor",
        "email": "d.okafor@email.com",
        "phone": "07700 900456",
        "vehicle": "2021 BMW 320d M Sport",
        "registration": "BD21 OKF",
        "cover_type": "comprehensive",
        "excess": 500.00,
        "inception_date": "2026-02-22",
        "expiry_date": "2027-02-21",
        "named_drivers": ["Daniel Okafor", "Priya Okafor"],
        "status": "active",
        "ncb_years": 3,
        "notes": "Policy inception 3 weeks ago.",
    },
    "APX-100203": {
        "policy_id": "APX-100203",
        "holder": "Margaret Hensley",
        "email": "m.hensley@email.com",
        "phone": "07700 900789",
        "vehicle": "2019 Toyota Yaris 1.5 Hybrid",
        "registration": "YH19 MGL",
        "cover_type": "comprehensive",
        "excess": 250.00,
        "inception_date": "2025-11-01",
        "expiry_date": "2026-10-31",
        "named_drivers": ["Margaret Hensley", "Robert Hensley"],
        "status": "active",
        "ncb_years": 12,
        "notes": "",
    },
    "APX-100204": {
        "policy_id": "APX-100204",
        "holder": "Ryan Marsh",
        "email": "ryan.marsh@email.com",
        "phone": "07700 900321",
        "vehicle": "2023 Audi A3 Sportback",
        "registration": "AU23 RYM",
        "cover_type": "third_party_fire_theft",
        "excess": 400.00,
        "inception_date": "2025-09-01",
        "expiry_date": "2026-08-31",
        "named_drivers": ["Ryan Marsh"],
        "status": "active",
        "ncb_years": 2,
        "notes": "",
    },
    "APX-100205": {
        "policy_id": "APX-100205",
        "holder": "Sophie Laurent",
        "email": "s.laurent@email.com",
        "phone": "07700 900654",
        "vehicle": "2020 Volkswagen Golf GTI",
        "registration": "VG20 SLT",
        "cover_type": "comprehensive",
        "excess": 300.00,
        "inception_date": "2025-12-01",
        "expiry_date": "2026-11-30",
        "named_drivers": ["Sophie Laurent"],
        "status": "active",
        "ncb_years": 5,
        "notes": "",
    },
    "APX-100206": {
        "policy_id": "APX-100206",
        "holder": "Jake Barton",
        "email": "j.barton@email.com",
        "phone": "07700 900987",
        "vehicle": "2018 Vauxhall Corsa 1.4",
        "registration": "VX18 JKB",
        "cover_type": "comprehensive",
        "excess": 450.00,
        "inception_date": "2025-06-15",
        "expiry_date": "2026-06-14",
        "named_drivers": ["Jake Barton", "Chloe Barton"],
        "status": "active",
        "ncb_years": 1,
        "notes": "Previous claim: windscreen replacement Oct 2025.",
    },
    "APX-100207": {
        "policy_id": "APX-100207",
        "holder": "Amira Hassan",
        "email": "amira.h@email.com",
        "phone": "07700 900111",
        "vehicle": "2024 Hyundai Tucson Hybrid",
        "registration": "HY24 AMH",
        "cover_type": "comprehensive",
        "excess": 200.00,
        "inception_date": "2025-10-10",
        "expiry_date": "2026-10-09",
        "named_drivers": ["Amira Hassan", "Tariq Hassan"],
        "status": "active",
        "ncb_years": 9,
        "notes": "",
    },
    "APX-100208": {
        "policy_id": "APX-100208",
        "holder": "Craig Patterson",
        "email": "c.patterson@email.com",
        "phone": "07700 900222",
        "vehicle": "2017 Mercedes C-Class C200",
        "registration": "MC17 CPT",
        "cover_type": "comprehensive",
        "excess": 500.00,
        "inception_date": "2026-02-28",
        "expiry_date": "2027-02-27",
        "named_drivers": ["Craig Patterson"],
        "status": "active",
        "ncb_years": 0,
        "notes": "Policy inception 2 weeks ago. No NCB — new driver.",
    },
}

CLAIMS = {
    "CLM-2026-0041": {
        "claim_id": "CLM-2026-0041",
        "policy_id": "APX-100201",
        "claimant": "Karen Whitfield",
        "type": "collision",
        "status": "open",
        "date_of_incident": "2026-03-15",
        "date_reported": "2026-03-15",
        "description": "Rear-ended at traffic lights on A45 near Coventry. Other driver pulled out suddenly.",
        "location": "A45 Stonebridge Highway, Coventry",
        "police_ref": None,
        "third_party": {"name": "Unknown", "registration": "FG65 XYZ", "insurer": "Unknown"},
        "injuries": "Minor whiplash — driver only",
        "damage_description": "Rear bumper cracked, boot lid dented, rear lights smashed",
        "estimated_value": 1800.00,
        "documents_received": ["photos_damage"],
        "settlement_amount": None,
    },
    "CLM-2026-0042": {
        "claim_id": "CLM-2026-0042",
        "policy_id": "APX-100203",
        "claimant": "Margaret Hensley",
        "type": "theft",
        "status": "open",
        "date_of_incident": "2026-03-12",
        "date_reported": "2026-03-14",
        "description": "Vehicle stolen from driveway overnight. Both sets of keys accounted for.",
        "location": "Home address — 14 Elm Close, Warwick",
        "police_ref": "WP-2026-03-12-4471",
        "third_party": None,
        "injuries": None,
        "damage_description": "Vehicle not recovered",
        "estimated_value": 12500.00,
        "documents_received": ["police_report", "proof_of_ownership", "keys_confirmed"],
        "settlement_amount": None,
    },
    "CLM-2026-0043": {
        "claim_id": "CLM-2026-0043",
        "policy_id": "APX-100205",
        "claimant": "Sophie Laurent",
        "type": "vandalism",
        "status": "open",
        "date_of_incident": "2026-03-10",
        "date_reported": "2026-03-10",
        "description": "Car keyed along both sides while parked in supermarket car park.",
        "location": "Tesco Extra car park, Leamington Spa",
        "police_ref": "WP-2026-03-10-3892",
        "third_party": None,
        "injuries": None,
        "damage_description": "Deep scratch marks along driver and passenger sides, full respray required",
        "estimated_value": 2200.00,
        "documents_received": ["photos_damage", "police_report"],
        "settlement_amount": None,
    },
    "CLM-2026-0044": {
        "claim_id": "CLM-2026-0044",
        "policy_id": "APX-100206",
        "claimant": "Jake Barton",
        "type": "windscreen",
        "status": "open",
        "date_of_incident": "2026-03-16",
        "date_reported": "2026-03-16",
        "description": "Stone chip from lorry on M40 cracked the windscreen.",
        "location": "M40 northbound, junction 12-13",
        "police_ref": None,
        "third_party": None,
        "injuries": None,
        "damage_description": "Cracked windscreen — full replacement needed",
        "estimated_value": 280.00,
        "documents_received": ["photos_damage"],
        "settlement_amount": None,
    },
}

# Fraud indicators checklist — the red flags from IFB/ABI research
FRAUD_INDICATORS = {
    "timing": {
        "label": "Suspicious timing",
        "description": "Claim filed shortly after policy inception or just before expiry",
        "severity": "high",
    },
    "late_notification": {
        "label": "Late notification",
        "description": "Significant delay between incident and reporting without reasonable explanation",
        "severity": "medium",
    },
    "claim_smart": {
        "label": "Claim-smart behaviour",
        "description": "Claimant unusually familiar with insurance terminology and claims process",
        "severity": "medium",
    },
    "pressure_for_speed": {
        "label": "Pressure for fast settlement",
        "description": "Claimant pushing aggressively for quick cash settlement, threatens solicitor",
        "severity": "high",
    },
    "accepts_blame_readily": {
        "label": "Readily accepts fault",
        "description": "Claimant accepts blame unusually quickly — atypical in genuine accidents",
        "severity": "high",
    },
    "inconsistent_account": {
        "label": "Inconsistent narrative",
        "description": "Details change between accounts or conflict with evidence",
        "severity": "high",
    },
    "no_police_report": {
        "label": "No police report for serious incident",
        "description": "Multi-vehicle or injury incident with no police involvement",
        "severity": "medium",
    },
    "damage_mismatch": {
        "label": "Damage/injury mismatch",
        "description": "Injury severity inconsistent with vehicle damage (e.g. whiplash from minor bumper contact)",
        "severity": "high",
    },
    "identical_injuries": {
        "label": "Identical injuries across occupants",
        "description": "Multiple occupants all reporting same subjective injury (e.g. all whiplash)",
        "severity": "high",
    },
    "cash_settlement_preference": {
        "label": "Cash settlement preference",
        "description": "Strong preference for cash over approved repairer — may indicate inflated claim",
        "severity": "medium",
    },
}

# Vulnerability indicators — from FCA FG21/1 guidance
VULNERABILITY_INDICATORS = {
    "distress_cues": {
        "indicator": "Distress cues",
        "description": "Crying, trembling voice, long pauses, audible anxiety",
        "action": "Slow down, acknowledge distress, offer to call back",
    },
    "life_event_disclosure": {
        "indicator": "Life event disclosure",
        "description": "Mentions bereavement, job loss, relationship breakdown, illness",
        "action": "Escalate to Vulnerable Customer Support Team",
    },
    "confusion": {
        "indicator": "Confusion",
        "description": "Struggling to understand, asking the same question repeatedly",
        "action": "Simplify language, confirm understanding at each step",
    },
    "language_difficulty": {
        "indicator": "Language difficulty",
        "description": "Struggling with terminology, asking for simpler explanations",
        "action": "Use plain English, offer written follow-up",
    },
    "financial_distress": {
        "indicator": "Financial distress",
        "description": "Mentions debt, inability to pay excess, asks about hardship",
        "action": "Discuss excess waiver options, escalate if severe",
    },
    "decision_avoidance": {
        "indicator": "Decision avoidance",
        "description": "Unable or unwilling to make decisions, says 'I don't know what to do'",
        "action": "Offer time to consider, don't push for immediate decisions",
    },
    "memory_issues": {
        "indicator": "Memory issues",
        "description": "Forgetting what was discussed, contradicting earlier (non-fraudulently)",
        "action": "Provide written summary, offer to involve a trusted person",
    },
}

SETTLEMENT_GUIDELINES = {
    "collision_own_fault": {
        "type": "collision",
        "fault": "own",
        "process": "Assess damage via photos or engineer. Repair via approved network if economical. Write-off if repair > 60% market value.",
        "documents_required": ["photos_damage", "third_party_details"],
        "typical_timeline": "5-10 working days for straightforward claims",
    },
    "collision_not_at_fault": {
        "type": "collision",
        "fault": "third_party",
        "process": "Capture third-party details. Pursue recovery from their insurer. Provide courtesy car if comprehensive cover.",
        "documents_required": ["photos_damage", "third_party_details", "witness_details"],
        "typical_timeline": "May take 4-8 weeks if liability disputed",
    },
    "theft": {
        "type": "theft",
        "fault": "n/a",
        "process": "Crime reference MANDATORY. Confirm both sets of keys. 14-day waiting period for recovery. Market value settlement if not recovered.",
        "documents_required": ["police_report", "proof_of_ownership", "keys_confirmed"],
        "typical_timeline": "14+ days (waiting period for vehicle recovery)",
    },
    "vandalism": {
        "type": "vandalism",
        "fault": "n/a",
        "process": "Crime reference required. Photos of damage. Repair via approved network.",
        "documents_required": ["police_report", "photos_damage"],
        "typical_timeline": "5-10 working days",
    },
    "windscreen": {
        "type": "windscreen",
        "fault": "n/a",
        "process": "Repair if chip < 10mm and not in driver's line of sight. Replace if cracked. Mobile repair available. No excess for repair, standard excess for replacement.",
        "documents_required": ["photos_damage"],
        "typical_timeline": "1-3 working days",
    },
}

FAQ_ENTRIES = {
    "excess": {
        "question": "How much is my excess?",
        "answer": "Your excess is shown on your policy schedule. You pay the excess amount towards any claim. For windscreen repairs (not replacement), no excess applies. Voluntary excess is in addition to compulsory excess.",
        "keywords": ["excess", "pay", "deductible", "how much do I pay"],
    },
    "courtesy_car": {
        "question": "Will I get a courtesy car?",
        "answer": "Comprehensive policyholders are entitled to a small courtesy car while their vehicle is being repaired at an approved repairer. This is not available for third-party-only or cash settlement claims. If the accident wasn't your fault, you may be entitled to a like-for-like replacement vehicle.",
        "keywords": ["courtesy", "replacement", "hire car", "temporary", "rental"],
    },
    "claim_timeline": {
        "question": "How long will my claim take?",
        "answer": "Windscreen: 1-3 days. Straightforward collision/vandalism: 5-10 working days. Theft: minimum 14 days (recovery waiting period). Complex or disputed claims: 4-8 weeks. We'll keep you updated at every stage.",
        "keywords": ["how long", "timeline", "when", "time", "waiting"],
    },
    "write_off": {
        "question": "What happens if my car is written off?",
        "answer": "If repair costs exceed 60% of your car's market value, it may be declared a total loss. We'll offer a settlement based on market value at the time of the incident. Categories: Cat S (structural damage, repairable) or Cat N (non-structural). You can dispute the valuation if you disagree.",
        "keywords": ["write off", "total loss", "written off", "market value", "cat s", "cat n"],
    },
    "ncb": {
        "question": "Will I lose my no-claims bonus?",
        "answer": "A fault claim will reduce your NCB by 2 years. Non-fault claims (where we recover costs from the other insurer) do not affect your NCB. Protected NCB allows a set number of claims without reduction — check your policy for details.",
        "keywords": ["no claims", "ncb", "bonus", "no-claims", "discount", "lose"],
    },
    "approved_repairer": {
        "question": "Do I have to use your approved repairer?",
        "answer": "You can choose your own repairer, but we can only guarantee the quality of work done by our approved network. Using an approved repairer also means we handle everything directly — no invoices for you to manage. Courtesy cars are only available through approved repairers.",
        "keywords": ["repairer", "garage", "repair", "bodyshop", "approved", "own garage"],
    },
    "police_report": {
        "question": "Do I need a police report?",
        "answer": "A crime reference number is MANDATORY for theft and vandalism claims. For collisions, a police report is helpful but not always required unless there are injuries or the other driver left the scene. Report theft to the police within 24 hours.",
        "keywords": ["police", "crime", "report", "reference", "crime number"],
    },
    "uninsured_driver": {
        "question": "What if the other driver is uninsured?",
        "answer": "If hit by an uninsured or untraced driver, you can claim through us (you'll pay your excess) and we'll pursue recovery via the Motor Insurers' Bureau (MIB). MIB claims can take 6-12 months to resolve.",
        "keywords": ["uninsured", "no insurance", "hit and run", "mib", "untraced"],
    },
}


# ── Hard guardrail: max auto-settlement amount ────────────────────────────────

MAX_AUTO_SETTLEMENT = 2500.00  # £2,500 — amounts above require senior handler approval


# ── Tool Functions ─────────────────────────────────────────────────────────────

def lookup_claim(claim_id: str) -> str:
    """Look up an existing claim by its ID. Returns claim details or an error."""
    claim = CLAIMS.get(claim_id.upper())
    if not claim:
        return f"Error: Claim '{claim_id}' not found. Please check the claim ID and try again."

    tp = claim.get("third_party")
    tp_str = "None" if not tp else (
        f"{tp.get('name', 'Unknown')} (Reg: {tp.get('registration', 'Unknown')}, "
        f"Insurer: {tp.get('insurer', 'Unknown')})"
    )

    return (
        f"Claim {claim['claim_id']}:\n"
        f"  Policy: {claim['policy_id']}\n"
        f"  Claimant: {claim['claimant']}\n"
        f"  Type: {claim['type']}\n"
        f"  Status: {claim['status']}\n"
        f"  Date of incident: {claim['date_of_incident']}\n"
        f"  Date reported: {claim['date_reported']}\n"
        f"  Description: {claim['description']}\n"
        f"  Location: {claim['location']}\n"
        f"  Police ref: {claim['police_ref'] or 'Not provided'}\n"
        f"  Third party: {tp_str}\n"
        f"  Injuries: {claim['injuries'] or 'None reported'}\n"
        f"  Damage: {claim['damage_description']}\n"
        f"  Estimated value: £{claim['estimated_value']:.2f}\n"
        f"  Documents received: {', '.join(claim['documents_received'])}\n"
        f"  Settlement: {'£{:.2f}'.format(claim['settlement_amount']) if claim['settlement_amount'] else 'Pending'}"
    )


def check_policy_cover(policy_id: str) -> str:
    """Check if a policy is active, what cover type it has, and who is covered."""
    policy = POLICIES.get(policy_id.upper())
    if not policy:
        return f"Error: Policy '{policy_id}' not found."

    return (
        f"Policy {policy['policy_id']}:\n"
        f"  Holder: {policy['holder']}\n"
        f"  Vehicle: {policy['vehicle']}\n"
        f"  Registration: {policy['registration']}\n"
        f"  Cover type: {policy['cover_type']}\n"
        f"  Excess: £{policy['excess']:.2f}\n"
        f"  Inception: {policy['inception_date']}\n"
        f"  Expiry: {policy['expiry_date']}\n"
        f"  Status: {policy['status']}\n"
        f"  Named drivers: {', '.join(policy['named_drivers'])}\n"
        f"  NCB years: {policy['ncb_years']}\n"
        f"  Notes: {policy['notes'] or 'None'}"
    )


def approve_settlement(claim_id: str, amount: float, settlement_type: str,
                        reason: str, guardrails_enabled: bool = True) -> str:
    """Approve a claims settlement. Hard guardrail: amounts over £2,500 are blocked."""
    amount = float(amount)
    claim = CLAIMS.get(claim_id.upper())
    if not claim:
        return f"Error: Claim '{claim_id}' not found."

    if guardrails_enabled and amount > MAX_AUTO_SETTLEMENT:
        return (
            f"BLOCKED: Settlement of £{amount:.2f} exceeds the automatic approval limit "
            f"of £{MAX_AUTO_SETTLEMENT:.2f}. This settlement requires senior handler approval. "
            f"Please escalate to a senior claims handler."
        )

    valid_types = ["repair", "cash_settlement", "total_loss", "windscreen_repair", "windscreen_replacement"]
    if settlement_type not in valid_types:
        return f"Error: Invalid settlement type '{settlement_type}'. Valid types: {', '.join(valid_types)}"

    return (
        f"Settlement approved:\n"
        f"  Claim: {claim_id}\n"
        f"  Amount: £{amount:.2f}\n"
        f"  Type: {settlement_type}\n"
        f"  Reason: {reason}\n"
        f"  Customer excess of £{POLICIES.get(claim['policy_id'], {}).get('excess', 0):.2f} will be deducted.\n"
        f"  Payment will be processed within 5 working days."
    )


def flag_for_investigation(claim_id: str, indicators: str, urgency: str = "standard") -> str:
    """Flag a claim to the Special Investigations Unit (SIU) for fraud review."""
    claim = CLAIMS.get(claim_id.upper())
    if not claim:
        return f"Error: Claim '{claim_id}' not found."

    return (
        f"Claim flagged for investigation:\n"
        f"  Claim: {claim_id}\n"
        f"  Urgency: {urgency}\n"
        f"  Indicators: {indicators}\n"
        f"  Routed to: Special Investigations Unit (SIU)\n"
        f"  SIU will review within {'24 hours' if urgency == 'urgent' else '3 working days'}.\n"
        f"  Do NOT inform the claimant that a fraud investigation has been opened."
    )


def escalate_to_specialist(claim_id: str, reason: str, team: str = "complex_claims") -> str:
    """Escalate a claim to a specialist team (vulnerability, complex claims, or complaints)."""
    claim = CLAIMS.get(claim_id.upper())
    if not claim:
        return f"Error: Claim '{claim_id}' not found."

    valid_teams = ["vulnerability", "complex_claims", "complaints", "senior_handler"]
    if team not in valid_teams:
        return f"Error: Invalid team '{team}'. Valid teams: {', '.join(valid_teams)}"

    team_labels = {
        "vulnerability": "Vulnerable Customer Support Team",
        "complex_claims": "Complex Claims Unit",
        "complaints": "Customer Complaints Team",
        "senior_handler": "Senior Claims Handler",
    }

    return (
        f"Claim escalated:\n"
        f"  Claim: {claim_id}\n"
        f"  Routed to: {team_labels[team]}\n"
        f"  Reason: {reason}\n"
        f"  The specialist team will contact the customer within "
        f"{'1 hour' if team == 'vulnerability' else '4 hours'}."
    )


def search_faq(query: str) -> str:
    """Search the Apex Motor Insurance knowledge base for answers to common questions."""
    query_lower = query.lower()
    scored = []
    for key, entry in FAQ_ENTRIES.items():
        score = sum(1 for kw in entry["keywords"] if kw in query_lower)
        if score > 0:
            scored.append((score, entry))

    if not scored:
        return "No FAQ results found. The customer's question may need to be handled by a specialist."

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:2]
    results = []
    for _, entry in top:
        results.append(f"Q: {entry['question']}\nA: {entry['answer']}")
    return "\n\n".join(results)


# ── Failure Injection ─────────────────────────────────────────────────────────

FAILURE_MODES = {
    "service_unavailable": "Error: Claims system temporarily unavailable. Please try again later.",
    "timeout": "Error: Request timed out after 30 seconds. The claims database may be experiencing high load.",
    "server_error": "Error: Internal server error (500). An unexpected error occurred in the claims system.",
    "permission_denied": "Error: Access denied. Your session has expired — please re-authenticate.",
}


def inject_failure(tool_name: str, failure_config: dict) -> str | None:
    """Check if a tool should fail based on the failure config."""
    failure_mode = failure_config.get(tool_name)
    if failure_mode and failure_mode in FAILURE_MODES:
        return FAILURE_MODES[failure_mode]
    return None


# ── Tool Registry ─────────────────────────────────────────────────────────────

TOOLS = {
    "lookup_claim": {
        "function": lookup_claim,
        "description": "Look up a motor insurance claim by its ID. Returns claimant, incident details, damage, estimated value, and documents received.",
        "parameters": {"claim_id": "The claim ID (e.g. CLM-2026-0041)"},
    },
    "check_policy_cover": {
        "function": check_policy_cover,
        "description": "Check a policy's status, cover type, named drivers, excess, and no-claims bonus.",
        "parameters": {"policy_id": "The policy ID (e.g. APX-100201)"},
    },
    "approve_settlement": {
        "function": approve_settlement,
        "description": "Approve a claims settlement. Requires claim ID, amount, settlement type (repair/cash_settlement/total_loss/windscreen_repair/windscreen_replacement), and reason.",
        "parameters": {
            "claim_id": "The claim ID",
            "amount": "Settlement amount in GBP (number)",
            "settlement_type": "Type: repair, cash_settlement, total_loss, windscreen_repair, or windscreen_replacement",
            "reason": "Justification for the settlement",
        },
    },
    "flag_for_investigation": {
        "function": flag_for_investigation,
        "description": "Flag a claim to the Special Investigations Unit (SIU) for potential fraud. Include the fraud indicators observed.",
        "parameters": {
            "claim_id": "The claim ID",
            "indicators": "Description of fraud indicators observed",
            "urgency": "Urgency level: 'standard' or 'urgent' (optional, defaults to standard)",
        },
    },
    "escalate_to_specialist": {
        "function": escalate_to_specialist,
        "description": "Escalate a claim to a specialist team for handling. Use for vulnerable customers, complex claims, complaints, or cases exceeding settlement authority.",
        "parameters": {
            "claim_id": "The claim ID",
            "reason": "Why this claim needs specialist handling",
            "team": "Team: vulnerability, complex_claims, complaints, or senior_handler (optional, defaults to complex_claims)",
        },
    },
    "search_faq": {
        "function": search_faq,
        "description": "Search the Apex Motor Insurance knowledge base for answers about excess, courtesy cars, claim timelines, write-offs, NCB, approved repairers, police reports, and uninsured drivers.",
        "parameters": {"query": "The customer's question or keywords to search for"},
    },
}


# ── Domain metadata (used by domain loader) ──────────────────────────────────

DOMAIN_META = {
    "name": "Apex Motor Insurance",
    "tagline": "UK motor insurer — claims FNOL agent",
    "description": (
        "Apex Motor Insurance is a fictional mid-tier UK direct motor insurer. "
        "The claims FNOL agent handles first notification of loss for collision, theft, "
        "vandalism, and windscreen claims. FCA Consumer Duty regulated with fraud detection "
        "and vulnerable customer obligations."
    ),
    "stakes": "High — regulated financial services (FCA, fraud, vulnerable customers)",
    "colour": "#1a3a5c",  # Navy blue — insurance/finance
    "company_context": (
        "Mid-tier UK direct motor insurer based in Birmingham. 200,000 policyholders. "
        "FCA Consumer Duty regulated. Claims handled via FNOL process: notification → triage → "
        "validation → assessment → settlement. Special Investigations Unit (SIU) handles fraud. "
        "Vulnerable Customer Support Team handles customers showing vulnerability indicators. "
        "Average motor claim: £4,900. Motor fraud costs the industry £576M annually."
    ),
    "agent_role": (
        "Claims FNOL agent handling first notification of loss. Registers new claims, validates "
        "policy cover, triages by claim type, checks for fraud indicators and vulnerability cues, "
        "and approves straightforward settlements within authority limits."
    ),
    "hard_guardrail_name": "Settlement authority limit (£2,500 max)",
    "hard_guardrail_description": (
        "Settlements over £2,500 are automatically blocked and escalated to a senior claims handler. "
        "This is a code-level guardrail the agent cannot override. The average motor claim is £4,900, "
        "so most non-trivial claims will hit this limit."
    ),
}
