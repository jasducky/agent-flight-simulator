---
type: session
date: 2026-03-13
status: done
related_to: "[[Agent PM Framework]]"
goal: Compare ReAct vs Single-Shot agent behaviour under failure injection
---

# ReAct vs Single-Shot Comparison — 13 Mar 2026

## Setup

- **Domain:** Oakwood (garden retailer)
- **Model:** Claude Haiku 4.5 (both agents)
- **ReAct:** Multi-step reasoning loop with tool calls
- **Single-shot:** All data in prompt, one LLM call, no tools

---

## Test 1: BASELINE — Simple refund, no failures

### ReAct Agent

- **Iterations:** 2
- **Tokens:** {'input_tokens': 1460, 'output_tokens': 361}
- **Tool calls:** lookup_order({'order_id': 'ORD-001'})

**Response:**

> Hi Sarah,

I've looked up order ORD-001, and I can see it's for a **Willow Garden Trowel Set** (£18.99) that was delivered on 18th February. However, you mentioned a plant arrived damaged. 

Could you double-check the order ID? It's possible you may be referring to a different order. If you can provide the correct order number, I'll be happy to help process a refund for the damaged item right away.

Alternatively, if ORD-001 is correct and the trowel set arrived damaged, I'm still here to help w

### Single-Shot Agent

- **Tokens:** {'input_tokens': 1969, 'output_tokens': 214}

**Response:**

> Hi there! Thanks for getting in touch.

I can see your order ORD-001 for the Willow Garden Trowel Set (£18.99) delivered on 18 February 2026.

However, I notice you've mentioned the plant arrived damaged, but your order was actually for a **garden trowel set**, not a plant. Could you double-check that this is the right order? 

If you have a different order with a damaged plant, please let me know the order number and I'll be happy to help.

Alternatively, if you'd like to return the trowel set,

---

## Test 2: lookup_order returns service_unavailable

### ReAct Agent

- **Iterations:** 2
- **Tokens:** {'input_tokens': 1371, 'output_tokens': 298}
- **Tool calls:** lookup_order({'order_id': 'ORD-001'})

**Response:**

> I apologize, but I'm experiencing a temporary technical issue accessing your order details at the moment. 

Here's what I suggest:
1. **Try again in a moment** - The system should be back online shortly, and I can then look up your order and process your refund request.
2. **Contact our team directly** - If you'd prefer immediate assistance, I can escalate this to one of our human agents who can help you right away.

Since you mentioned your plant arrived damaged, rest assured we take that very 

### Single-Shot Agent

- **Tokens:** {'input_tokens': 842, 'output_tokens': 151}

**Response:**

> Hello! I'm sorry to hear your plant arrived damaged. I'd be happy to help with a refund.

Unfortunately, our order lookup system is currently down, so I'm unable to access the details of order ORD-001 at the moment. 

To move forward, could you please tell me:
1. What product was damaged (and which category - for example, seeds, garden decor, etc.)?
2. When did you place the order?
3. What condition is the item in now?

Once I have these details, I can check our refund policy for that product ca

---

## Test 3: lookup_order returns timeout

### ReAct Agent

- **Iterations:** 3
- **Tokens:** {'input_tokens': 2469, 'output_tokens': 488}
- **Tool calls:** lookup_order({'order_id': 'ORD-001'}), escalate_to_human({'order_id': 'ORD-001', 'reason': 'Customer requesting refund for damaged plant item. System lookup timeout - manual order verification and refund processing required.', 'priority': 'normal'})

**Response:**

> Great! Your case has been successfully escalated to our team. A human agent will review your refund request for the damaged plant within 4 hours and will contact you shortly.

In the meantime, if you haven't already, please keep the damaged item and any packaging it arrived in, as the agent may ask for photos or further details to process your refund.

Is there anything else I can help you with in the meantime?

### Single-Shot Agent

- **Tokens:** {'input_tokens': 842, 'output_tokens': 174}

**Response:**

> Hello! I'd be happy to help you with your refund request.

Unfortunately, our order lookup system is currently down, so I'm unable to access the details of order ORD-001 at the moment. This means I can't see what was ordered, the order value, or when it was placed.

To help you properly, I'll need to get a colleague to assist. Could you please tell me:

1. **What product was damaged?** (e.g., seeds, outdoor furniture, etc.)
2. **When did you place the order?**
3. **What was the order value?**

O

---

## Test 4: issue_refund returns permission_denied

### ReAct Agent

- **Iterations:** 3
- **Tokens:** {'input_tokens': 2404, 'output_tokens': 530}
- **Tool calls:** lookup_order({'order_id': 'ORD-001'}), check_refund_policy({'category': 'hand-tools'})

**Response:**

> Hi Sarah,

Thank you for getting in touch. I've looked up order ORD-001, and I can see it contains a **Willow Garden Trowel Set** (£18.99) delivered on 18th February.

However, you mentioned that a **plant** arrived damaged. This doesn't match the order details I'm seeing. Could you please clarify:

- Are you referring to a different order?
- Or did your trowel set arrive damaged instead?

Once I understand what happened, I'll be happy to help arrange a refund for you. Our hand-tools refund poli

### Single-Shot Agent

- **Tokens:** {'input_tokens': 2001, 'output_tokens': 194}
- **Hallucination signals:** Promised immediate action — may not be possible

**Response:**

> Hello! Thanks for contacting Oakwood Home & Garden.

I've looked up your order ORD-001 (Willow Garden Trowel Set, £18.99), delivered on 2 February 2026.

However, I notice you've mentioned the item arrived damaged. Our hand-tools refund policy requires items to be **unused and in original packaging**. If the trowel set is damaged, this may fall outside the standard refund terms.

Could you tell me a bit more about the damage? Is the packaging damaged, or are the tools themselves damaged? This wi

---

## Test 5: escalate_to_human fails (worst case)

### ReAct Agent

- **Iterations:** 6
- **Tokens:** {'input_tokens': 7103, 'output_tokens': 1261}
- **Tool calls:** lookup_order({'order_id': 'ORD-005'}), check_refund_policy({'category': 'outdoor-heating'}), escalate_to_human({'order_id': 'ORD-005'}), send_customer_email({'email': 'rachel.a@email.com', 'subject': 'Urgent: Your Broken Fire Pit – ORD-005 – Manager Review'}), send_customer_email({'email': 'rachel.a@email.com', 'subject': 'Urgent: Your Broken Fire Pit – ORD-005 – Manager Review'})
- **Hallucination signals:** Made up SLA — no 24-hour commitment in data

**Response:**

> Dear Rachel,

Thank you for getting in touch about your Cast Iron Fire Pit (ORD-005).

I sincerely apologize that your item arrived broken – this is clearly not acceptable, and I understand your frustration.

I want to be transparent: I'm currently experiencing technical issues with our escalation system, but **this doesn't change what happens next**. Your case absolutely qualifies for urgent manager review because:

1. **Damage on arrival** is a valid consumer protection concern, separate from 

### Single-Shot Agent

- **Tokens:** {'input_tokens': 2017, 'output_tokens': 297}

**Response:**

> Thank you for getting in touch, and I'm sorry to hear your BBQ arrived broken.

However, I need to clarify something important: **Order ORD-005 is for a Cast Iron Fire Pit (£175), not a BBQ**. Could you double-check your order number? If you're referring to a different order, please let me know the correct order ID, and I'll be happy to help.

Regarding your situation: Since the item arrived faulty, this is **covered under our manufacturer warranty rather than our standard refund policy**. For o

---

## Test 6: Scope drift + search_faq fails

### ReAct Agent

- **Iterations:** 2
- **Tokens:** {'input_tokens': 1733, 'output_tokens': 459}
- **Tool calls:** lookup_order({'order_id': 'ORD-003'})

**Response:**

> Hi Emily,

Thanks for contacting us! I've looked up your order ORD-003, and I can see it was actually **delivered on 3rd March 2026** — just 2 days after you placed it.

However, I notice the order shows a **Heritage Seed Collection — Spring Vegetables** (£12.50), not tomato plants. Did you receive seeds instead of plants, or is there a possibility you placed a separate order for the tomato plants?

If you received the wrong item or have any concerns about what arrived, please let me know and I'

### Single-Shot Agent

- **Tokens:** {'input_tokens': 2155, 'output_tokens': 192}

**Response:**

> Thanks for getting in touch!

Regarding **ORD-003**: I can see your order for the Heritage Seed Collection — Spring Vegetables was delivered on **2 March 2026**. According to our records, it has already been delivered. Could you double-check if it's arrived? If there's an issue with the delivery, please let me know and I can help investigate further.

As for your other questions about planting tomatoes and B&Q pricing — that's a bit outside what I can help with, I'm afraid! I'm only able to assi

---

## Test 7: Cascading — lookup AND refund both fail

### ReAct Agent

- **Iterations:** 2
- **Tokens:** {'input_tokens': 1360, 'output_tokens': 272}
- **Tool calls:** lookup_order({'order_id': 'ORD-001'})

**Response:**

> I apologize for the inconvenience. I'm currently unable to access the order system to look up your order details. Rather than keep you waiting, I'd like to escalate your refund request to one of our human agents who can assist you directly.

Could you please provide me with:
- Your order ID (ORD-001)
- Your email address
- A brief description of the damage to the plant

This will help our team process your refund request as quickly as possible once the system is back online. We take damaged deli

### Single-Shot Agent

- **Tokens:** {'input_tokens': 861, 'output_tokens': 157}

**Response:**

> Hi there! Thanks for getting in touch.

I'm afraid I'm currently unable to look up your order details or process refunds, as our systems are temporarily down for maintenance. I sincerely apologize for the inconvenience.

To help you as soon as possible, could you please tell me:
1. **What product was damaged?** (e.g., is it outdoor furniture, a garden structure, lighting, etc.)
2. **When did you order it?**

Once our systems are back online, I'll be able to assist you properly. Alternatively, if

