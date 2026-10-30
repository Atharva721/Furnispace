"""
Deterministic Rule-Based Room Bundle Recommendation Engine for FurniSpace.
Zero external AI APIs required. 100% deterministic, robust, and budget-guaranteed.
"""

from typing import List, Dict, Optional, Any
from models import Product

ROOM_CATEGORY_PRIORITIES = {
    'Living Room': ['sofas', 'tables', 'chairs', 'storage', 'lighting', 'decor'],
    'Bedroom': ['beds', 'wardrobes', 'storage', 'lighting', 'decor'],
    'Dining Room': ['tables', 'chairs', 'storage', 'lighting', 'decor'],
    'Study Room': ['tables', 'chairs', 'storage', 'lighting', 'decor']
}

ROOM_MINIMUM_ESSENTIALS = {
    'Living Room': ['sofas', 'tables'],
    'Bedroom': ['beds', 'storage'],
    'Dining Room': ['tables', 'chairs'],
    'Study Room': ['tables', 'chairs']
}


def recommend_room_bundle(
    room_type: str,
    budget: int,
    style: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generates an optimized, deterministic furniture bundle strictly within the given budget.
    
    1. Fetches active, in-stock products matching room suitability.
    2. Prioritizes matching style first, then gracefully expands if needed.
    3. Greedily fulfills essential room categories, then accessory categories as budget allows.
    4. Guarantees total <= budget.
    """
    if budget <= 0:
        return {
            "success": False,
            "message": "Please enter a valid budget greater than ₹0.",
            "items": [],
            "bundle_items": [],
            "total_price": 0,
            "remaining_budget": budget,
            "room_type": room_type,
            "style": style or "Any",
            "alternatives": {}
        }

    categories_priority = ROOM_CATEGORY_PRIORITIES.get(
        room_type,
        ['sofas', 'tables', 'chairs', 'storage', 'lighting', 'decor']
    )
    essentials = ROOM_MINIMUM_ESSENTIALS.get(room_type, categories_priority[:2])

    # Fetch candidate products matching the room
    all_candidates = Product.query.filter(
        Product.is_active.is_(True),
        Product.stock > 0
    ).all()

    # Filter candidates that explicitly include room_type in room_types string
    room_candidates = [
        p for p in all_candidates
        if room_type.lower() in [r.lower() for r in p.room_list()]
    ]
    # Fallback to general candidates if room tagging is sparse
    if len(room_candidates) < len(categories_priority):
        room_candidates = all_candidates

    # Group candidate products by category
    candidates_by_cat: Dict[str, List[Product]] = {}
    for cat in categories_priority:
        cat_items = [p for p in room_candidates if p.category.lower() == cat.lower()]
        # Sort items: style match first, then by balanced price
        if style and style != 'Any':
            cat_items.sort(
                key=lambda p: (0 if p.style.lower() == style.lower() else 1, p.price)
            )
        else:
            cat_items.sort(key=lambda p: p.price)
        candidates_by_cat[cat] = cat_items

    # Build bundle
    selected_items: List[Product] = []
    current_total = 0

    # Step 1: Ensure minimum essentials fit within budget
    for cat in essentials:
        available = candidates_by_cat.get(cat, [])
        picked = None
        for item in available:
            if current_total + item.price <= budget:
                picked = item
                break
        if picked:
            selected_items.append(picked)
            current_total += picked.price

    # Check if we could not even afford essentials
    if len(selected_items) < len(essentials):
        # Find minimum required cost for essentials
        min_needed = 0
        for cat in essentials:
            available = candidates_by_cat.get(cat, [])
            if available:
                min_needed += min(p.price for p in available)
        return {
            "success": False,
            "message": f"Your budget of ₹{budget:,} is lower than the minimum essential combination for a {room_type} (approx. ₹{min_needed:,}). Please consider increasing your budget or exploring our pre-loved Resale Marketplace.",
            "items": [],
            "bundle_items": [],
            "total_price": 0,
            "remaining_budget": budget,
            "room_type": room_type,
            "style": style or "Any",
            "alternatives": {}
        }

    # Step 2: Greedily add remaining priority categories as budget permits
    for cat in categories_priority:
        if any(item.category == cat for item in selected_items):
            continue  # Already picked for this category

        available = candidates_by_cat.get(cat, [])
        for item in available:
            if current_total + item.price <= budget:
                selected_items.append(item)
                current_total += item.price
                break

    # Prepare alternative options for swapping in each selected slot
    alternatives: Dict[int, List[Dict[str, Any]]] = {}
    for item in selected_items:
        cat_pool = candidates_by_cat.get(item.category, [])
        alt_list = []
        for alt in cat_pool:
            if alt.id != item.id:
                alt_list.append({
                    "id": alt.id,
                    "name": alt.name,
                    "price": alt.price,
                    "image_url": alt.image_url,
                    "style": alt.style,
                    "material": alt.material,
                    "dimensions": alt.dimensions,
                    "difference": alt.price - item.price
                })
        alternatives[item.id] = alt_list

    return {
        "success": True,
        "message": f"Successfully curated a balanced {style or 'harmonious'} {room_type} bundle!",
        "items": selected_items,
        "bundle_items": selected_items,
        "total_price": current_total,
        "remaining_budget": budget - current_total,
        "budget": budget,
        "room_type": room_type,
        "style": style or "Any",
        "alternatives": alternatives
    }
