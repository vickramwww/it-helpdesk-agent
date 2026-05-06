"""
Mock tool implementations for the Order Management Triage Agent.

Tool names, input/output schemas, and mock data match architecture.md §3.
Real implementations would replace these bodies with live API/DB calls.
"""

import json
from datetime import datetime, timedelta
from difflib import SequenceMatcher

# ---------------------------------------------------------------------------
# Mock data
# ---------------------------------------------------------------------------

_now = datetime.utcnow()

MOCK_ORDERS: dict = {
    "ORD-001": {
        "order_id": "ORD-001",
        "customer_id": "CUST-100",
        "status": "in_transit",
        "locked": False,
        "carrier": "UPS",
        "tracking_number": "1Z999AA10123456784",
        "estimated_delivery": (_now + timedelta(days=2)).strftime("%Y-%m-%d"),
        "last_scan": f"Chicago hub, {_now.strftime('%Y-%m-%dT%H:%MZ')}",
        "cancellation_eligible": False,
        "fulfillment_started": True,
        "fraud_flag": False,
        "order_total": 1299.99,
        "items": [{"sku": "LAPTOP-PRO", "qty": 1, "price": 1299.99}],
        "created_at": (_now - timedelta(days=3)).isoformat(),
        "is_enterprise": False,
    },
    "ORD-002": {
        "order_id": "ORD-002",
        "customer_id": "CUST-101",
        "status": "stuck",
        "locked": False,
        "carrier": None,
        "tracking_number": None,
        "estimated_delivery": None,
        "last_scan": None,
        "cancellation_eligible": True,
        "fulfillment_started": False,
        "fraud_flag": False,
        "order_total": 29999.50,
        "items": [{"sku": "MONITOR-4K", "qty": 50, "price": 599.99}],
        "created_at": (_now - timedelta(hours=30)).isoformat(),
        "is_enterprise": True,
        "notes": "No status update for 30+ hours — potential P1.",
    },
    "ORD-003": {
        "order_id": "ORD-003",
        "customer_id": "CUST-102",
        "status": "delivered",
        "locked": True,
        "carrier": "UPS",
        "tracking_number": "1Z999AA10123456785",
        "estimated_delivery": (_now - timedelta(days=1)).strftime("%Y-%m-%d"),
        "last_scan": "Delivered — Front Door",
        "cancellation_eligible": False,
        "fulfillment_started": True,
        "fraud_flag": False,
        "order_total": 89.99,
        "items": [{"sku": "HEADPHONES-BT", "qty": 1, "price": 89.99}],
        "created_at": (_now - timedelta(days=7)).isoformat(),
        "is_enterprise": False,
    },
    "ORD-004": {
        "order_id": "ORD-004",
        "customer_id": "CUST-103",
        "status": "fraud_hold",
        "locked": True,
        "carrier": None,
        "tracking_number": None,
        "estimated_delivery": None,
        "last_scan": None,
        "cancellation_eligible": False,
        "fulfillment_started": False,
        "fraud_flag": True,
        "order_total": 2399.97,
        "items": [{"sku": "TABLET-PRO", "qty": 3, "price": 799.99}],
        "created_at": (_now - timedelta(hours=2)).isoformat(),
        "is_enterprise": False,
        "notes": "Risk engine flagged unusual pattern.",
    },
    "ORD-005": {
        "order_id": "ORD-005",
        "customer_id": "CUST-104",
        "status": "payment_captured_no_order",
        "locked": False,
        "carrier": None,
        "tracking_number": None,
        "estimated_delivery": None,
        "last_scan": None,
        "cancellation_eligible": False,
        "fulfillment_started": False,
        "fraud_flag": False,
        "order_total": 149.99,
        "items": [{"sku": "KEYBOARD-MECH", "qty": 1, "price": 149.99}],
        "created_at": (_now - timedelta(minutes=45)).isoformat(),
        "is_enterprise": False,
        "payment_captured": True,
        "order_created": False,
        "notes": "Revenue leak — payment taken, OMS failed to create order record.",
    },
}

MOCK_CUSTOMERS: dict = {
    "CUST-100": {
        "customer_id": "CUST-100",
        "tier": "standard",
        "fraud_flagged": False,
        "open_tickets_48h": 0,
        "recent_categories": [],
        "do_not_contact": False,
    },
    "CUST-101": {
        "customer_id": "CUST-101",
        "tier": "enterprise",
        "fraud_flagged": False,
        "open_tickets_48h": 0,
        "recent_categories": [],
        "do_not_contact": False,
    },
    "CUST-102": {
        "customer_id": "CUST-102",
        "tier": "standard",
        "fraud_flagged": False,
        "open_tickets_48h": 1,
        "recent_categories": ["return_refund"],
        "do_not_contact": False,
    },
    "CUST-103": {
        "customer_id": "CUST-103",
        "tier": "standard",
        "fraud_flagged": True,
        "open_tickets_48h": 0,
        "recent_categories": [],
        "do_not_contact": False,
    },
    "CUST-104": {
        "customer_id": "CUST-104",
        "tier": "standard",
        "fraud_flagged": False,
        "open_tickets_48h": 0,
        "recent_categories": [],
        "do_not_contact": False,
    },
    "CUST-200": {
        "customer_id": "CUST-200",
        "tier": "standard",
        "fraud_flagged": False,
        "open_tickets_48h": 3,
        "recent_categories": ["wismo", "wismo", "cancellation"],
        "do_not_contact": False,
    },
}

FAQ_ARTICLES: list[dict] = [
    {
        "id": "kb-001",
        "title": "How to track my order",
        "keywords": ["track", "tracking", "where is", "wismo", "status", "shipped", "delivery update"],
        "snippet": "Visit tracking.example.com and enter your order ID. Updates post every 4 hours.",
        "self_service": True,
    },
    {
        "id": "kb-002",
        "title": "Return and refund policy",
        "keywords": ["return", "refund", "send back", "exchange", "30 day", "policy", "money back"],
        "snippet": "30-day return window from delivery. Electronics must be unopened. Initiate at returns.example.com.",
        "self_service": True,
    },
    {
        "id": "kb-003",
        "title": "How to cancel an order",
        "keywords": ["cancel", "cancellation", "stop order", "don't want", "change my mind"],
        "snippet": "Orders can be cancelled within 2 hours if fulfillment has not begun. Use 'Cancel Order' in account portal.",
        "self_service": False,
    },
    {
        "id": "kb-004",
        "title": "Order confirmation email not received",
        "keywords": ["confirmation", "email", "receipt", "not received", "didn't get", "resend"],
        "snippet": "Confirmation emails send within 5 minutes. Check spam. Resend from account settings.",
        "self_service": True,
    },
    {
        "id": "kb-005",
        "title": "Shipping windows and estimated delivery",
        "keywords": ["shipping", "delivery", "how long", "when will", "estimated", "eta", "arrive"],
        "snippet": "Standard: 5-7 days. Express: 2-3 days. Overnight: next business day.",
        "self_service": True,
    },
    {
        "id": "kb-006",
        "title": "Promotional discount not applied",
        "keywords": ["promo", "discount", "coupon", "code", "not applied", "sale price", "promotion"],
        "snippet": "Verify: code is active, meets minimum, not expired, one per order. If valid — contact support with order ID.",
        "self_service": False,
    },
    {
        "id": "kb-007",
        "title": "Wrong item received",
        "keywords": ["wrong item", "incorrect", "not what i ordered", "wrong product", "different item"],
        "snippet": "Photograph the wrong item and submit via returns.example.com. Correct item ships with prepaid return label.",
        "self_service": False,
    },
    {
        "id": "kb-008",
        "title": "Subscription order management",
        "keywords": ["subscription", "recurring", "auto-renew", "skip", "pause", "frequency", "subscribe"],
        "snippet": "Manage at account.example.com/subscriptions. Changes apply next billing cycle.",
        "self_service": True,
    },
]


# ---------------------------------------------------------------------------
# Tool functions — names match architecture.md §3
# ---------------------------------------------------------------------------

def knowledge_lookup(query: str) -> dict:
    """Search FAQ/policy knowledge base. Returns top 3 matches with relevance scores."""
    query_lower = query.lower()
    matches = []

    for article in FAQ_ARTICLES:
        score = sum(1 for kw in article["keywords"] if kw in query_lower)
        title_sim = SequenceMatcher(None, query_lower, article["title"].lower()).ratio()
        total = score + title_sim * 2

        if total > 0.4:
            matches.append({"score": round(total, 2), "article": article})

    matches.sort(key=lambda x: x["score"], reverse=True)

    if not matches:
        return {"found": False, "message": "No matching knowledge base articles found."}

    return {
        "found": True,
        "matches": [
            {"id": m["article"]["id"], "title": m["article"]["title"],
             "snippet": m["article"]["snippet"], "score": m["score"]}
            for m in matches[:3]
        ],
    }


def order_lookup(order_id: str, customer_id: str) -> dict:
    """Fetch real-time order and carrier status from mock OMS."""
    order = MOCK_ORDERS.get(order_id.upper())

    if not order:
        return {"found": False, "message": f"Order {order_id} not found in OMS."}

    if order["customer_id"] != customer_id:
        return {
            "found": False,
            "message": "Order does not belong to this customer.",
            "security_flag": True,
        }

    return {"found": True, **order}


def check_customer(customer_id: str) -> dict:
    """Fetch customer profile, fraud flag, tier, and recent ticket history."""
    customer = MOCK_CUSTOMERS.get(customer_id)

    if not customer:
        return {
            "found": False,
            "customer_id": customer_id,
            "tier": "standard",
            "fraud_flagged": False,
            "open_tickets_48h": 0,
            "recent_categories": [],
            "do_not_contact": False,
        }

    return {"found": True, **customer}


# ---------------------------------------------------------------------------
# Tool definitions (JSON schema for Claude) — names match architecture.md §3
# ---------------------------------------------------------------------------

TOOL_DEFINITIONS: list[dict] = [
    {
        "name": "knowledge_lookup",
        "description": (
            "Search the order management knowledge base for return policies, shipping windows, "
            "and common procedures. Returns up to 3 matches with relevance scores. "
            "Use when the ticket looks FAQ-answerable."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural-language query derived from the ticket text.",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "order_lookup",
        "description": (
            "Look up an order's current status, tracking info, carrier, estimated delivery, "
            "fulfillment state, and fraud flag. Use when the ticket references a specific order ID."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "The order ID to look up (e.g. ORD-001)"},
                "customer_id": {"type": "string", "description": "Required for ownership verification."},
            },
            "required": ["order_id", "customer_id"],
        },
    },
    {
        "name": "check_customer",
        "description": (
            "Look up a customer's profile: fraud flag, tier, open ticket count in last 48h, "
            "and recent issue categories. Use to detect repeat escalations or fraud-flagged accounts."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string", "description": "The customer's ID"},
            },
            "required": ["customer_id"],
        },
    },
    {
        "name": "submit_triage_decision",
        "description": (
            "Final triage decision. Must be called exactly once to end the turn. "
            "Do not call any other tool after this."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": [
                        "wismo", "cancellation", "return_refund", "fraud",
                        "invoice", "subscription", "duplicate", "faq", "other",
                    ],
                    "description": "The primary issue category",
                },
                "priority": {
                    "type": "string",
                    "enum": ["P1", "P2", "P3", "P4"],
                    "description": "Ticket priority level",
                },
                "confidence": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": "Classification confidence between 0.0 and 1.0",
                },
                "action": {
                    "type": "string",
                    "enum": ["auto_resolve", "route"],
                    "description": "Action the agent takes on this ticket",
                },
                "auto_action": {
                    "type": "string",
                    "enum": [
                        "wismo_response", "send_tracking", "resend_confirmation",
                        "cancel_order", "merge_duplicate", "kb_reply",
                    ],
                    "description": "Specific auto-resolve action (required when action=auto_resolve)",
                },
                "route_to": {
                    "type": "string",
                    "enum": ["ops-l1", "ops-l2", "fraud-team", "legal-compliance", "triage-review"],
                    "description": "Destination queue (required when action=route)",
                },
                "reasoning": {
                    "type": "string",
                    "description": (
                        "1-3 sentences. Cite tool results used. "
                        "Mention any guardrail triggered."
                    ),
                },
                "guardrail_triggered": {
                    "type": "string",
                    "description": "Empty string if none. Otherwise name the specific guardrail rule.",
                },
            },
            "required": ["category", "priority", "confidence", "action", "reasoning", "guardrail_triggered"],
        },
    },
]


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

def execute_tool(name: str, inputs: dict) -> str:
    """Dispatch a tool call and return a JSON string result."""
    if name == "knowledge_lookup":
        result = knowledge_lookup(inputs["query"])
    elif name == "order_lookup":
        result = order_lookup(inputs["order_id"], inputs["customer_id"])
    elif name == "check_customer":
        result = check_customer(inputs["customer_id"])
    else:
        result = {"error": f"Unknown tool: {name}"}

    return json.dumps(result, default=str)


# ---------------------------------------------------------------------------
# Priority ticket queue — sorts P1 → P2 → P3 → P4, FIFO within each tier
# ---------------------------------------------------------------------------

PRIORITY_ORDER: dict[str, int] = {"P1": 0, "P2": 1, "P3": 2, "P4": 3}


class PriorityTicketQueue:
    """
    In-memory priority queue for triage results.

    Tickets are bucketed by priority tier (P1–P4). `dequeue` always
    returns from the highest-priority non-empty bucket; within a tier
    tickets are served first-in-first-out (arrival order).
    """

    def __init__(self) -> None:
        self._buckets: dict[str, list[dict]] = {"P1": [], "P2": [], "P3": [], "P4": []}

    def enqueue(self, ticket_id: str, priority: str, result: dict) -> None:
        tier = priority if priority in self._buckets else "P4"
        self._buckets[tier].append({"ticket_id": ticket_id, "priority": tier, "result": result})

    def dequeue(self) -> dict | None:
        """Return and remove the next highest-priority item, or None if empty."""
        for tier in sorted(self._buckets, key=lambda p: PRIORITY_ORDER[p]):
            if self._buckets[tier]:
                return self._buckets[tier].pop(0)
        return None

    def peek_sizes(self) -> dict[str, int]:
        return {p: len(items) for p, items in self._buckets.items()}

    def is_empty(self) -> bool:
        return not any(self._buckets.values())

    def total(self) -> int:
        return sum(len(items) for items in self._buckets.values())
