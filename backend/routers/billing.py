"""
Billing router — Stripe integration for SaaS plans.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request

from core.config import settings
from core.supabase import get_supabase_admin
from middleware.auth import AuthUser

router = APIRouter(prefix="/api")
logger = logging.getLogger(__name__)

# Plan limits
PLAN_LIMITS = {
    "free": {"riders": 10, "analyses_per_month": 5, "members": 2},
    "pro": {"riders": 50, "analyses_per_month": 100, "members": 10},
    "enterprise": {"riders": -1, "analyses_per_month": -1, "members": -1},
}


@router.post("/billing/checkout")
async def create_checkout(user: AuthUser, plan: str = "pro"):
    """Create a Stripe checkout session."""
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(501, "Stripe not configured")

    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Map plans to Stripe price IDs (configure in Stripe dashboard)
    PRICE_MAP = {
        "pro": "price_pro_monthly",  # Replace with actual Stripe price ID
        "enterprise": "price_enterprise_monthly",
    }

    price_id = PRICE_MAP.get(plan)
    if not price_id:
        raise HTTPException(400, f"Invalid plan: {plan}")

    session = stripe.checkout.Session.create(
        mode="subscription",
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=f"{settings.FRONTEND_URL}/dashboard/settings/billing?success=true",
        cancel_url=f"{settings.FRONTEND_URL}/dashboard/settings/billing?cancelled=true",
        metadata={"team_id": user.team_id},
    )

    return {"checkout_url": session.url}


@router.post("/billing/portal")
async def create_portal(user: AuthUser):
    """Create a Stripe customer portal session."""
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(501, "Stripe not configured")

    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Get customer ID from team (would need to store this)
    # For now, return a placeholder
    raise HTTPException(501, "Portal not yet implemented")


@router.post("/billing/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events."""
    if not settings.STRIPE_SECRET_KEY or not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(501, "Stripe not configured")

    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not sig_header:
        raise HTTPException(400, "Missing stripe-signature header")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(400, "Invalid signature")

    # Handle events
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        team_id = session.get("metadata", {}).get("team_id")
        if team_id:
            sb = get_supabase_admin()
            sb.table("teams").update({"plan": "pro"}).eq("id", team_id).execute()
            logger.info("Team %s upgraded to pro", team_id)

    elif event["type"] == "customer.subscription.deleted":
        session = event["data"]["object"]
        team_id = session.get("metadata", {}).get("team_id")
        if team_id:
            sb = get_supabase_admin()
            sb.table("teams").update({"plan": "free"}).eq("id", team_id).execute()
            logger.info("Team %s downgraded to free", team_id)

    return {"received": True}
