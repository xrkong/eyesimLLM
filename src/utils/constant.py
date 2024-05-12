from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().resolve().parents[2]

PROMPT_DIR = PROJECT_DIR / "experiment" / "prompt"

DATA_DIR = PROJECT_DIR / "experiment" / "data"

LLM_MODEL_DIR = PROJECT_DIR / "models"

LLM_MODEL_DIR.mkdir(parents=True, exist_ok=True)
PROMPT_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATA_COLLECTION_FREQUENCY = 1 # in seconds
CONTROL_EVENT_CHECK_FREQUENCY = 1 # in seconds
SAFETY_EVENT_CHECK_FREQUENCY = 1 # in seconds
