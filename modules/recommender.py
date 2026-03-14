def get_recommendations(color, garment_type):

    rules = {
        "black": {
            "daily": ("white", 95, "Classic high contrast formal pairing."),
            "event": ("light blue", 85, "Professional and clean for meetings."),
            "genz": ("beige", 75, "Modern neutral pairing.")
        },

        "navy": {
            "daily": ("white", 95, "Timeless navy-white formal combination."),
            "event": ("pink", 85, "Elegant contrast suitable for events."),
            "genz": ("lavender", 75, "Trendy yet formal palette.")
        }
    }

    if color not in rules:
        return []

    data = rules[color]

    return [
        {
            "category": "Daily Wear",
            "color": data["daily"][0],
            "confidence": data["daily"][1],
            "reason": data["daily"][2]
        },
        {
            "category": "Event Wear",
            "color": data["event"][0],
            "confidence": data["event"][1],
            "reason": data["event"][2]
        },
        {
            "category": "Gen Z Style",
            "color": data["genz"][0],
            "confidence": data["genz"][1],
            "reason": data["genz"][2]
        }
    ]