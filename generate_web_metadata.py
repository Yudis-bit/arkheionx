import json
import re
from datetime import datetime
from pathlib import Path


EDUCATIONAL_INSIGHTS = {
    "Reentry": "A vulnerability where a function is called repeatedly before the initial execution is complete.",
    "Oracle": "Price manipulation exploit targeting external price feeds or decentralized exchange pools.",
    "Flashloan": "Leveraging uncollateralized instant loans to drain protocol liquidity in a single transaction.",
}

DEFAULT_INSIGHTS = [
    "A foundational case study on early smart contract logic vulnerabilities.",
    "Analyzing the evolution of attack vectors in decentralized finance.",
    "Key takeaways on state management and security best practices.",
    "Historical exploit analysis: Preventing the mistakes of the past.",
    "Strategic review of protocol architecture and its hidden risks.",
]

REMOTE_URL = "https://github.com/Yudis-bit/DeFi-Exploit-PoCs"

MONTH_NAMES = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]


def get_protocol_name_from_filename(folder_name: str, date: str) -> str:
    """Extract protocol name from folder name (YYYY-MM-Protocol), or format as Archive if date only."""
    match = re.match(r"^(\d{4}-\d{2})(?:-(.*))?$", folder_name)
    if match:
        protocol = match.group(2)
        if protocol:
            year, month = date.split("-")
            month_int = int(month)
            if month_int < 1 or month_int > 12:
                return folder_name
            return f"{protocol.replace('-', ' ')} ({MONTH_NAMES[month_int - 1]} {year})"
        year, month = date.split("-")
        month_int = int(month)
        if month_int < 1 or month_int > 12:
            return folder_name
        month_name = MONTH_NAMES[month_int - 1]
        return f"{month_name} {year} Archive"
    return folder_name


def get_educational_insight(folder_name: str, index: int) -> str:
    """Get educational insight based on folder name keywords, rotating defaults if none found."""
    for keyword, insight in EDUCATIONAL_INSIGHTS.items():
        if keyword in folder_name:
            return insight
    return DEFAULT_INSIGHTS[index % len(DEFAULT_INSIGHTS)]


def generate_metadata():
    """Generate metadata.json by scanning EVM/test/ folders."""
    test_dir = Path("EVM/test")

    if not test_dir.exists():
        raise FileNotFoundError(f"Directory {test_dir} not found")

    exploits = []
    id_counter = 1
    default_index = 0

    for folder in sorted(test_dir.iterdir()):
        if not folder.is_dir():
            continue
        if folder.name.startswith("."):
            continue

        folder_match = re.match(r"^(\d{4}-\d{2})(?:-(.*))?$", folder.name)
        if not folder_match:
            continue

        date = folder_match.group(1)
        title = get_protocol_name_from_filename(folder.name, date)
        insight = get_educational_insight(folder.name, default_index)
        link = f"{REMOTE_URL}/tree/main/EVM/test/{folder.name}"

        exploits.append({
            "id": id_counter,
            "title": title,
            "date": date,
            "tags": ["EVM", "Foundry"],
            "link": link,
            "educational_insight": insight
        })

        id_counter += 1
        default_index += 1

    metadata = {
        "author": "Yudis-bit",
        "last_update": datetime.now().isoformat(),
        "total_poc": len(exploits),
        "exploits": exploits
    }

    output_file = Path("web/public/metadata.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(metadata, indent=2))

    print(f"Generated metadata.json with {len(exploits)} PoCs")


if __name__ == "__main__":
    generate_metadata()