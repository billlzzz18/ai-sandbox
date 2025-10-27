#!/usr/bin/env python3
"""
Value Effort Framework Tool
Analyzes items based on impact vs effort for prioritization.
"""

from typing import Dict, List, Any, Optional
import json

def process_value_effort(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process items using Value vs Effort framework.

    Args:
        input_data: Input data following q4.input.schema.json

    Returns:
        Quadrant analysis result
    """
    items = input_data.get('items', [])
    prefs = input_data.get('prefs', {})

    # Define quadrants
    quadrants = {
        "Q1": {"x": "low", "y": "high", "name": "Quick Wins"},
        "Q2": {"x": "high", "y": "high", "name": "Major Projects"},
        "Q3": {"x": "low", "y": "low", "name": "Fill-ins"},
        "Q4": {"x": "high", "y": "low", "name": "Thankless Tasks"}
    }

    # Categorize items
    cards = []
    quadrant_counts = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}

    for item in items:
        impact = item.get('impact', 0)
        effort = item.get('effort', 0)

        # Determine quadrant
        if impact >= 0.5 and effort < 0.5:
            quadrant = "Q1"
        elif impact >= 0.5 and effort >= 0.5:
            quadrant = "Q2"
        elif impact < 0.5 and effort < 0.5:
            quadrant = "Q3"
        else:
            quadrant = "Q4"

        quadrant_counts[quadrant] += 1

        cards.append({
            "id": item.get('id', f"item_{len(cards)}"),
            "title": item.get('title', 'Untitled'),
            "quadrant": quadrant,
            "x": effort,
            "y": impact,
            "data": item
        })

    return {
        "layout": "quadrant",
        "framework": "value_effort",
        "axes": {"x": "effort", "y": "impact"},
        "quadrants": quadrants,
        "cards": cards,
        "ui": prefs.get('ui', {"style": "cards", "theme": "neutral"}),
        "meta": {
            "total_items": len(items),
            "quadrant_distribution": quadrant_counts
        }
    }