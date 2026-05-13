SYSTEM_PROMPT = """
You are an AI-powered operations assistant for SMEs.

Your responsibilities:
- analyze operational stock risks
- generate procurement communication
- prioritize urgent supply issues
- protect business continuity

Behavior Rules:
- concise but impactful
- professional operational language
- avoid conversational filler
- focus on business risk
- outputs must sound enterprise-grade
- produce actionable operational outputs
"""

def build_stock_email_prompt(
    product_name: str,
    current_stock: int,
    critical_limit: int,
    supplier_email: str
):

    return f"""
Product Information:

- Product Name: {product_name}
- Current Stock: {current_stock}
- Critical Limit: {critical_limit}
- Supplier Email: {supplier_email}

Task:
Generate a professional supplier email.

Requirements:
- explain that stock level is below critical threshold
- request urgent restocking
- request pricing and delivery information
- maintain concise business tone
- maximum 120 words
- no markdown formatting
- output email body only
"""

def build_stock_analysis_prompt(products: list):

    product_text = "\n".join(
        [
            f"- {p.name} (SKU: {p.sku}) | Stock: {p.stock_quantity} | Critical Limit: {p.critical_limit}"
            for p in products
        ]
    )

    return f"""
Critical Stock Report:

{product_text}

Task:
Analyze the operational risks caused by low stock levels.

Generate:
1. Overall risk assessment
2. Highest priority products
3. Possible operational impacts
4. Recommended immediate actions

Requirements:
- concise and actionable
- maximum 180 words
- prioritize business continuity
- avoid generic statements
- no markdown tables
"""