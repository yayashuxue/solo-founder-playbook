import csv
import os

# Category mapping: old -> new
CATEGORY_MAPPING = {
    # Background variations
    'Background/Journey': 'Advice/Lessons',
    'Background/Origin Story': 'Advice/Lessons',
    'Career Change': 'Advice/Lessons',
    'Personal Philosophy': 'Advice/Lessons',
    
    # Building variations
    'Building Skills/Development': 'Building/Development',
    'Building/Development - AI Coding': 'Building/Development',
    'Design': 'Building/Development',
    
    # Challenges variations
    'Challenges/Sacrifice': 'Challenges/Failures',
    'Overcoming Adversity': 'Challenges/Failures',
    'Competition': 'Challenges/Failures',
    
    # Growth variations
    'Growth - Paid Ads': 'Growth',
    'Growth - Scaling from Freelancer to Agency': 'Growth',
    'Growth/Fundraising': 'Growth',
    
    # Marketing variations
    'Marketing/Distribution - Networking': 'Marketing/Distribution',
    'Paid Advertising': 'Marketing/Distribution',
    'Platform Strategy': 'Marketing/Distribution',
    'Platform Strategy Framework': 'Marketing/Distribution',
    'Content Creation': 'Marketing/Distribution',
    'Branding': 'Marketing/Distribution',
    
    # Monetization variations
    'Monetization - Onboarding & Conversion': 'Monetization',
    'Monetization Strategy': 'Monetization',
    
    # Validation variations
    'User Testing/Feedback': 'Validation',
    'Customer Discovery': 'Validation',
    
    # Launch variations
    'Getting Started/First Client': 'Launch',
    'Market Opportunity': 'Idea Generation',
    'Tools/Productivity': 'Building/Development',
}

# Standard categories
STANDARD_CATEGORIES = [
    'Idea Generation',
    'Validation',
    'Building/Development',
    'Launch',
    'Marketing/Distribution',
    'Growth',
    'Monetization',
    'Challenges/Failures',
    'Team/Hiring',
    'Cost/Expenses',
    'Advice/Lessons'
]

def merge_csv_categories(input_file='chapters_analysis.csv', output_file='chapters_analysis_merged.csv'):
    """Merge duplicate categories in the CSV file"""
    
    if not os.path.exists(input_file):
        print(f"❌ Error: {input_file} not found")
        return
    
    # Read all rows
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"📊 Processing {len(rows)} videos...")
    
    # Process each row
    merged_rows = []
    for row in rows:
        # Start with basic info
        new_row = {
            'video_id': row['video_id'],
            'video_title': row['video_title'],
            'video_url': row['video_url']
        }
        
        # Initialize standard categories
        for cat in STANDARD_CATEGORIES:
            new_row[cat] = ''
        
        # Merge content from old categories to new
        for old_col, content in row.items():
            if old_col in ['video_id', 'video_title', 'video_url']:
                continue
            
            if not content:  # Skip empty cells
                continue
            
            # Determine target category
            target_cat = CATEGORY_MAPPING.get(old_col, old_col)
            
            # If target is a standard category, append content
            if target_cat in STANDARD_CATEGORIES:
                if new_row[target_cat]:
                    new_row[target_cat] += ' ' + content
                else:
                    new_row[target_cat] = content
        
        merged_rows.append(new_row)
    
    # Write merged CSV
    fieldnames = ['video_id', 'video_title', 'video_url'] + STANDARD_CATEGORIES
    
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(merged_rows)
    
    print(f"\n✅ Merged CSV saved to: {output_file}")
    print(f"📂 Standard categories: {len(STANDARD_CATEGORIES)}")
    print(f"\n📊 Categories:")
    for cat in STANDARD_CATEGORIES:
        count = sum(1 for row in merged_rows if row[cat])
        print(f"   - {cat}: {count} videos")
    
    # Show what was merged
    print(f"\n🔀 Merged categories:")
    for old, new in sorted(CATEGORY_MAPPING.items()):
        print(f"   {old} → {new}")

if __name__ == "__main__":
    merge_csv_categories()
    
    # Ask if user wants to replace original
    print("\n" + "="*70)
    response = input("Replace original chapters_analysis.csv with merged version? (y/n): ")
    if response.lower() == 'y':
        import shutil
        shutil.move('chapters_analysis_merged.csv', 'chapters_analysis.csv')
        print("✅ Replaced original file!")
    else:
        print("📁 Kept both files (original + merged)")

