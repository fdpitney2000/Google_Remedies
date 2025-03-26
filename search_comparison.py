import json
import time
import pandas as pd
from googlesearch import search

# Load your JSON data files
with open('your_data_file.json', 'r') as file:
    business_data = json.load(file)

with open('30searches.json', 'r') as file:
    search_phrases = json.load(file)['search_phrases']

# Extract all business URLs for easier comparison
business_urls = []
for business in business_data:
    url = business['url'].lower()
    # Normalize URL
    if url.startswith('http://'):
        url = url[7:]
    elif url.startswith('https://'):
        url = url[8:]
    if url.endswith('/'):
        url = url[:-1]
    
    business_urls.append({
        'original_url': business['url'],
        'normalized_url': url,
        'business': business['business'],
        'category': business['category']
    })

# Prepare to store results
all_search_results = {}
total_matches = 0
matched_businesses = set()  # Track unique businesses that were found

# Process each search phrase
for idx, phrase in enumerate(search_phrases):
    print(f"Searching for: '{phrase}' ({idx+1}/{len(search_phrases)})")
    
    # Store results for this search
    results_for_query = []
    matches_for_query = 0
    
    # Get the first 30 Google search results
    try:
        for url in search(phrase, num_results=30):
            # Normalize the result URL for comparison
            normalized_result = url.lower()
            if normalized_result.startswith('http://'):
                normalized_result = normalized_result[7:]
            elif normalized_result.startswith('https://'):
                normalized_result = normalized_result[8:]
            if normalized_result.endswith('/'):
                normalized_result = normalized_result[:-1]
            
            # Check if this result matches any business URL
            matched_business = None
            for business in business_urls:
                if business['normalized_url'] == normalized_result or business['normalized_url'] in normalized_result:
                    matched_business = business
                    matched_businesses.add(business['original_url'])
                    total_matches += 1
                    matches_for_query += 1
                    break
            
            # Store this result
            results_for_query.append({
                'url': url,
                'normalized_url': normalized_result,
                'matches_business': matched_business is not None,
                'matched_business_name': matched_business['business'] if matched_business else None
            })
            
            # Small delay to be respectful to Google
            time.sleep(1)
    except Exception as e:
        print(f"Error searching for '{phrase}': {e}")
    
    # Add to overall results
    all_search_results[phrase] = {
        'results': results_for_query,
        'total_matches': matches_for_query
    }
    
    # Print progress
    print(f"  Found {matches_for_query} matches for this phrase")
    print(f"  Running total: {total_matches} matches across all searches")
    print(f"  Unique businesses matched so far: {len(matched_businesses)}")
    
    # Pause between searches to be respectful to Google
    time.sleep(2)
    
    # Save intermediate results after every 5 searches
    if (idx + 1) % 5 == 0 or idx == len(search_phrases) - 1:
        # Save detailed results
        with open('search_comparison_results.json', 'w') as f:
            json.dump(all_search_results, f, indent=4)
        
        # Save summary report
        summary = {
            'total_searches': idx + 1,
            'total_search_results': (idx + 1) * 30,
            'total_matches_found': total_matches,
            'match_percentage': (total_matches / ((idx + 1) * 30)) * 100,
            'unique_businesses_matched': len(matched_businesses),
            'unique_match_percentage': (len(matched_businesses) / len(business_urls)) * 100,
            'search_phrases_complete': search_phrases[:idx+1],
            'businesses_matched': list(matched_businesses)
        }
        
        with open('search_comparison_summary.json', 'w') as f:
            json.dump(summary, f, indent=4)
        
        print(f"Saved results after processing {idx+1}/{len(search_phrases)} search phrases")

# Create a CSV report
csv_data = []
for phrase, results in all_search_results.items():
    for i, result in enumerate(results['results']):
        csv_data.append({
            'search_phrase': phrase,
            'result_number': i + 1,
            'url': result['url'],
            'matches_business': result['matches_business'],
            'matched_business_name': result['matched_business_name']
        })

pd.DataFrame(csv_data).to_csv('search_comparison_results.csv', index=False)

# Final summary
print("\nSearch comparison completed!")
print(f"Total search results analyzed: {len(search_phrases) * 30}")
print(f"Total matches found: {total_matches} ({(total_matches / (len(search_phrases) * 30)) * 100:.2f}%)")
print(f"Unique businesses matched: {len(matched_businesses)} out of {len(business_urls)} ({(len(matched_businesses) / len(business_urls)) * 100:.2f}%)")
print("\nDetailed results have been saved to:")
print("- search_comparison_results.json: Full details of all searches")
print("- search_comparison_summary.json: Summary statistics")
print("- search_comparison_results.csv: CSV format for easy viewing")