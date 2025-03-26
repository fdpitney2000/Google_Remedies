import json
import pandas as pd

# Load your original data
with open('your_data_file.json', 'r') as file:
    original_data = json.load(file)

# Load the search results
with open('search_results.json', 'r') as file:
    search_results = json.load(file)

# Create a list to store matches
matches = []
no_matches = []

# Create counters for statistics
total_entities = len(original_data)
entities_with_matches = 0
entities_in_top_3 = 0
entities_in_top_5 = 0

# Check each entity
for entity in original_data:
    # Construct the search query that would have been used
    search_query = f"{entity['sub2']} Whidbey"
    entity_url = entity['url'].lower()  # Normalize URL for comparison
    
    # Remove http/https and trailing slashes for more accurate comparison
    if entity_url.startswith('http://'):
        entity_url = entity_url[7:]
    elif entity_url.startswith('https://'):
        entity_url = entity_url[8:]
    if entity_url.endswith('/'):
        entity_url = entity_url[:-1]
    
    # Check if we have results for this search query
    if search_query in search_results:
        # Check if the entity's URL appears in the search results
        found = False
        position = -1
        
        # Normalize search result URLs the same way
        for idx, result_url in enumerate(search_results[search_query]):
            normalized_result = result_url.lower()
            if normalized_result.startswith('http://'):
                normalized_result = normalized_result[7:]
            elif normalized_result.startswith('https://'):
                normalized_result = normalized_result[8:]
            if normalized_result.endswith('/'):
                normalized_result = normalized_result[:-1]
            
            # Check if the normalized URL matches or is contained within the result
            if entity_url == normalized_result or entity_url in normalized_result:
                found = True
                position = idx + 1  # Convert to 1-based indexing
                break
        
        # Record the result
        if found:
            entities_with_matches += 1
            
            if position <= 3:
                entities_in_top_3 += 1
            if position <= 5:
                entities_in_top_5 += 1
                
            matches.append({
                'business': entity['business'],
                'url': entity['url'],
                'search_query': search_query,
                'position': position
            })
        else:
            no_matches.append({
                'business': entity['business'],
                'url': entity['url'],
                'search_query': search_query
            })
    else:
        # No search results for this query
        no_matches.append({
            'business': entity['business'],
            'url': entity['url'],
            'search_query': search_query,
            'reason': 'No search results found for this query'
        })

# Calculate percentages
match_percentage = (entities_with_matches / total_entities) * 100
top_3_percentage = (entities_in_top_3 / total_entities) * 100
top_5_percentage = (entities_in_top_5 / total_entities) * 100

# Print summary statistics
print(f"Total entities analyzed: {total_entities}")
print(f"Entities found in search results: {entities_with_matches} ({match_percentage:.2f}%)")
print(f"Entities in top 3 results: {entities_in_top_3} ({top_3_percentage:.2f}%)")
print(f"Entities in top 5 results: {entities_in_top_5} ({top_5_percentage:.2f}%)")

# Save the results
pd.DataFrame(matches).to_csv('url_matches.csv', index=False)
pd.DataFrame(no_matches).to_csv('url_no_matches.csv', index=False)

# Create a more detailed report
report = {
    'summary': {
        'total_entities': total_entities,
        'entities_with_matches': entities_with_matches,
        'match_percentage': match_percentage,
        'entities_in_top_3': entities_in_top_3,
        'top_3_percentage': top_3_percentage,
        'entities_in_top_5': entities_in_top_5,
        'top_5_percentage': top_5_percentage
    },
    'matches': matches,
    'no_matches': no_matches
}

# Save the detailed report as JSON
with open('search_visibility_report.json', 'w') as f:
    json.dump(report, f, indent=4)

print("\nAnalysis complete! Results saved to:")
print("- url_matches.csv: Entities found in search results")
print("- url_no_matches.csv: Entities not found in search results")
print("- search_visibility_report.json: Detailed report with all statistics")