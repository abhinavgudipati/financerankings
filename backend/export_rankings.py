import json
from ranking import compute_rankings

data = compute_rankings(2016, 2024)

with open("../financerankings-site/rankings_detailed.json", "w") as f:
    json.dump(data, f, indent=2)

print("Exported rankings.json")