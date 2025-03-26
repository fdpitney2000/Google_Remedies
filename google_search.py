import json
import time
import pandas as pd
from googlesearch import search

# Load your JSON data
with open('your_data_file.json', 'r') as file:
    data = json.load(file)

# Prepare to store results
search_results = {}  # Use a dictionary to track unique searches
unique_searches = set()  # Track unique search terms

# First, identify all unique search queries
for record in data:
    search_query = f"{record['sub2']} Whidbey"
    unique_searches.add(search_query)

print(f"Found {len(unique_searches)} unique searches out of {len(data)} records")

# Process each unique search query
for idx, search_query in enumerate(unique_searches):
    print(f"Searching for: {search_query} ({idx+1}/{len(unique_searches)})")
    
    # Skip if we already have results for this query
    if search_query in search_results:
        print(f"Skipping duplicate search: {search_query}")
        continue
    
    # Get the first 10 Google search results
    urls = []
    try:
        for url in search(search_query, num_results=10):
            urls.append(url)
            # Small delay to be respectful to Google
            time.sleep(1)
    except Exception as e:
        print(f"Error searching for '{search_query}': {e}")
    
    # Store this search result
    search_results[search_query] = urls
    
    # Pause between searches to be respectful to Google
    time.sleep(2)
    
    # Save intermediate results after every 5 searches
    if (idx + 1) % 5 == 0 or idx == len(unique_searches) - 1:
        # Save as JSON
        with open('search_results.json', 'w') as f:
            json.dump(search_results, f, indent=4)
        
        # Save as CSV (flattened format with business info)
        csv_data = []
        
        # For CSV, we need to associate each business with its search results
        for record in data:
            record_search_query = f"{record['sub2']} Whidbey"
            if record_search_query in search_results:
                for i, url in enumerate(search_results[record_search_query]):
                    csv_data.append({
                        "search_query": record_search_query,
                        "business": record["business"],
                        "category": record["category"],
                        "sub1": record["sub1"],
                        "sub2": record["sub2"],
                        "result_number": i + 1,
                        "url": url
                    })
        
        pd.DataFrame(csv_data).to_csv('search_results.csv', index=False)
        print(f"Saved results after processing {idx+1}/{len(unique_searches)} unique searches")

print("Completed all searches!")