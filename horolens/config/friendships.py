FRIENDSHIPS = {

    "Sun": {
        "friends": ["Moon", "Mars", "Jupiter"],
        "enemies": ["Venus", "Saturn"],
        "neutral": ["Mercury"]
    },

    "Moon": {
        "friends": ["Sun", "Mercury"],
        "enemies": [],
        "neutral": ["Mars", "Jupiter", "Venus", "Saturn"]
    },

    "Mars": {
        "friends": ["Sun", "Moon", "Jupiter"],
        "enemies": ["Mercury"],
        "neutral": ["Venus", "Saturn"]
    },

    "Mercury": {
        "friends": ["Sun", "Venus"],
        "enemies": ["Moon"],
        "neutral": ["Mars", "Jupiter", "Saturn"]
    },

    "Jupiter": {
        "friends": ["Sun", "Moon", "Mars"],
        "enemies": ["Mercury", "Venus"],
        "neutral": ["Saturn"]
    },

    "Venus": {
        "friends": ["Mercury", "Saturn"],
        "enemies": ["Sun", "Moon"],
        "neutral": ["Mars", "Jupiter"]
    },

    "Saturn": {
        "friends": ["Mercury", "Venus"],
        "enemies": ["Sun", "Moon"],
        "neutral": ["Mars", "Jupiter"]
    }
}