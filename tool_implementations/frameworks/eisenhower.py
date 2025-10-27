#!/usr/bin/env python3
"""
Eisenhower Matrix Framework Tool
Analyzes tasks based on urgency and importance.
"""

from typing import Dict, List, Any, Optional
import json

def process_eisenhower(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process items using Eisenhower Matrix framework.

    Args:
        input_data: Input data following q4.input.schema.json

    Returns:
        Quadrant analysis result
    """
    items = input_data.get('items', [])
    prefs = input_data.get('prefs', {})

    # Define quadrants
    quadrants = {
        "Q1": {"x": "high", "y": "high", "name": "Do Now"},
        "Q2": {"x": "low", "y": "high", "name": "Schedule"},
        "Q3": {"x": "high", "y": "low", "name": "Delegate"},
        "Q4": {"x": "low", "y": "low", "name": "Eliminate"}
    }

    # Categorize items
    cards = []
    quadrant_counts = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}

    for item in items:
        urgency = item.get('urgency', 0)
        importance = item.get('importance', 0)

        # Determine quadrant
        if urgency >= 0.5 and importance >= 0.5:
            quadrant = "Q1"
        elif urgency < 0.5 and importance >= 0.5:
            quadrant = "Q2"
        elif urgency >= 0.5 and importance < 0.5:
            quadrant = "Q3"
        else:
            quadrant = "Q4"

        quadrant_counts[quadrant] += 1

        cards.append({
            "id": item.get('id', f"item_{len(cards)}"),
            "title": item.get('title', 'Untitled'),
            "quadrant": quadrant,
            "x": urgency,
            "y": importance,
            "data": item
        })

    return {
        "layout": "quadrant",
        "framework": "eisenhower",
        "axes": {"x": "urgency", "y": "importance"},
        "quadrants": quadrants,
        "cards": cards,
        "ui": prefs.get('ui', {"style": "cards", "theme": "neutral"}),
        "meta": {
            "total_items": len(items),
            "quadrant_distribution": quadrant_counts
        }
    }