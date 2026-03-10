"""
Tools for the Hartwell & Lane lettings assistant agent.

Each tool is a plain Python function that takes parameters and returns a string.
The agent calls these tools during its reasoning loop.

Mock data simulates a real lettings agency database and tenant eligibility system.
"""

# -- Mock Data ----------------------------------------------------------------

PROPERTIES = {
    "PROP-001": {
        "property_id": "PROP-001",
        "address": "14 Riverside Walk, Millbrook, Bristol BS3 4PQ",
        "type": "flat",
        "bedrooms": 2,
        "rent_pcm": 1150,
        "deposit": 1150,
        "available_from": "2026-04-01",
        "status": "available",
        "features": ["pet-friendly", "parking", "balcony"],
        "epc_rating": "C",
        "area_info": "Millbrook is a residential area approximately 2 miles south of Bristol city centre, served by regular bus routes.",
        "dss_accepted": True,
    },
    "PROP-002": {
        "property_id": "PROP-002",
        "address": "Flat 3, 88 Queen Street, Coventry CV1 3EH",
        "type": "flat",
        "bedrooms": 1,
        "rent_pcm": 750,
        "deposit": 750,
        "available_from": "2026-03-15",
        "status": "available",
        "features": ["city centre", "furnished", "bike storage"],
        "epc_rating": "B",
        "area_info": "City centre location within walking distance of Coventry railway station and the Cathedral Quarter.",
        "dss_accepted": True,
    },
    "PROP-003": {
        "property_id": "PROP-003",
        "address": "27 Oakfield Road, Selly Oak, Birmingham B29 6BE",
        "type": "house",
        "bedrooms": 4,
        "rent_pcm": 1600,
        "deposit": 1600,
        "available_from": "2026-06-01",
        "status": "available",
        "features": ["garden", "garage", "unfurnished", "near university"],
        "epc_rating": "D",
        "area_info": "Selly Oak is a suburban area adjacent to the University of Birmingham campus, with local shops and transport links.",
        "dss_accepted": False,
    },
    "PROP-004": {
        "property_id": "PROP-004",
        "address": "Flat 12, Waterside Court, Leamington Spa CV32 5JN",
        "type": "flat",
        "bedrooms": 2,
        "rent_pcm": 950,
        "deposit": 950,
        "available_from": "2026-04-15",
        "status": "let agreed",
        "features": ["parking", "communal garden", "lift access"],
        "epc_rating": "B",
        "area_info": "Leamington Spa town centre location, close to the Parade and local amenities.",
        "dss_accepted": True,
    },
    "PROP-005": {
        "property_id": "PROP-005",
        "address": "9 Station Lane, Kenilworth CV8 1JD",
        "type": "house",
        "bedrooms": 3,
        "rent_pcm": 1400,
        "deposit": 1400,
        "available_from": "2026-05-01",
        "status": "available",
        "features": ["garden", "driveway", "pet-friendly", "unfurnished"],
        "epc_rating": "C",
        "area_info": "Kenilworth is a market town between Coventry and Warwick, with independent shops and a mainline rail station.",
        "dss_accepted": False,
    },
    "PROP-006": {
        "property_id": "PROP-006",
        "address": "Studio 4, The Maltings, Stratford-upon-Avon CV37 6BA",
        "type": "studio",
        "bedrooms": 0,
        "rent_pcm": 625,
        "deposit": 625,
        "available_from": "2026-03-20",
        "status": "available",
        "features": ["furnished", "bills included", "city centre"],
        "epc_rating": "C",
        "area_info": "Central Stratford-upon-Avon location near the waterfront and town centre shops.",
        "dss_accepted": True,
    },
    "PROP-007": {
        "property_id": "PROP-007",
        "address": "2A Priory Gardens, Rugby CV21 3RW",
        "type": "maisonette",
        "bedrooms": 2,
        "rent_pcm": 825,
        "deposit": 825,
        "available_from": "2026-04-01",
        "status": "under offer",
        "features": ["private entrance", "garden", "parking"],
        "epc_rating": "D",
        "area_info": "Priory Gardens is a residential street approximately half a mile from Rugby town centre.",
        "dss_accepted": True,
    },
    "PROP-008": {
        "property_id": "PROP-008",
        "address": "Flat 1, 45 Earlsdon Avenue, Coventry CV5 6GH",
        "type": "flat",
        "bedrooms": 2,
        "rent_pcm": 895,
        "deposit": 895,
        "available_from": "2026-04-10",
        "status": "available",
        "features": ["garden access", "unfurnished", "pet-friendly", "period features"],
        "epc_rating": "D",
        "area_info": "Earlsdon is a residential area with independent shops, cafes, and good bus links to Coventry city centre.",
        "dss_accepted": False,
    },
    "PROP-009": {
        "property_id": "PROP-009",
        "address": "17 Harborne Road, Edgbaston, Birmingham B15 3AA",
        "type": "flat",
        "bedrooms": 1,
        "rent_pcm": 850,
        "deposit": 850,
        "available_from": "2026-03-25",
        "status": "available",
        "features": ["furnished", "parking", "near hospital"],
        "epc_rating": "B",
        "area_info": "Edgbaston is a suburban area close to the Queen Elizabeth Hospital and University of Birmingham.",
        "dss_accepted": False,
    },
}

TENANT_CRITERIA = {
    "standard": {
        "category": "standard",
        "requirements": [
            "Annual income of at least 3x the annual rent (e.g. £30,000 for £833/month rent)",
            "Satisfactory credit check",
            "Two years of address history",
            "Right-to-rent documentation (passport or share code)",
        ],
        "documents_needed": [
            "Photo ID (passport or driving licence)",
            "Proof of income (3 months payslips or tax return)",
            "Bank statements (3 months)",
            "Previous landlord reference",
        ],
        "notes": "All adult occupants must pass referencing. Joint tenants are jointly and severally liable.",
    },
    "student": {
        "category": "student",
        "requirements": [
            "UK-based guarantor with income of at least 3x the annual rent",
            "University enrolment confirmation letter",
            "Right-to-rent documentation",
        ],
        "documents_needed": [
            "Photo ID",
            "University enrolment letter (current academic year)",
            "Guarantor's photo ID and proof of income",
            "Guarantor's signed guarantor agreement",
        ],
        "notes": "Guarantor must be a UK homeowner. International students need a UK-based guarantor or can pay 6 months rent in advance.",
    },
    "professional": {
        "category": "professional",
        "requirements": [
            "Employer reference confirming role and salary",
            "Minimum 6-month tenancy",
            "Satisfactory credit check",
            "Right-to-rent documentation",
        ],
        "documents_needed": [
            "Photo ID",
            "Employment contract or offer letter",
            "Employer reference (on company letterhead)",
            "3 months bank statements",
        ],
        "notes": "Probationary employees may need a guarantor. Self-employed applicants need 2 years of accounts or SA302.",
    },
    "dss_accepted": {
        "category": "dss_accepted",
        "requirements": [
            "Housing benefit or Universal Credit housing element confirmation",
            "Top-up payments may be required if benefit does not cover full rent",
            "Satisfactory credit check",
            "Right-to-rent documentation",
        ],
        "documents_needed": [
            "Photo ID",
            "Benefits entitlement letter (dated within 3 months)",
            "Bank statements (3 months)",
            "Previous landlord reference (if applicable)",
        ],
        "notes": "Acceptance is per-property — check individual listings. Blanket 'No DSS' policies are unlawful. Landlords may request a guarantor.",
    },
    "pet_policy": {
        "category": "pet_policy",
        "requirements": [
            "Property must be listed as pet-friendly",
            "Written pet request submitted with application",
            "Landlord consent required (cannot be unreasonably withheld under Tenant Fees Act 2019 / Renters Reform)",
        ],
        "documents_needed": [
            "Pet description (type, breed, size)",
            "Vaccination records (dogs and cats)",
            "Pet insurance confirmation (recommended)",
        ],
        "notes": "Pet-friendly properties are marked in listings. Additional pet deposit is no longer permitted under the Tenant Fees Act 2019. Landlord may add reasonable pet clauses to the tenancy agreement.",
    },
}


# -- Tool Functions -----------------------------------------------------------

def search_properties(query: str) -> str:
    """Search available properties by keyword. Returns matching listings."""
    query_lower = query.lower()
    matches = []
    for prop_id, prop in PROPERTIES.items():
        searchable = " ".join([
            prop["address"].lower(),
            prop["type"].lower(),
            str(prop["bedrooms"]),
            " ".join(f.lower() for f in prop["features"]),
            prop["status"].lower(),
            f"£{prop['rent_pcm']}",
            prop["epc_rating"].lower(),
            "dss" if prop["dss_accepted"] else "",
            "housing benefit" if prop["dss_accepted"] else "",
        ])
        # Match any query word
        query_words = query_lower.split()
        if any(word in searchable for word in query_words):
            matches.append(prop)

    if not matches:
        return f"No properties found matching '{query}'. Try different search terms or contact our office for assistance."

    results = []
    for p in matches:
        status_note = f" [{p['status'].upper()}]" if p["status"] != "available" else ""
        pet_note = " | Pet-friendly" if "pet-friendly" in p["features"] else ""
        dss_note = " | DSS accepted" if p["dss_accepted"] else ""
        results.append(
            f"{p['property_id']}: {p['type'].title()}, {p['bedrooms']} bed — "
            f"£{p['rent_pcm']}/month\n"
            f"  {p['address']}{status_note}\n"
            f"  Features: {', '.join(p['features'])}{pet_note}{dss_note}\n"
            f"  Available: {p['available_from']} | EPC: {p['epc_rating']}"
        )
    return f"Found {len(matches)} matching properties:\n\n" + "\n\n".join(results)


def get_property_details(property_id: str) -> str:
    """Get full details for a specific property by ID."""
    prop = PROPERTIES.get(property_id.upper())
    if not prop:
        return f"Error: Property '{property_id}' not found. Please check the property ID and try again."
    # NOTE: area_info is deliberately factual — no demographic or subjective data
    return (
        f"Property {prop['property_id']}:\n"
        f"  Address: {prop['address']}\n"
        f"  Type: {prop['type'].title()}\n"
        f"  Bedrooms: {prop['bedrooms']}\n"
        f"  Rent: £{prop['rent_pcm']}/month\n"
        f"  Deposit: £{prop['deposit']}\n"
        f"  Available from: {prop['available_from']}\n"
        f"  Status: {prop['status']}\n"
        f"  Features: {', '.join(prop['features'])}\n"
        f"  EPC Rating: {prop['epc_rating']}\n"
        f"  Area: {prop['area_info']}\n"
        f"  DSS accepted: {'Yes' if prop['dss_accepted'] else 'No'}"
    )


def check_tenant_criteria(category: str) -> str:
    """Check tenant eligibility criteria for a given category."""
    criteria = TENANT_CRITERIA.get(category.lower())
    if not criteria:
        return f"Error: No criteria found for category '{category}'. Available categories: standard, student, professional, dss_accepted, pet_policy."
    return (
        f"Tenant Criteria — {criteria['category']}:\n"
        f"  Requirements:\n    - " + "\n    - ".join(criteria["requirements"]) + "\n"
        f"  Documents needed:\n    - " + "\n    - ".join(criteria["documents_needed"]) + "\n"
        f"  Notes: {criteria['notes']}"
    )


def book_viewing(property_id: str, name: str, email: str, preferred_date: str) -> str:
    """Book a viewing for a property. (Simulated — does not actually book.)"""
    prop = PROPERTIES.get(property_id.upper())
    if not prop:
        return f"Error: Property '{property_id}' not found."
    if prop["status"] == "let agreed":
        return (
            f"Sorry — {property_id} ({prop['address']}) is now let agreed and no longer "
            f"available for viewings. Would you like to see similar properties?"
        )
    return (
        f"Viewing booked successfully:\n"
        f"  Property: {prop['property_id']} — {prop['address']}\n"
        f"  Tenant: {name} ({email})\n"
        f"  Requested date: {preferred_date}\n"
        f"  A Hartwell & Lane agent will confirm the viewing time within 24 hours."
    )


def escalate_to_agent(property_id: str, reason: str, priority: str = "normal") -> str:
    """Escalate a case to a human estate agent."""
    return (
        f"Case escalated:\n"
        f"  Property: {property_id}\n"
        f"  Priority: {priority}\n"
        f"  Reason: {reason}\n"
        f"  A Hartwell & Lane agent will respond within "
        f"{'30 minutes' if priority == 'emergency' else '1 hour' if priority == 'high' else '4 hours'}."
    )


# -- FAQ Knowledge Base (simulated RAG) --------------------------------------

FAQ_ENTRIES = {
    "viewing": {
        "question": "How do I book a viewing?",
        "answer": "You can book a viewing through our website, by calling 01926 555 100, or by asking our online assistant. We offer daytime, evening, and weekend viewings. All viewings are accompanied by a Hartwell & Lane agent.",
        "keywords": ["viewing", "book", "visit", "see", "appointment", "look around"],
    },
    "application": {
        "question": "What is the application process?",
        "answer": "Once you've found a property, you submit a holding deposit (equivalent to one week's rent, max £350) to reserve it. We then carry out referencing through our partner agency, which takes 3-5 working days. You'll need photo ID, proof of income, and a previous landlord reference. Once approved, we prepare the tenancy agreement for signing.",
        "keywords": ["application", "apply", "process", "how to rent", "referencing", "reference"],
    },
    "deposit_protection": {
        "question": "How is my deposit protected?",
        "answer": "All deposits are protected in a government-approved tenancy deposit scheme (TDS, DPS, or MyDeposits) within 30 days of receipt. You'll receive a certificate confirming protection. At the end of your tenancy, the deposit is returned within 10 working days, subject to any agreed deductions for damage beyond fair wear and tear.",
        "keywords": ["deposit", "protection", "scheme", "TDS", "DPS", "security"],
    },
    "maintenance": {
        "question": "How do I report a maintenance issue?",
        "answer": "Report maintenance issues through our tenant portal at tenants.hartwellandlane.co.uk, by calling 01926 555 100, or by emailing maintenance@hartwellandlane.co.uk. Emergency issues (gas leaks, flooding, no heating in winter) should be reported immediately by phone. We aim to respond within 24 hours for routine issues and within 2 hours for emergencies.",
        "keywords": ["maintenance", "repair", "broken", "fix", "issue", "emergency", "gas", "leak", "heating"],
    },
    "tenancy_agreement": {
        "question": "What type of tenancy agreement do you use?",
        "answer": "We use Assured Shorthold Tenancy (AST) agreements, typically for 12 months with a 6-month break clause. The agreement is based on the ARLA Propertymark template. You'll receive a draft to review before signing. We also provide the government's 'How to Rent' guide as required by law.",
        "keywords": ["tenancy", "agreement", "contract", "AST", "term", "length", "break clause"],
    },
    "council_tax": {
        "question": "Who pays council tax?",
        "answer": "Tenants are responsible for council tax from the start date of their tenancy. You must register with the local council within 2 weeks of moving in. Students in full-time education may be exempt — contact your local council for details. Council tax band information is available on the Valuation Office Agency website.",
        "keywords": ["council tax", "tax", "council", "bills", "who pays"],
    },
    "moving_in": {
        "question": "What do I need to do when I move in?",
        "answer": "Before moving in: set up a standing order for rent, arrange contents insurance (recommended), take meter readings, and register for council tax. On move-in day: attend a check-in appointment where we'll walk through the inventory and hand over keys. Take dated photos of the property's condition for your own records.",
        "keywords": ["moving in", "move in", "checklist", "keys", "start", "begin"],
    },
    "ending_tenancy": {
        "question": "How do I end my tenancy?",
        "answer": "Give written notice as specified in your tenancy agreement (usually 2 months for the landlord, 1 month for the tenant after the fixed term). We'll arrange a check-out inspection and compare the property against the move-in inventory. Your deposit will be returned within 10 working days, minus any agreed deductions. Professional cleaning is usually required — check your tenancy agreement.",
        "keywords": ["end", "leave", "notice", "move out", "terminate", "ending"],
    },
}


def search_faq(query: str) -> str:
    """Search the company knowledge base for answers to common lettings questions."""
    query_lower = query.lower()
    scored = []
    for key, entry in FAQ_ENTRIES.items():
        score = sum(1 for kw in entry["keywords"] if kw in query_lower)
        if score > 0:
            scored.append((score, entry))

    if not scored:
        return "No FAQ results found. The enquiry may need to be handled by a Hartwell & Lane agent."

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:2]  # Return top 2 matches
    results = []
    for _, entry in top:
        results.append(f"Q: {entry['question']}\nA: {entry['answer']}")
    return "\n\n".join(results)


# -- Failure Injection (chaos testing for agents) ----------------------------

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
            e.g. {"search_properties": "service_unavailable", "book_viewing": "timeout"}

    Returns:
        Error string if the tool should fail, None if it should work normally.
    """
    failure_mode = failure_config.get(tool_name)
    if failure_mode and failure_mode in FAILURE_MODES:
        return FAILURE_MODES[failure_mode]
    return None


# -- Tool registry (used by the agent to know what's available) ---------------

TOOLS = {
    "search_properties": {
        "function": search_properties,
        "description": "Search available rental properties by keyword (location, type, bedrooms, features, budget). Returns matching listings with key details.",
        "parameters": {"query": "Search terms (e.g. '2 bed flat pet-friendly', 'Coventry', 'under 900')"},
    },
    "get_property_details": {
        "function": get_property_details,
        "description": "Get full details for a specific property by its ID. Returns address, rent, features, EPC rating, and area information.",
        "parameters": {"property_id": "The property ID (e.g. PROP-001)"},
    },
    "check_tenant_criteria": {
        "function": check_tenant_criteria,
        "description": "Check tenant eligibility requirements for a category. Returns income requirements, documents needed, and notes.",
        "parameters": {"category": "Criteria category (standard, student, professional, dss_accepted, pet_policy)"},
    },
    "book_viewing": {
        "function": book_viewing,
        "description": "Book a viewing for a specific property. Requires tenant name, email, and preferred date.",
        "parameters": {
            "property_id": "The property ID",
            "name": "Tenant's full name",
            "email": "Tenant's email address",
            "preferred_date": "Preferred viewing date (e.g. 2026-04-05)",
        },
    },
    "escalate_to_agent": {
        "function": escalate_to_agent,
        "description": "Escalate a case to a human Hartwell & Lane agent for review.",
        "parameters": {
            "property_id": "The property ID (or 'GENERAL' for non-property queries)",
            "reason": "Why this case needs human attention",
            "priority": "Priority level: 'normal', 'high', or 'emergency' (optional, defaults to normal)",
        },
    },
    "search_faq": {
        "function": search_faq,
        "description": "Search the Hartwell & Lane knowledge base for answers to common lettings questions about viewings, applications, deposits, maintenance, and tenancy agreements.",
        "parameters": {"query": "The tenant's question or keywords to search for"},
    },
}
