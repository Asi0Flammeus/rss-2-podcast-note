import os
import sys
import json
import feedparser
import datetime
import anthropic
from dotenv import load_dotenv
from dateutil import parser
import time
from typing import List, Dict, Any, Optional
import re

# Load environment variables
load_dotenv()

class RSSPodcastNoteGenerator:
    def __init__(self):
        # Get API key from environment variables
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            print("Error: ANTHROPIC_API_KEY not found in .env file")
            sys.exit(1)
            
        # Initialize Anthropic client
        self.client = anthropic.Anthropic(api_key=self.api_key)
        
        # Load RSS feeds from JSON file
        self.rss_feeds = self.load_rss_feeds("rss_feeds.json")
        
        if not self.rss_feeds:
            # Default feed if none specified in JSON
            self.rss_feeds = {
                "Stacker News": "https://stacker.news/rss",
                "Hacker News": "https://news.ycombinator.com/rss",
                "Bitcoin Magazine": "https://bitcoinmagazine.com/.rss/full/"
            }
            
        # Create output directory if it doesn't exist
        self.output_dir = "output"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def load_rss_feeds(self, json_file_path: str) -> Dict[str, str]:
        """Load RSS feeds from JSON file."""
        try:
            if os.path.exists(json_file_path):
                with open(json_file_path, 'r') as f:
                    return json.load(f)
            else:
                print(f"Warning: RSS feeds file {json_file_path} not found. Using defaults.")
                return {}
        except Exception as e:
            print(f"Error loading RSS feeds from {json_file_path}: {e}")
            return {}

    def fetch_rss_feed(self, url: str) -> List[Dict[str, Any]]:
        """Fetch and parse an RSS feed."""
        try:
            feed = feedparser.parse(url)
            return feed.entries
        except Exception as e:
            print(f"Error fetching RSS feed from {url}: {e}")
            return []

    def filter_entries_by_date(self, entries: List[Dict[str, Any]], weeks_ago: int) -> List[Dict[str, Any]]:
        """Filter entries based on publication date."""
        now = datetime.datetime.now(datetime.timezone.utc)
        cutoff_date = now - datetime.timedelta(weeks=weeks_ago)
        
        filtered_entries = []
        for entry in entries:
            # Try to parse the published date
            try:
                if 'published_parsed' in entry and entry.published_parsed:
                    pub_date = datetime.datetime(*entry.published_parsed[:6], tzinfo=datetime.timezone.utc)
                elif 'published' in entry:
                    pub_date = parser.parse(entry.published)
                elif 'updated_parsed' in entry and entry.updated_parsed:
                    pub_date = datetime.datetime(*entry.updated_parsed[:6], tzinfo=datetime.timezone.utc)
                elif 'updated' in entry:
                    pub_date = parser.parse(entry.updated)
                else:
                    # Skip entries without dates
                    continue
                
                if pub_date >= cutoff_date:
                    filtered_entries.append(entry)
            except Exception as e:
                print(f"Error parsing date for entry: {e}")
                continue
                
        return filtered_entries

    def generate_program_notes(self, entries: List[Dict[str, Any]], num_topics: int, tech_level: int) -> str:
        """Generate podcast program notes using Anthropic's Claude."""
        if not entries:
            return "No entries found for the selected time period."
        
        # Prepare content for Claude
        content = "Here are recent articles from an RSS feed:\n\n"
        
        for i, entry in enumerate(entries[:20]):  # Limit to 20 entries to avoid token limits
            title = entry.get('title', 'No title')
            link = entry.get('link', 'No link')
            
            # Try to get summary or content
            summary = ""
            if 'summary' in entry:
                summary = entry.get('summary', '')
            elif 'content' in entry and entry.content:
                for content_item in entry.content:
                    if 'value' in content_item:
                        summary = content_item.value
                        break
            
            # Clean HTML tags from summary
            summary = re.sub(r'<[^>]+>', '', summary)
            
            # Get published date
            published = ""
            if 'published' in entry:
                published = entry.get('published', '')
            elif 'updated' in entry:
                published = entry.get('updated', '')
            
            content += f"Article {i+1}:\n"
            content += f"Title: {title}\n"
            content += f"Link: {link}\n"
            content += f"Published: {published}\n"
            content += f"Summary: {summary[:500]}...\n\n"  # Limit summary length
        
        # Create prompt for Claude
        prompt = f"""
Based on the articles provided, create program notes for a weekly podcast episode.
The notes should cover {num_topics} main topics from these articles.

Technical depth level: {tech_level}/5 (where 0 is non-technical and 5 is highly technical)

For each topic:
1. Create a catchy title
2. Write a brief summary (2-3 sentences)
3. Include key points for discussion (3-5 bullet points)
4. Mention relevant articles from the list

Here are the articles:
{content}

Format the response as:
# Weekly Podcast Program Notes

## Topic 1: [Catchy Title]
[Brief summary]

Key points:
- [Point 1]
- [Point 2]
- [Point 3]

Related articles: [Article url]

## Topic 2: [Catchy Title]
...and so on
"""

        try:
            response = self.client.messages.create(
                model="claude-3-7-sonnet-latest",
                max_tokens=4000,
                temperature=0.7,
                system="You are an expert podcast producer who creates concise, informative program notes.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            print(f"Error generating program notes: {e}")
            return "Failed to generate program notes. Please try again."

    def run(self):
        """Main execution flow."""
        # Display available RSS feeds
        print("\n=== Available RSS Feeds ===")
        feed_names = list(self.rss_feeds.keys())
        for i, name in enumerate(feed_names):
            print(f"{i+1}. {name}")
        
        # Get user selection for RSS feed
        while True:
            try:
                feed_choice = int(input("\nSelect a feed (number): ")) - 1
                if 0 <= feed_choice < len(feed_names):
                    selected_feed_name = feed_names[feed_choice]
                    selected_feed_url = self.rss_feeds[selected_feed_name]
                    break
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a number.")
        
        print(f"\nFetching {selected_feed_name} feed...")
        entries = self.fetch_rss_feed(selected_feed_url)
        
        if not entries:
            print("No entries found in the feed. Exiting.")
            return
            
        print(f"Found {len(entries)} entries in the feed.")
        
        # Get time period selection
        print("\n=== Select Time Period ===")
        print("1. Past week")
        print("2. Past 2 weeks")
        print("3. Past 3 weeks")
        print("4. Past 4 weeks")
        
        while True:
            try:
                weeks_choice = int(input("\nSelect time period (number): "))
                if 1 <= weeks_choice <= 4:
                    weeks_ago = weeks_choice
                    break
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a number.")
        
        # Filter entries by date
        filtered_entries = self.filter_entries_by_date(entries, weeks_ago)
        print(f"\nFound {len(filtered_entries)} entries from the past {weeks_ago} week(s).")
        
        if not filtered_entries:
            print("No entries found for the selected time period. Exiting.")
            return
        
        # Get number of topics
        while True:
            try:
                num_topics = int(input("\nHow many topics for the program notes? (1-5): "))
                if 1 <= num_topics <= 5:
                    break
                else:
                    print("Please enter a number between 1 and 5.")
            except ValueError:
                print("Please enter a number.")
        
        # Get technical level
        while True:
            try:
                tech_level = int(input("\nTechnical depth level (0-5, where 0 is non-technical and 5 is highly technical): "))
                if 0 <= tech_level <= 5:
                    break
                else:
                    print("Please enter a number between 0 and 5.")
            except ValueError:
                print("Please enter a number.")
        
        print("\nGenerating podcast program notes...")
        program_notes = self.generate_program_notes(filtered_entries, num_topics, tech_level)
        
        # Display and save results
        print("\n=== Podcast Program Notes ===\n")
        print(program_notes)
        
        # Save to file in the output directory
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_feed_name = selected_feed_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
        filename = f"{safe_feed_name}_{timestamp}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(program_notes)
        
        print(f"\nProgram notes saved to {filepath}")

if __name__ == "__main__":
    print("=== RSS Podcast Note Generator ===")
    generator = RSSPodcastNoteGenerator()
    generator.run()
