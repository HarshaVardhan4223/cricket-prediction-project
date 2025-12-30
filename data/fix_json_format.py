
import json

# Read JSONL file
input_file = r'E:\cricket-prediction-project\data\global_cricket_players.json'
output_file = r'E:\cricket-prediction-project\data\global_cricket_players_fixed.json'

try:
    players = []
    with open(input_file, 'r') as f:
        for line in f:
            if line.strip():  # Skip empty lines
                player = json.loads(line)
                players.append(player)
    
    # Write as proper JSON array
    with open(output_file, 'w') as f:
        json.dump(players, f, indent=2)
    
    print(f"✅ Fixed JSON file saved to {output_file}")
except Exception as e:
    print(f"❌ Error fixing JSON: {e}")
