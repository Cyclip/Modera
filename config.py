description = """Intelligent Discord bot for moderation assistance."""

prefix = "~"

owners = [475272000089227276, 744580836241965118]

cooldownCooldown = 10

inviteLink = "https://discord.com/api/oauth2/authorize?client_id=840601414685556746&permissions=8&scope=bot"

uniColour = 0x6A509B

status = "~help | git.io/J35vM"

attributes = {
    "toxicity": {
        "description": "Rude and disrespectful comments will be flagged. This filter is relatively strict.",
        "attribute": "TOXICITY",
        "settings": {
            "enabled": {
                "restrict": "values",
                "values": ["on", "off"],
            },
            "threshold": {
                "restrict": "range",
                "range": [0, 100],
            },
        },
    },
    "abusive": {
        "description": "Extreme disrespectful and aggressive comments will be flagged.",
        "attribute": "SEVERE_TOXICITY",
        "settings": {
            "enabled": {
                "restrict": "values",
                "values": ["on", "off"],
            },
            "threshold": {
                "restrict": "range",
                "range": [0, 100],
            },
        },
    },
    "identity_attack": {
        "description": "Hateful comments targeting a person based on their identity will be flagged.",
        "attribute": "IDENTITY_ATTACK",
        "settings": {
            "enabled": {
                "restrict": "values",
                "values": ["on", "off"],
            },
            "threshold": {
                "restrict": "range",
                "range": [0, 100],
            },
        },
    },
    "insults": {
        "description": "Insults and inflammatory statement towards a person(s) will be flagged.",
        "attribute": "INSULT",
        "settings": {
            "enabled": {
                "restrict": "values",
                "values": ["on", "off"],
            },
            "threshold": {
                "restrict": "range",
                "range": [0, 100],
            },
        },
    },
    "profanity": {
        "description": "Swear words and obscene language will be flagged.",
        "attribute": "PROFANITY",
        "settings": {
            "enabled": {
                "restrict": "values",
                "values": ["on", "off"],
            },
            "threshold": {
                "restrict": "range",
                "range": [0, 100],
            },
        },
    },
    "threats": {
        "description": "Threats to inflict pain, injury or violence against a person(s) will be flagged.",
        "attribute": "THREAT",
        "settings": {
            "enabled": {
                "restrict": "values",
                "values": ["on", "off"],
            },
            "threshold": {
                "restrict": "range",
                "range": [0, 100],
            },
        },
    },
    "sexual": {
        "description": "All references to sexually explicit or lewd concepts will be flagged.",
        "attribute": "SEXUALLY_EXPLICIT",
        "settings": {
            "enabled": {
                "restrict": "values",
                "values": ["on", "off"],
            },
            "threshold": {
                "restrict": "range",
                "range": [0, 100],
            },
            "allow_nsfw": {
                "restrict": "values",
                "values": ["true", "false"],
            },
        },
    },
    "flirtation": {
        "description": "Pickup lines, subtle sexual innuendos, etc. will be flagged.",
        "attribute": "FLIRTATION",
        "settings": {
            "enabled": {
                "restrict": "values",
                "values": ["on", "off"],
            },
            "threshold": {
                "restrict": "range",
                "range": [0, 100],
            },
            "allow_nsfw": {
                "restrict": "values",
                "values": ["true", "false"],
            },
        },
    },
    "incoherency": {
        "description": "Nonsensical messages will be flagged.",
        "attribute": "INCOHERENT",
        "settings": {
            "enabled": {
                "restrict": "values",
                "values": ["on", "off"],
            },
            "threshold": {
                "restrict": "range",
                "range": [0, 100],
            },
        },
    },
    "inflammatory": {
        "description": "Comments made to provoke or inflame will be flagged.",
        "attribute": "INFLAMMATORY",
        "settings": {
            "enabled": {
                "restrict": "values",
                "values": ["on", "off"],
            },
            "threshold": {
                "restrict": "range",
                "range": [0, 100],
            },
        },
    },
}

attributeConv = {
    "toxicityFiltering": "TOXICITY",
    "abusiveFiltering": "SEVERE_TOXICITY",
    "identity_attackFiltering": "IDENTITY_ATTACK",
    "insultsFiltering": "INSULT",
    "profanityFiltering": "PROFANITY",
    "threatsFiltering": "THREAT",
    "sexualFiltering": "SEXUALLY_EXPLICIT",
    "flirtationFiltering": "FLIRTATION",
    "incoherencyFiltering": "INCOHERENT",
    "inflammatoryFiltering": "INFLAMMATORY",
}

describeSettings = {
    "prefixes": "A list of prefixes to call the bot by",
    "deleteComments": "Whether or not to delete flagged comments",
}

dashboardRoot = "127.0.0.1:5000/dashboard"
