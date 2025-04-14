"""
Pricing & Sales Tools

This module provides tools for pricing and sales-related tasks including generating SaaS pricing tiers,
creating checkout offers with discounts, and initializing payment configurations.
"""

import random
import datetime
from typing import Dict, List, Any, Optional

# Import the registry for tool registration
from ...registry import register_tool


def pricing_generate(product_name: str, industry: str = "SaaS", tiers: int = 3) -> Dict[str, Any]:
    """
    Generate realistic SaaS tier pricing plans.
    
    Args:
        product_name: The name of the product or service
        industry: The industry or sector (defaults to SaaS)
        tiers: Number of pricing tiers to generate
        
    Returns:
        A dictionary containing the pricing tiers and metadata
    """
    # Define industry-specific pricing models
    industry_models = {
        "SaaS": {
            "billing_cycles": ["monthly", "annual"],
            "tier_names": ["Basic", "Professional", "Enterprise", "Ultimate"],
            "feature_categories": ["Core Features", "Advanced Features", "Support", "Limits", "Integrations"],
            "price_ranges": {
                "Basic": {"min": 9, "max": 29},
                "Professional": {"min": 29, "max": 99},
                "Enterprise": {"min": 99, "max": 299},
                "Ultimate": {"min": 299, "max": 999}
            }
        },
        "eCommerce": {
            "billing_cycles": ["monthly", "annual"],
            "tier_names": ["Starter", "Growth", "Business", "Enterprise"],
            "feature_categories": ["Store Features", "Marketing Tools", "Analytics", "Support", "Transaction Fees"],
            "price_ranges": {
                "Starter": {"min": 19, "max": 39},
                "Growth": {"min": 49, "max": 79},
                "Business": {"min": 99, "max": 199},
                "Enterprise": {"min": 249, "max": 499}
            }
        },
        "Marketing": {
            "billing_cycles": ["monthly", "annual"],
            "tier_names": ["Essentials", "Standard", "Premium", "Enterprise"],
            "feature_categories": ["Campaign Tools", "Analytics", "Automation", "Support", "Content Creation"],
            "price_ranges": {
                "Essentials": {"min": 15, "max": 49},
                "Standard": {"min": 59, "max": 129},
                "Premium": {"min": 149, "max": 299},
                "Enterprise": {"min": 349, "max": 799}
            }
        }
    }
    
    # Use default if industry not found
    model = industry_models.get(industry, industry_models["SaaS"])
    
    # Ensure tiers is within reasonable range
    tiers = max(2, min(tiers, len(model["tier_names"])))
    
    # Select tier names
    tier_names = model["tier_names"][:tiers]
    
    # Generate pricing structure
    pricing = {
        "product_name": product_name,
        "industry": industry,
        "currency": "USD",
        "billing_cycles": model["billing_cycles"],
        "tiers": []
    }
    
    # Generate features for each category
    features_by_category = generate_features_by_category(model["feature_categories"], industry)
    
    # Generate each tier
    for i, tier_name in enumerate(tier_names):
        # Calculate price based on tier
        price_range = model["price_ranges"][tier_name]
        monthly_price = random.randint(price_range["min"], price_range["max"])
        
        # Apply annual discount (typically 10-20%)
        annual_discount = random.randint(10, 20)
        annual_price = round(monthly_price * 12 * (1 - annual_discount / 100))
        
        # Create tier object
        tier = {
            "name": tier_name,
            "description": generate_tier_description(tier_name, product_name),
            "pricing": {
                "monthly": monthly_price,
                "annual": annual_price,
                "annual_discount_percentage": annual_discount
            },
            "features": generate_tier_features(features_by_category, i, tiers),
            "recommended": i == 1 if tiers >= 3 else i == 0,  # Usually recommend the second tier
            "cta": generate_tier_cta(tier_name)
        }
        
        pricing["tiers"].append(tier)
    
    # Add pricing recommendations
    pricing["recommendations"] = {
        "highlight_tier": pricing["tiers"][1]["name"] if tiers >= 3 else pricing["tiers"][0]["name"],
        "suggested_annual_discount": f"{annual_discount}%",
        "display_recommendations": [
            "Highlight the recommended plan visually",
            "Show annual pricing by default to emphasize savings",
            "Include a feature comparison table below pricing cards",
            "Add tooltips to explain complex features",
            "Include a money-back guarantee to reduce purchase anxiety"
        ]
    }
    
    return pricing


def generate_features_by_category(categories: List[str], industry: str) -> Dict[str, List[Dict[str, Any]]]:
    """Helper function to generate features by category."""
    features_by_category = {}
    
    # Define features for each category based on industry
    if industry == "SaaS":
        features_by_category = {
            "Core Features": [
                {"name": "Basic Dashboard", "value": True, "tier_availability": [0, 1, 2, 3]},
                {"name": "User Management", "value": True, "tier_availability": [0, 1, 2, 3]},
                {"name": "Data Export", "value": "CSV", "tier_availability": [0]},
                {"name": "Data Export", "value": "CSV, Excel, PDF", "tier_availability": [1, 2, 3]},
                {"name": "API Access", "value": False, "tier_availability": [0]},
                {"name": "API Access", "value": "Read-only", "tier_availability": [1]},
                {"name": "API Access", "value": "Full access", "tier_availability": [2, 3]}
            ],
            "Advanced Features": [
                {"name": "Advanced Analytics", "value": False, "tier_availability": [0]},
                {"name": "Advanced Analytics", "value": "Basic", "tier_availability": [1]},
                {"name": "Advanced Analytics", "value": "Advanced", "tier_availability": [2, 3]},
                {"name": "Automation", "value": False, "tier_availability": [0]},
                {"name": "Automation", "value": "Limited", "tier_availability": [1]},
                {"name": "Automation", "value": "Full", "tier_availability": [2, 3]},
                {"name": "Custom Reporting", "value": False, "tier_availability": [0, 1]},
                {"name": "Custom Reporting", "value": True, "tier_availability": [2, 3]}
            ],
            "Support": [
                {"name": "Email Support", "value": "Standard (48h)", "tier_availability": [0]},
                {"name": "Email Support", "value": "Priority (24h)", "tier_availability": [1]},
                {"name": "Email Support", "value": "Priority (12h)", "tier_availability": [2, 3]},
                {"name": "Phone Support", "value": False, "tier_availability": [0, 1]},
                {"name": "Phone Support", "value": "Business hours", "tier_availability": [2]},
                {"name": "Phone Support", "value": "24/7", "tier_availability": [3]},
                {"name": "Dedicated Account Manager", "value": False, "tier_availability": [0, 1, 2]},
                {"name": "Dedicated Account Manager", "value": True, "tier_availability": [3]}
            ],
            "Limits": [
                {"name": "Users", "value": "Up to 5", "tier_availability": [0]},
                {"name": "Users", "value": "Up to 20", "tier_availability": [1]},
                {"name": "Users", "value": "Up to 100", "tier_availability": [2]},
                {"name": "Users", "value": "Unlimited", "tier_availability": [3]},
                {"name": "Storage", "value": "5 GB", "tier_availability": [0]},
                {"name": "Storage", "value": "50 GB", "tier_availability": [1]},
                {"name": "Storage", "value": "500 GB", "tier_availability": [2]},
                {"name": "Storage", "value": "Unlimited", "tier_availability": [3]}
            ],
            "Integrations": [
                {"name": "Third-party Integrations", "value": "Basic (3)", "tier_availability": [0]},
                {"name": "Third-party Integrations", "value": "Standard (10+)", "tier_availability": [1]},
                {"name": "Third-party Integrations", "value": "Advanced (30+)", "tier_availability": [2]},
                {"name": "Third-party Integrations", "value": "All available", "tier_availability": [3]},
                {"name": "Custom Integrations", "value": False, "tier_availability": [0, 1]},
                {"name": "Custom Integrations", "value": "Limited", "tier_availability": [2]},
                {"name": "Custom Integrations", "value": "Full support", "tier_availability": [3]}
            ]
        }
    
    elif industry == "eCommerce":
        features_by_category = {
            "Store Features": [
                {"name": "Products", "value": "Up to 100", "tier_availability": [0]},
                {"name": "Products", "value": "Up to 1,000", "tier_availability": [1]},
                {"name": "Products", "value": "Up to 10,000", "tier_availability": [2]},
                {"name": "Products", "value": "Unlimited", "tier_availability": [3]},
                {"name": "Custom Domain", "value": True, "tier_availability": [0, 1, 2, 3]},
                {"name": "Abandoned Cart Recovery", "value": False, "tier_availability": [0]},
                {"name": "Abandoned Cart Recovery", "value": True, "tier_availability": [1, 2, 3]}
            ],
            "Marketing Tools": [
                {"name": "Discount Codes", "value": "Basic", "tier_availability": [0]},
                {"name": "Discount Codes", "value": "Advanced", "tier_availability": [1, 2, 3]},
                {"name": "Email Marketing", "value": "Up to 1,000 emails/month", "tier_availability": [0]},
                {"name": "Email Marketing", "value": "Up to 10,000 emails/month", "tier_availability": [1]},
                {"name": "Email Marketing", "value": "Unlimited", "tier_availability": [2, 3]},
                {"name": "SEO Tools", "value": "Basic", "tier_availability": [0, 1]},
                {"name": "SEO Tools", "value": "Advanced", "tier_availability": [2, 3]}
            ],
            "Analytics": [
                {"name": "Sales Reports", "value": "Basic", "tier_availability": [0]},
                {"name": "Sales Reports", "value": "Advanced", "tier_availability": [1, 2, 3]},
                {"name": "Customer Insights", "value": False, "tier_availability": [0]},
                {"name": "Customer Insights", "value": "Basic", "tier_availability": [1]},
                {"name": "Customer Insights", "value": "Advanced", "tier_availability": [2, 3]},
                {"name": "Conversion Tracking", "value": False, "tier_availability": [0]},
                {"name": "Conversion Tracking", "value": True, "tier_availability": [1, 2, 3]}
            ],
            "Support": [
                {"name": "Support", "value": "Email", "tier_availability": [0]},
                {"name": "Support", "value": "Email & Chat", "tier_availability": [1]},
                {"name": "Support", "value": "Priority Support", "tier_availability": [2]},
                {"name": "Support", "value": "Dedicated Support", "tier_availability": [3]},
                {"name": "Setup Assistance", "value": False, "tier_availability": [0, 1]},
                {"name": "Setup Assistance", "value": True, "tier_availability": [2, 3]}
            ],
            "Transaction Fees": [
                {"name": "Transaction Fee", "value": "2.9% + 30¢", "tier_availability": [0]},
                {"name": "Transaction Fee", "value": "2.5% + 30¢", "tier_availability": [1]},
                {"name": "Transaction Fee", "value": "2.2% + 30¢", "tier_availability": [2]},
                {"name": "Transaction Fee", "value": "1.9% + 30¢", "tier_availability": [3]}
            ]
        }
    
    elif industry == "Marketing":
        features_by_category = {
            "Campaign Tools": [
                {"name": "Email Campaigns", "value": "Basic", "tier_availability": [0]},
                {"name": "Email Campaigns", "value": "Advanced", "tier_availability": [1, 2, 3]},
                {"name": "Social Media Scheduling", "value": False, "tier_availability": [0]},
                {"name": "Social Media Scheduling", "value": "Up to 3 platforms", "tier_availability": [1]},
                {"name": "Social Media Scheduling", "value": "All platforms", "tier_availability": [2, 3]},
                {"name": "A/B Testing", "value": False, "tier_availability": [0]},
                {"name": "A/B Testing", "value": "Basic", "tier_availability": [1]},
                {"name": "A/B Testing", "value": "Advanced", "tier_availability": [2, 3]}
            ],
            "Analytics": [
                {"name": "Campaign Analytics", "value": "Basic", "tier_availability": [0]},
                {"name": "Campaign Analytics", "value": "Advanced", "tier_availability": [1, 2, 3]},
                {"name": "Custom Reports", "value": False, "tier_availability": [0]},
                {"name": "Custom Reports", "value": "Limited", "tier_availability": [1]},
                {"name": "Custom Reports", "value": "Full", "tier_availability": [2, 3]},
                {"name": "ROI Tracking", "value": False, "tier_availability": [0, 1]},
                {"name": "ROI Tracking", "value": True, "tier_availability": [2, 3]}
            ],
            "Automation": [
                {"name": "Marketing Automation", "value": False, "tier_availability": [0]},
                {"name": "Marketing Automation", "value": "Basic workflows", "tier_availability": [1]},
                {"name": "Marketing Automation", "value": "Advanced workflows", "tier_availability": [2, 3]},
                {"name": "Drip Campaigns", "value": False, "tier_availability": [0]},
                {"name": "Drip Campaigns", "value": "Limited", "tier_availability": [1]},
                {"name": "Drip Campaigns", "value": "Unlimited", "tier_availability": [2, 3]}
            ],
            "Support": [
                {"name": "Support", "value": "Email", "tier_availability": [0]},
                {"name": "Support", "value": "Email & Chat", "tier_availability": [1]},
                {"name": "Support", "value": "Priority Support", "tier_availability": [2]},
                {"name": "Support", "value": "Dedicated Manager", "tier_availability": [3]},
                {"name": "Training", "value": "Documentation", "tier_availability": [0]},
                {"name": "Training", "value": "Documentation & Webinars", "tier_availability": [1]},
                {"name": "Training", "value": "Custom Training", "tier_availability": [2, 3]}
            ],
            "Content Creation": [
                {"name": "Templates", "value": "Limited (5)", "tier_availability": [0]},
                {"name": "Templates", "value": "Standard (20+)", "tier_availability": [1]},
                {"name": "Templates", "value": "Premium (50+)", "tier_availability": [2, 3]},
                {"name": "Design Tools", "value": "Basic", "tier_availability": [0, 1]},
                {"name": "Design Tools", "value": "Advanced", "tier_availability": [2, 3]},
                {"name": "Content Library", "value": False, "tier_availability": [0]},
                {"name": "Content Library", "value": "Basic", "tier_availability": [1]},
                {"name": "Content Library", "value": "Advanced", "tier_availability": [2, 3]}
            ]
        }
    
    else:
        # Generic features for any industry
        features_by_category = {
            "Core Features": [
                {"name": "Basic Features", "value": True, "tier_availability": [0, 1, 2, 3]},
                {"name": "Advanced Features", "value": False, "tier_availability": [0]},
                {"name": "Advanced Features", "value": True, "tier_availability": [1, 2, 3]}
            ],
            "Support": [
                {"name": "Support", "value": "Email", "tier_availability": [0]},
                {"name": "Support", "value": "Email & Chat", "tier_availability": [1]},
                {"name": "Support", "value": "Priority Support", "tier_availability": [2]},
                {"name": "Support", "value": "Dedicated Support", "tier_availability": [3]}
            ],
            "Limits": [
                {"name": "Users", "value": "Limited", "tier_availability": [0]},
                {"name": "Users", "value": "Standard", "tier_availability": [1]},
                {"name": "Users", "value": "Extended", "tier_availability": [2]},
                {"name": "Users", "value": "Unlimited", "tier_availability": [3]}
            ]
        }
    
    # Filter to only include requested categories
    return {category: features_by_category.get(category, []) for category in categories if category in features_by_category}


def generate_tier_description(tier_name: str, product_name: str) -> str:
    """Helper function to generate tier descriptions."""
    descriptions = {
        "Basic": f"Essential {product_name} features for individuals and small teams just getting started.",
        "Starter": f"Everything you need to begin your journey with {product_name}.",
        "Essentials": f"Core {product_name} functionality at an affordable price point.",
        
        "Professional": f"Advanced {product_name} features for growing teams and businesses.",
        "Growth": f"Scaled {product_name} capabilities to support your expanding business needs.",
        "Standard": f"The most popular {product_name} plan with a balanced feature set.",
        
        "Enterprise": f"Comprehensive {product_name} solution with priority support for large organizations.",
        "Business": f"Powerful {product_name} tools designed for established businesses with complex needs.",
        "Premium": f"Enhanced {product_name} capabilities with premium features and support.",
        
        "Ultimate": f"The complete {product_name} experience with all features and dedicated support.",
    }
    
    return descriptions.get(tier_name, f"{tier_name} tier of {product_name} with appropriate features for this level.")


def generate_tier_features(features_by_category: Dict[str, List[Dict[str, Any]]], tier_index: int, total_tiers: int) -> Dict[str, List[Dict[str, Any]]]:
    """Helper function to generate features for a specific tier."""
    tier_features = {}
    
    for category, features in features_by_category.items():
        tier_features[category] = []
        
        for feature in features:
            if tier_index in feature["tier_availability"]:
                tier_features[category].append({
                    "name": feature["name"],
                    "value": feature["value"]
                })
    
    return tier_features


def generate_tier_cta(tier_name: str) -> Dict[str, str]:
    """Helper function to generate call-to-action for a tier."""
    cta_text = {
        "Basic": "Get Started",
        "Starter": "Start Free",
        "Essentials": "Try Essentials",
        
        "Professional": "Go Professional",
        "Growth": "Choose Growth",
        "Standard": "Select Standard",
        
        "Enterprise": "Contact Sales",
        "Business": "Request Demo",
        "Premium": "Go Premium",
        
        "Ultimate": "Get Ultimate"
    }
    
    return {
        "text": cta_text.get(tier_name, f"Choose {tier_name}"),
        "url": "#"  # Placeholder URL
    }


def checkout_offer_create(product_name: str, regular_price: float, discount_type: str = "percentage", discount_value: float = 15) -> Dict[str, Any]:
    """
    Generate a checkout offer with discount logic.
    
    Args:
        product_name: The name of the product
        regular_price: The regular price of the product
        discount_type: Type of discount (percentage, fixed, etc.)
        discount_value: Value of the discount
        
    Returns:
        A dictionary containing the checkout offer and metadata
    """
    # Validate inputs
    regular_price = max(0.01, regular_price)
    discount_value = max(0, discount_value)
    
    # Calculate discounted price based on discount type
    if discount_type == "percentage":
        discount_value = min(100, discount_value)  # Cap percentage at 100%
        discount_amount = regular_price * (discount_value / 100)
        discounted_price = regular_price - discount_amount
    elif discount_type == "fixed":
        discount_amount = min(regular_price - 0.01, discount_value)  # Ensure price doesn't go below 0.01
        discounted_price = regular_price - discount_amount
    else:  # Default to percentage
        discount_value = min(100, discount_value)
        discount_amount = regular_price * (discount_value / 100)
        discounted_price = regular_price - discount_amount
    
    # Round prices to two decimal places
    regular_price = round(regular_price, 2)
    discount_amount = round(discount_amount, 2)
    discounted_price = round(discounted_price, 2)
    
    # Calculate savings percentage
    savings_percentage = round((discount_amount / regular_price) * 100, 1)
    
    # Generate offer details
    offer = {
        "product": {
            "name": product_name,
            "regular_price": regular_price,
            "currency": "USD"
        },
        "discount": {
            "type": discount_type,
            "value": discount_value,
            "amount": discount_amount,
            "discounted_price": discounted_price,
            "savings_percentage": savings_percentage
        },
        "display": {
            "price_display": f"${discounted_price}",
            "regular_price_display": f"${regular_price}",
            "savings_display": f"Save ${discount_amount} ({savings_percentage}%)"
        }
    }
    
    # Generate call-to-action options
    cta_options = generate_cta_options(product_name, savings_percentage, discount_type)
    offer["cta_options"] = cta_options
    
    # Generate urgency elements
    urgency_elements = generate_urgency_elements()
    offer["urgency_elements"] = urgency_elements
    
    # Generate upsell opportunities
    upsell_opportunities = generate_upsell_opportunities(product_name, discounted_price)
    offer["upsell_opportunities"] = upsell_opportunities
    
    # Generate display recommendations
    offer["display_recommendations"] = [
        "Show original price with strikethrough next to discounted price",
        f"Highlight the savings of {savings_percentage}%",
        "Use a contrasting color for the discount callout",
        "Add a countdown timer if the offer is time-limited",
        "Display security badges and payment options near the checkout button"
    ]
    
    return offer


def generate_cta_options(product_name: str, savings_percentage: float, discount_type: str) -> List[Dict[str, str]]:
    """Helper function to generate CTA options."""
    cta_options = []
    
    # Standard CTAs
    cta_options.append({
        "text": "Buy Now",
        "style": "primary",
        "conversion_rate": "baseline"
    })
    
    # Savings-focused CTAs
    if savings_percentage >= 10:
        cta_options.append({
            "text": f"Save {round(savings_percentage)}% Today",
            "style": "primary",
            "conversion_rate": "potentially 5-15% higher than baseline"
        })
    
    # Product-focused CTAs
    cta_options.append({
        "text": f"Get {product_name}",
        "style": "primary",
        "conversion_rate": "similar to baseline"
    })
    
    # Urgency CTAs
    if discount_type == "percentage" and savings_percentage >= 15:
        cta_options.append({
            "text": "Claim Your Discount",
            "style": "primary",
            "conversion_rate": "potentially 10-20% higher than baseline"
        })
    
    # Risk-reduction CTAs
    cta_options.append({
        "text": "Try Risk-Free",
        "style": "secondary",
        "conversion_rate": "potentially effective for high-priced items"
    })
    
    return cta_options


def generate_urgency_elements() -> List[Dict[str, Any]]:
    """Helper function to generate urgency elements."""
    urgency_elements = []
    
    # Time-limited offer
    end_date = (datetime.datetime.now() + datetime.timedelta(days=random.randint(3, 7))).strftime("%Y-%m-%d")
    urgency_elements.append({
        "type": "time_limited",
        "display_text": f"Offer ends {end_date}",
        "end_date": end_date,
        "recommended": True
    })
    
    # Limited quantity
    quantity = random.randint(5, 20)
    urgency_elements.append({
        "type": "limited_quantity",
        "display_text": f"Only {quantity} left at this price",
        "quantity": quantity,
        "recommended": quantity <= 10
    })
    
    # Social proof
    recent_purchases = random.randint(10, 50)
    urgency_elements.append({
        "type": "social_proof",
        "display_text": f"{recent_purchases} people purchased in the last 24 hours",
        "count": recent_purchases,
        "recommended": recent_purchases >= 20
    })
    
    return urgency_elements


def generate_upsell_opportunities(product_name: str, base_price: float) -> List[Dict[str, Any]]:
    """Helper function to generate upsell opportunities."""
    upsell_opportunities = []
    
    # Extended warranty/support
    support_price = round(base_price * 0.2, 2)
    upsell_opportunities.append({
        "type": "add_on",
        "name": f"Extended Support for {product_name}",
        "description": "Get priority support and updates for 12 months",
        "price": support_price,
        "display_price": f"${support_price}",
        "recommended": True
    })
    
    # Premium features
    premium_price = round(base_price * 0.3, 2)
    upsell_opportunities.append({
        "type": "upgrade",
        "name": f"Premium {product_name} Features",
        "description": "Unlock advanced features and capabilities",
        "price": premium_price,
        "display_price": f"${premium_price}",
        "recommended": base_price >= 50
    })
    
    # Bundle deal
    bundle_discount = random.randint(10, 25)
    bundle_price = round(base_price * 1.5 * (1 - bundle_discount / 100), 2)
    upsell_opportunities.append({
        "type": "bundle",
        "name": f"{product_name} Complete Package",
        "description": f"Get {product_name} plus all add-ons at {bundle_discount}% off",
        "price": bundle_price,
        "display_price": f"${bundle_price}",
        "savings": f"{bundle_discount}%",
        "recommended": True
    })
    
    return upsell_opportunities


def payment_init(product_name: str, price: float, currency: str = "USD", payment_methods: List[str] = None) -> Dict[str, Any]:
    """
    Generate Stripe-ready payment configuration.
    
    Args:
        product_name: The name of the product
        price: The price of the product
        currency: The currency code
        payment_methods: List of payment methods to accept
        
    Returns:
        A dictionary containing the payment configuration and metadata
    """
    # Default payment methods if none provided
    if not payment_methods:
        payment_methods = ["card", "apple_pay", "google_pay"]
    
    # Validate inputs
    price = max(0.01, price)
    
    # Generate a unique product ID and price ID (simulating Stripe IDs)
    product_id = f"prod_{random_string(14)}"
    price_id = f"price_{random_string(14)}"
    
    # Generate payment configuration
    payment_config = {
        "mode": "payment",  # or "subscription" for recurring payments
        "product": {
            "id": product_id,
            "name": product_name,
            "description": f"Purchase of {product_name}",
            "metadata": {
                "product_type": "digital",  # or "physical", "service"
                "category": "software"  # example category
            }
        },
        "price": {
            "id": price_id,
            "unit_amount": int(price * 100),  # Stripe uses cents
            "currency": currency.lower(),
            "display_amount": format_currency(price, currency)
        },
        "payment_methods": payment_methods,
        "success_url": "https://example.com/success?session_id={CHECKOUT_SESSION_ID}",
        "cancel_url": "https://example.com/cancel",
        "metadata": {
            "source": "website_checkout",
            "utm_source": "{UTM_SOURCE}"  # Placeholder for dynamic insertion
        }
    }
    
    # Add Stripe-specific configuration
    payment_config["stripe_config"] = {
        "publishable_key": "pk_test_placeholder",  # Placeholder for actual key
        "checkout_session_config": {
            "payment_method_types": payment_methods,
            "line_items": [
                {
                    "price": price_id,
                    "quantity": 1
                }
            ],
            "mode": "payment",
            "success_url": payment_config["success_url"],
            "cancel_url": payment_config["cancel_url"],
            "metadata": payment_config["metadata"]
        },
        "elements_config": {
            "appearance": {
                "theme": "stripe",
                "variables": {
                    "colorPrimary": "#0570de",
                    "colorBackground": "#ffffff",
                    "colorText": "#30313d",
                    "colorDanger": "#df1b41",
                    "fontFamily": "Ideal Sans, system-ui, sans-serif",
                    "spacingUnit": "4px",
                    "borderRadius": "4px"
                }
            }
        }
    }
    
    # Add sandbox testing configuration
    payment_config["sandbox_config"] = {
        "test_cards": [
            {
                "type": "Visa",
                "number": "4242 4242 4242 4242",
                "exp": "Any future date",
                "cvc": "Any 3 digits",
                "zip": "Any 5 digits",
                "behavior": "Successful payment"
            },
            {
                "type": "Visa (3D Secure)",
                "number": "4000 0000 0000 3220",
                "exp": "Any future date",
                "cvc": "Any 3 digits",
                "zip": "Any 5 digits",
                "behavior": "3D Secure authentication"
            },
            {
                "type": "Visa (Declined)",
                "number": "4000 0000 0000 0002",
                "exp": "Any future date",
                "cvc": "Any 3 digits",
                "zip": "Any 5 digits",
                "behavior": "Declined payment"
            }
        ],
        "webhook_testing": {
            "local_testing": "Use Stripe CLI: stripe listen --forward-to localhost:4242/webhook",
            "trigger_events": "Use Stripe CLI: stripe trigger payment_intent.succeeded"
        }
    }
    
    # Add implementation code snippets
    payment_config["implementation"] = {
        "frontend": {
            "language": "javascript",
            "code": generate_frontend_code(product_name, price_id)
        },
        "backend": {
            "language": "python",
            "code": generate_backend_code(product_name, price_id)
        }
    }
    
    return payment_config


def random_string(length: int) -> str:
    """Helper function to generate a random string."""
    import string
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def format_currency(amount: float, currency: str) -> str:
    """Helper function to format currency."""
    currency_symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "CAD": "C$",
        "AUD": "A$"
    }
    
    symbol = currency_symbols.get(currency.upper(), currency.upper() + " ")
    
    # Format based on currency
    if currency.upper() == "JPY":
        return f"{symbol}{int(amount)}"  # JPY doesn't use decimal places
    else:
        return f"{symbol}{amount:.2f}"


def generate_frontend_code(product_name: str, price_id: str) -> str:
    """Helper function to generate frontend code snippet."""
    return f"""// Create a Stripe checkout for {product_name}
const stripe = Stripe('pk_test_your_publishable_key');

document.getElementById('checkout-button').addEventListener('click', async () => {{
  try {{
    // Create a checkout session
    const response = await fetch('/create-checkout-session', {{
      method: 'POST',
      headers: {{
        'Content-Type': 'application/json',
      }},
      body: JSON.stringify({{
        priceId: '{price_id}',
        productName: '{product_name}',
      }}),
    }});
    
    const session = await response.json();
    
    // Redirect to Stripe Checkout
    const result = await stripe.redirectToCheckout({{
      sessionId: session.id,
    }});
    
    if (result.error) {{
      console.error(result.error.message);
    }}
  }} catch (error) {{
    console.error('Error:', error);
  }}
}});
"""


def generate_backend_code(product_name: str, price_id: str) -> str:
    """Helper function to generate backend code snippet."""
    return f"""# Flask backend for {product_name} checkout
from flask import Flask, request, jsonify
import stripe
import os

app = Flask(__name__)
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        data = request.get_json()
        
        # Create a checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {{
                    'price': '{price_id}',
                    'quantity': 1,
                }},
            ],
            mode='payment',
            success_url='https://example.com/success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url='https://example.com/cancel',
            metadata={{
                'product_name': '{product_name}',
                'source': 'website_checkout'
            }}
        )
        
        return jsonify({{'id': checkout_session.id}})
    except Exception as e:
        return jsonify(error=str(e)), 400

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ.get('STRIPE_WEBHOOK_SECRET')
        )
        
        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            # Fulfill the order
            fulfill_order(session)
            
        return jsonify(success=True)
    except Exception as e:
        return jsonify(error=str(e)), 400
        
def fulfill_order(session):
    # Implement order fulfillment logic here
    print(f"Fulfilling order for session {{session.id}}")
    # e.g., send email, provision access, etc.
"""


# Register all Pricing & Sales tools
register_tool(
    name="pricing.generate",
    description="Generate realistic SaaS tier pricing plans",
    category="Pricing & Sales",
    timeout_seconds=45,
    max_retries=2,
    requires_reflection=True,
    handler=pricing_generate
)

register_tool(
    name="checkout.offer.create",
    description="Generate a checkout offer with discount logic",
    category="Pricing & Sales",
    timeout_seconds=30,
    max_retries=2,
    requires_reflection=False,
    handler=checkout_offer_create
)

register_tool(
    name="payment.init",
    description="Generate Stripe-ready payment configuration",
    category="Pricing & Sales",
    timeout_seconds=45,
    max_retries=3,
    requires_reflection=True,
    handler=payment_init
)
