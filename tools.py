"""
Tools for the Oakwood Home & Garden customer service agent.

Each tool is a plain Python function that takes parameters and returns a string.
The agent calls these tools during its reasoning loop.

Mock data simulates a real order database and refund policy system.
"""

# ── Mock Data ──────────────────────────────────────────────────────────────────

ORDERS = {
    "ORD-001": {
        "order_id": "ORD-001",
        "customer": "Sarah Mitchell",
        "email": "sarah.mitchell@email.com",
        "item": "Willow Garden Trowel Set",
        "price": 18.99,
        "order_date": "2026-02-15",
        "delivery_date": "2026-02-18",
        "status": "delivered",
        "category": "hand-tools",
    },
    "ORD-002": {
        "order_id": "ORD-002",
        "customer": "James Thornton",
        "email": "j.thornton@email.com",
        "item": "Cedar Raised Bed Kit (1.2m)",
        "price": 89.99,
        "order_date": "2026-01-20",
        "delivery_date": "2026-01-25",
        "status": "delivered",
        "category": "garden-structures",
    },
    "ORD-003": {
        "order_id": "ORD-003",
        "customer": "Emily Watson",
        "email": "emily.w@email.com",
        "item": "Heritage Seed Collection — Spring Vegetables",
        "price": 12.50,
        "order_date": "2026-02-28",
        "delivery_date": "2026-03-02",
        "status": "delivered",
        "category": "seeds",
    },
    "ORD-004": {
        "order_id": "ORD-004",
        "customer": "David Chen",
        "email": "d.chen@email.com",
        "item": "Oakwood Premium BBQ — The Pitmaster 600",
        "price": 450.00,
        "order_date": "2026-01-05",
        "delivery_date": "2026-01-10",
        "status": "delivered",
        "category": "outdoor-cooking",
    },
    "ORD-005": {
        "order_id": "ORD-005",
        "customer": "Rachel Adams",
        "email": "rachel.a@email.com",
        "item": "Cast Iron Fire Pit — Cotswold Large",
        "price": 175.00,
        "order_date": "2026-01-28",
        "delivery_date": "2026-02-01",
        "status": "delivered",
        "category": "outdoor-heating",
    },
    "ORD-006": {
        "order_id": "ORD-006",
        "customer": "Tom Bradley",
        "email": "tom.b@email.com",
        "item": "Bamboo Wind Chime — Large",
        "price": 24.99,
        "order_date": "2026-02-20",
        "delivery_date": "2026-02-23",
        "status": "delivered",
        "category": "garden-decor",
    },
    "ORD-007": {
        "order_id": "ORD-007",
        "customer": "Lisa Park",
        "email": "lisa.park@email.com",
        "item": "Professional Secateurs — Bypass",
        "price": 34.99,
        "order_date": "2026-02-25",
        "delivery_date": "2026-02-27",
        "status": "delivered",
        "category": "hand-tools",
    },
    "ORD-008": {
        "order_id": "ORD-008",
        "customer": "Mark Stevens",
        "email": "m.stevens@email.com",
        "item": "Solar Path Lights (Pack of 8)",
        "price": 45.99,
        "order_date": "2026-02-10",
        "delivery_date": "2026-02-14",
        "status": "delivered",
        "category": "lighting",
    },
    "ORD-009": {
        "order_id": "ORD-009",
        "customer": "Helen Wright",
        "email": "h.wright@email.com",
        "item": "Gardener's Knee Pad — Memory Foam",
        "price": 8.99,
        "order_date": "2026-03-01",
        "delivery_date": "2026-03-03",
        "status": "delivered",
        "category": "accessories",
    },
    "ORD-010": {
        "order_id": "ORD-010",
        "customer": "Alex Morgan",
        "email": "a.morgan@email.com",
        "item": "Wooden Compost Bin — 400L",
        "price": 64.99,
        "order_date": "2026-02-05",
        "delivery_date": "2026-02-08",
        "status": "delivered",
        "category": "composting",
    },
}

REFUND_POLICIES = {
    "hand-tools": {
        "category": "hand-tools",
        "refund_window_days": 30,
        "condition": "unused, in original packaging",
        "notes": "Sharpened or visibly used tools cannot be refunded.",
    },
    "garden-structures": {
        "category": "garden-structures",
        "refund_window_days": 14,
        "condition": "unassembled, in original packaging",
        "notes": "Assembled items cannot be returned. Faulty items covered under manufacturer warranty (12 months).",
    },
    "seeds": {
        "category": "seeds",
        "refund_window_days": 14,
        "condition": "unopened packets only",
        "notes": "Opened seed packets cannot be refunded due to contamination risk. Germination is not guaranteed.",
    },
    "outdoor-cooking": {
        "category": "outdoor-cooking",
        "refund_window_days": 30,
        "condition": "unused, in original packaging",
        "notes": "Used BBQs cannot be refunded. Faulty units covered under manufacturer warranty (24 months).",
    },
    "outdoor-heating": {
        "category": "outdoor-heating",
        "refund_window_days": 30,
        "condition": "unused, in original packaging, no fire damage",
        "notes": "Items showing signs of use (soot, ash) are not eligible. Faulty items: contact manufacturer.",
    },
    "garden-decor": {
        "category": "garden-decor",
        "refund_window_days": 30,
        "condition": "undamaged, in original packaging",
        "notes": "Personalised items are non-refundable.",
    },
    "lighting": {
        "category": "lighting",
        "refund_window_days": 30,
        "condition": "unused, in original packaging",
        "notes": "Solar items must include all original components. Battery issues covered under warranty.",
    },
    "accessories": {
        "category": "accessories",
        "refund_window_days": 14,
        "condition": "unused, in original packaging",
        "notes": "Hygiene items (knee pads, gloves) cannot be returned once used.",
    },
    "composting": {
        "category": "composting",
        "refund_window_days": 14,
        "condition": "unassembled, in original packaging",
        "notes": "Assembled bins cannot be returned. Missing parts replaced free of charge.",
    },
}

# ── Hard guardrail: max auto-refund amount ─────────────────────────────────────

MAX_AUTO_REFUND = 50.00  # £50 — amounts above this require human approval


# ── Tool Functions ─────────────────────────────────────────────────────────────

def lookup_order(order_id: str) -> str:
    """Look up an order by its ID. Returns order details or an error."""
    order = ORDERS.get(order_id.upper())
    if not order:
        return f"Error: Order '{order_id}' not found. Please check the order ID and try again."
    return (
        f"Order {order['order_id']}:\n"
        f"  Customer: {order['customer']}\n"
        f"  Email: {order['email']}\n"
        f"  Item: {order['item']}\n"
        f"  Price: £{order['price']:.2f}\n"
        f"  Ordered: {order['order_date']}\n"
        f"  Delivered: {order['delivery_date']}\n"
        f"  Status: {order['status']}\n"
        f"  Category: {order['category']}"
    )


def check_refund_policy(category: str) -> str:
    """Check the refund policy for a product category."""
    policy = REFUND_POLICIES.get(category.lower())
    if not policy:
        return f"Error: No refund policy found for category '{category}'."
    return (
        f"Refund Policy — {policy['category']}:\n"
        f"  Window: {policy['refund_window_days']} days from delivery\n"
        f"  Condition: {policy['condition']}\n"
        f"  Notes: {policy['notes']}"
    )


def issue_refund(order_id: str, amount: float, reason: str, guardrails_enabled: bool = True) -> str:
    """
    Issue a refund for an order.

    HARD GUARDRAIL: If guardrails are enabled and amount > £50,
    the refund is blocked and must be escalated to a human.
    """
    amount = float(amount)
    order = ORDERS.get(order_id.upper())
    if not order:
        return f"Error: Order '{order_id}' not found."

    if guardrails_enabled and amount > MAX_AUTO_REFUND:
        return (
            f"BLOCKED: Refund of £{amount:.2f} exceeds the automatic refund limit "
            f"of £{MAX_AUTO_REFUND:.2f}. This refund requires manager approval. "
            f"Please escalate to a human agent."
        )

    return (
        f"Refund processed successfully:\n"
        f"  Order: {order_id}\n"
        f"  Amount: £{amount:.2f}\n"
        f"  Reason: {reason}\n"
        f"  Refund will appear on the customer's statement within 5-7 working days."
    )


def send_customer_email(email: str, subject: str, body: str) -> str:
    """Send an email to a customer. (Simulated — does not actually send.)"""
    return (
        f"Email sent successfully:\n"
        f"  To: {email}\n"
        f"  Subject: {subject}\n"
        f"  Body preview: {body[:100]}..."
    )


def escalate_to_human(order_id: str, reason: str, priority: str = "normal") -> str:
    """Escalate a case to a human agent."""
    return (
        f"Case escalated:\n"
        f"  Order: {order_id}\n"
        f"  Priority: {priority}\n"
        f"  Reason: {reason}\n"
        f"  A human agent will review this case within "
        f"{'1 hour' if priority == 'high' else '4 hours'}."
    )


# ── FAQ Knowledge Base (simulated RAG) ────────────────────────────────────────

FAQ_ENTRIES = {
    "delivery": {
        "question": "How long does delivery take?",
        "answer": "Standard delivery is 3-5 working days. Express delivery (next working day) is available for £5.99. Free delivery on orders over £50. We deliver Monday to Saturday.",
        "keywords": ["delivery", "shipping", "dispatch", "arrive", "how long"],
    },
    "returns": {
        "question": "How do I return an item?",
        "answer": "Contact us with your order number and we'll arrange a return. Items must be in original packaging and unused. Return postage is free for faulty items. For change-of-mind returns, a £3.99 return label is deducted from your refund.",
        "keywords": ["return", "send back", "return label", "how to return"],
    },
    "payment": {
        "question": "What payment methods do you accept?",
        "answer": "We accept Visa, Mastercard, American Express, PayPal, and Apple Pay. All payments are processed securely. We do not accept cheques or bank transfers.",
        "keywords": ["payment", "pay", "card", "paypal", "visa", "mastercard"],
    },
    "gift_wrapping": {
        "question": "Do you offer gift wrapping?",
        "answer": "Yes! Gift wrapping is available for £2.99 per item. Select the gift wrap option at checkout. We'll include a printed message card with your personal note.",
        "keywords": ["gift", "wrapping", "wrap", "present"],
    },
    "store_locations": {
        "question": "Do you have physical stores?",
        "answer": "Oakwood Home & Garden is an online-only retailer. We don't have physical stores, but we do have a showroom in Cirencester, Gloucestershire open Thursday to Saturday, 10am-4pm.",
        "keywords": ["store", "shop", "location", "visit", "showroom", "physical"],
    },
    "warranty": {
        "question": "What warranty do your products have?",
        "answer": "All Oakwood-branded products carry a 12-month warranty against manufacturing defects. Third-party products carry the manufacturer's warranty (check product listing for details). Warranty does not cover normal wear and tear.",
        "keywords": ["warranty", "guarantee", "defect", "faulty", "broken"],
    },
    "opening_hours": {
        "question": "What are your customer service hours?",
        "answer": "Our customer service team is available Monday to Friday, 9am-5:30pm, and Saturday 9am-1pm. We're closed on Sundays and bank holidays. Live chat is available during these hours.",
        "keywords": ["hours", "open", "available", "contact", "when", "chat"],
    },
    "bulk_orders": {
        "question": "Do you offer trade or bulk discounts?",
        "answer": "Yes, we offer trade accounts for businesses and landscapers. Orders over £500 qualify for a 10% trade discount. Contact trade@oakwoodhg.co.uk to set up an account.",
        "keywords": ["bulk", "trade", "discount", "wholesale", "business", "landscaper"],
    },
}


def search_faq(query: str) -> str:
    """Search the company knowledge base for answers to common questions."""
    query_lower = query.lower()
    scored = []
    for key, entry in FAQ_ENTRIES.items():
        score = sum(1 for kw in entry["keywords"] if kw in query_lower)
        if score > 0:
            scored.append((score, entry))

    if not scored:
        return "No FAQ results found. The customer's question may need to be handled by a human agent."

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
            e.g. {"lookup_order": "service_unavailable", "issue_refund": "timeout"}

    Returns:
        Error string if the tool should fail, None if it should work normally.
    """
    failure_mode = failure_config.get(tool_name)
    if failure_mode and failure_mode in FAILURE_MODES:
        return FAILURE_MODES[failure_mode]
    return None


# ── Tool registry (used by the agent to know what's available) ─────────────────

TOOLS = {
    "lookup_order": {
        "function": lookup_order,
        "description": "Look up an order by its ID. Returns customer name, item, price, dates, and status.",
        "parameters": {"order_id": "The order ID (e.g. ORD-001)"},
    },
    "check_refund_policy": {
        "function": check_refund_policy,
        "description": "Check the refund policy for a product category. Returns refund window, conditions, and notes.",
        "parameters": {"category": "Product category (e.g. hand-tools, seeds, outdoor-cooking)"},
    },
    "issue_refund": {
        "function": issue_refund,
        "description": "Issue a refund for an order. Requires order ID, amount, and reason.",
        "parameters": {
            "order_id": "The order ID",
            "amount": "Refund amount in GBP (number)",
            "reason": "Reason for the refund",
        },
    },
    "send_customer_email": {
        "function": send_customer_email,
        "description": "Send an email to a customer with a subject and body.",
        "parameters": {
            "email": "Customer's email address",
            "subject": "Email subject line",
            "body": "Email body text",
        },
    },
    "escalate_to_human": {
        "function": escalate_to_human,
        "description": "Escalate a case to a human agent for review.",
        "parameters": {
            "order_id": "The order ID",
            "reason": "Why this case needs human attention",
            "priority": "Priority level: 'normal' or 'high' (optional, defaults to normal)",
        },
    },
    "search_faq": {
        "function": search_faq,
        "description": "Search the company knowledge base for answers to common questions about delivery, returns, payments, warranties, and store information.",
        "parameters": {"query": "The customer's question or keywords to search for"},
    },
}
