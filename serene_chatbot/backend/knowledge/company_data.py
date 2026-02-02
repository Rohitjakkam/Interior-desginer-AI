"""Company knowledge base for Serene Design Studio chatbot."""

COMPANY_INFO = {
    "name": "Serene Design Studio",
    "tagline": "Elevate Your Living Experience With Thoughtful Design Solutions",
    "description": "Serene Design Studio delivers smart, reliable interior solutions for everyday living.",
    "values": ["Comfort", "Luxury", "Assurance", "Quality", "Premium"],
    "address": "Office No. 14, 1st Floor, VTP Cygnus Commercial Complex, Manjari Khurd, Pune - 412307",
    "philosophy": "Design is not just what it looks like and feels like. Design is how it works.",

    "services": {
        "basic": {
            "name": "Basic Interior",
            "description": "Smart and functional interiors designed for everyday living. Ideal for budget-friendly homes with clean layouts and essential finishes."
        },
        "premium": {
            "name": "Premium Interior",
            "description": "Well-balanced interiors with enhanced design details and quality finishes. Perfect for modern homes that value comfort and style."
        },
        "luxury": {
            "name": "Luxury Interior",
            "description": "Exclusive, high-end interiors crafted with elegance and precision. Designed for those who seek refined aesthetics and bespoke detailing."
        }
    },

    "offerings": [
        {
            "name": "Full Home Interior",
            "description": "End to end home interiors."
        },
        {
            "name": "Custom Furniture",
            "description": "Bespoke furniture for your space."
        },
        {
            "name": "Office Interior",
            "description": "Professional workspace designs."
        }
    ],

    "process": [
        {
            "step": 1,
            "name": "Start Project",
            "description": "Embark on your design adventure by initiating your project. Share your vision and set the stage for a bespoke design experience."
        },
        {
            "step": 2,
            "name": "Craft",
            "description": "Collaborate closely to achieve design excellence refining your vision and crafting brilliance into every aspect of your space."
        },
        {
            "step": 3,
            "name": "Execute",
            "description": "Witness your vision becoming a reality as we execute the design plan with precision. Celebrate the joy of your newly transformed space."
        }
    ],

    "promises": [
        {
            "name": "On-Time Delivery",
            "description": "We commit to delivering your project on schedule."
        },
        {
            "name": "5+ Years Warranty",
            "description": "All our work comes with a comprehensive warranty for your peace of mind."
        },
        {
            "name": "No Hidden Costs",
            "description": "Transparent pricing with no surprises. What we quote is what you pay."
        }
    ],

    "house_types": ["1RK", "1BHK", "2BHK", "3BHK", "4BHK", "Villa", "Penthouse", "Office", "Shop", "Restaurant"],

    "budget_ranges": [
        "Under 5 Lakhs",
        "5-10 Lakhs",
        "10-15 Lakhs",
        "15-25 Lakhs",
        "25-50 Lakhs",
        "50 Lakhs+"
    ]
}


FAQS = {
    "cost_complete_interior": {
        "question": "How much does a complete home interior cost?",
        "answer": "A complete home interior is tailored to your unique style, space requirements, and material preferences. The cost varies depending on the design scope, finishes, and customization you choose. We begin with understanding your vision and then craft a personalized plan. This ensures you get a beautifully designed home that fits your lifestyle perfectly. Would you like to get a free estimate for your home?"
    },
    "choose_designer": {
        "question": "How do I choose the right interior designer?",
        "answer": "When choosing an interior designer, look for experience, portfolio quality, communication style, and customer reviews. At Serene Design Studio, we pride ourselves on transparent communication, 5+ years warranty, on-time delivery, and no hidden costs. We'd love to show you our portfolio and discuss your project!"
    },
    "cost_1bhk": {
        "question": "What is the average cost of a 1BHK interior?",
        "answer": "The cost of a 1BHK interior depends on your chosen style, materials, and level of customization. Our Basic, Premium, and Luxury packages cater to different budgets while ensuring quality. For an accurate estimate tailored to your requirements, please share your details and we'll provide a personalized quote."
    },
    "cost_2bhk_3bhk": {
        "question": "What is the estimated cost for 2BHK and 3BHK interiors?",
        "answer": "2BHK and 3BHK interior costs vary based on the scope of work, material choices, and design complexity. We offer flexible packages to suit different budgets - from functional Basic interiors to exclusive Luxury designs. Share your requirements with us for a detailed, customized quote!"
    },
    "factors_cost": {
        "question": "What factors affect the cost of interior design?",
        "answer": "Several factors influence interior design costs: 1) Size of the space, 2) Quality of materials and finishes, 3) Complexity of design and customization, 4) Furniture type (modular vs custom), 5) Timeline requirements. At Serene, we provide transparent pricing with no hidden costs, so you always know what to expect."
    }
}


def get_faq_response(message: str) -> str | None:
    """Check if the message matches any FAQ and return the answer."""
    message_lower = message.lower()

    keywords_map = {
        "cost_complete_interior": ["complete home", "complete interior", "full home cost", "total cost", "how much"],
        "choose_designer": ["choose designer", "right designer", "select designer", "find designer"],
        "cost_1bhk": ["1bhk", "1 bhk", "one bhk"],
        "cost_2bhk_3bhk": ["2bhk", "3bhk", "2 bhk", "3 bhk", "two bhk", "three bhk"],
        "factors_cost": ["factors", "affect cost", "price factors", "what affects"]
    }

    for faq_key, keywords in keywords_map.items():
        for keyword in keywords:
            if keyword in message_lower:
                return FAQS[faq_key]["answer"]

    return None


SYSTEM_PROMPT = """You are a friendly and professional customer service representative for Serene Design Studio, a premium interior design company based in Pune, India.

ABOUT SERENE DESIGN STUDIO:
- Tagline: "Elevate Your Living Experience With Thoughtful Design Solutions"
- Values: Comfort, Luxury, Assurance, Quality, Premium
- Philosophy: "Design is not just what it looks like and feels like. Design is how it works."
- Address: Office No. 14, 1st Floor, VTP Cygnus Commercial Complex, Manjari Khurd, Pune - 412307

SERVICES (Three Tiers):
1. Basic Interior - Smart, functional interiors for budget-friendly homes with clean layouts and essential finishes
2. Premium Interior - Enhanced design details with quality finishes, perfect for modern homes valuing comfort and style
3. Luxury Interior - Exclusive, high-end interiors with elegance, precision, and bespoke detailing

OFFERINGS:
- Full Home Interior (end-to-end home design)
- Custom Furniture (bespoke furniture for your space)
- Office Interior (professional workspace designs)

OUR PROCESS (Three Simple Steps):
1. Start Project - Share your vision and initiate the design journey
2. Craft - Collaborate closely to refine and perfect the design
3. Execute - Watch your vision become reality with precision execution

OUR PROMISES:
- On-Time Delivery - Projects delivered on schedule
- 5+ Years Warranty - Comprehensive warranty for peace of mind
- No Hidden Costs - Transparent pricing, what we quote is what you pay

YOUR ROLE:
1. Greet customers warmly and professionally
2. Answer questions about our services, process, and offerings
3. For pricing questions, explain that costs vary based on space, materials, and customization
4. Guide interested customers to get a FREE estimate by sharing their details
5. Collect lead information (name, mobile, location, house type, budget) when appropriate
6. Be helpful, professional, and encourage engagement

RESPONSE GUIDELINES:
- Keep responses concise (2-4 sentences typically)
- Be warm and welcoming
- Always highlight our unique selling points: warranty, no hidden costs, on-time delivery
- For specific pricing, encourage them to get a personalized free estimate
- When someone shows interest, ask if they'd like to share their details for a free consultation
- Use simple, clear language
- Don't overwhelm with too much information at once

IMPORTANT:
- Never make up specific prices - always guide to free estimate
- Be honest if you don't know something
- Focus on building trust and encouraging the next step (getting a quote)
"""


GREETING_MESSAGE = """Hello! Welcome to Serene Design Studio!

I'm here to help you explore our interior design services. Whether you're looking to transform your home or office, we've got you covered with our Basic, Premium, and Luxury design packages.

How can I assist you today?"""


QUICK_REPLIES_INITIAL = [
    "Get Free Quote",
    "Our Services",
    "View Packages",
    "FAQs"
]

QUICK_REPLIES_SERVICES = [
    "Basic Interior",
    "Premium Interior",
    "Luxury Interior",
    "Get Quote"
]

QUICK_REPLIES_AFTER_INFO = [
    "Get Free Estimate",
    "Ask Another Question",
    "Talk to Expert"
]
