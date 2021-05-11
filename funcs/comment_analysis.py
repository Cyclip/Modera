from googleapiclient import discovery
import os
from dotenv import load_dotenv

load_dotenv()

client = discovery.build(
    "commentanalyzer",
    "v1alpha1",
    developerKey=os.getenv("CLOUD_API_KEY"),
    discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
    static_discovery=False,
)


def request(text):
    req = {
        "comment": {"text": text},
        "requestedAttributes": {
            "TOXICITY": {},
            "SEVERE_TOXICITY": {},
            "IDENTITY_ATTACK": {},
            "INSULT": {},
            "PROFANITY": {},
            "THREAT": {},
            "SEXUALLY_EXPLICIT": {},
            "FLIRTATION": {},
            "INCOHERENT": {},
            "INFLAMMATORY": {},
        },
        "doNotStore": True,
        "spanAnnotations": True,
        "languages": ["en"],
    }

    return client.comments().analyze(body=req).execute()["attributeScores"]
