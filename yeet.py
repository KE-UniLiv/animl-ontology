
import requests

# Path to your local TTL file
ttl_file_path = "infinite.ttl"

# The URI you want to assign to the named graph
graph_uri = "https://example.org/testcases/infinite"

# Fuseki dataset endpoint
fuseki_url = f"http://localhost:3030/yourDataset/data?graph={graph_uri}"

# Read the TTL file
with open(ttl_file_path, "rb") as f:
    ttl_data = f.read()

# Send the PUT request
headers = {"Content-Type": "text/turtle"}
response = requests.put(fuseki_url, data=ttl_data, headers=headers)

# Check the response
if response.status_code in [200, 201, 204]:
    print("Upload successful!")
else:
    print(f"Upload failed: {response.status_code}")
    print(response.text)
