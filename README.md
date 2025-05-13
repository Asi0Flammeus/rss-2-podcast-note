# RSS Podcast Notes Generator

A Python tool that fetches content from multiple RSS feeds, analyzes recent articles, and generates structured podcast program notes using Anthropic's Claude AI.

## Features

- **Multiple RSS Feed Support**: Select one or more feeds from your configured sources
- **Customizable Time Range**: Filter articles from the past 1-4 weeks
- **Adjustable Technical Depth**: Set the technical level (0-5) based on your audience
- **AI-Generated Program Notes**: Uses Anthropic's Claude to create structured podcast topics
- **Flexible Output**: Generates markdown files with organized program notes
- **Feed Sorting**: Sort your feed list alphabetically for easier selection

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/rss-podcast-notes-generator.git
   cd rss-podcast-notes-generator
   ```

2. Install required dependencies:

   ```bash
   pip install feedparser python-dateutil anthropic python-dotenv
   ```

3. Create a `.env` file with your Anthropic API key:

   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

4. Create a `rss_feeds.json` file with your RSS feeds:
   ```json
   {
     "Feed Name 1": "https://example.com/feed.xml",
     "Feed Name 2": "https://another-site.com/rss"
   }
   ```

## Usage

Run the script:

```bash
python podcast_notes_generator.py
```

Follow the interactive prompts:

1. Choose how to sort your RSS feeds (alphabetical or default order)
2. Select one or more feeds from the list (comma-separated numbers)
3. Choose the time period for articles (1-4 weeks)
4. Specify the number of topics for the program notes (1-5)
5. Set the technical depth level (0-5)

The script will:

- Fetch articles from the selected feeds
- Filter them based on the chosen time period
- Generate podcast program notes using Claude
- Save the notes to a markdown file in the `output` directory

## Example Output

The generated program notes follow this structure:

```
# Weekly Podcast Program Notes

## Topic 1: Catchy Title for First Topic

Brief summary of what this topic covers and why it's relevant.

Key points:

- Important point about the topic
- Technical detail or interesting fact
- Controversial aspect or future implication

Related articles: [1, 3] from [Feed Name 1, Feed Name 2]

## Topic 2: Another Interesting Topic

...and so on
```

## Configuration

### RSS Feeds

The `rss_feeds.json` file should contain a JSON object mapping feed names to their URLs:

```json
{
  "@lightcoin": "https://lightco.in/feed/",
  "Bitcoin Optech": "https://bitcoinops.org/feed.xml",
  "Lyn Alden": "https://www.lynalden.com/feed/"
}
```

### Environment Variables

Create a `.env` file with:

- `ANTHROPIC_API_KEY`: Your Anthropic API key for Claude

## Customization

- Modify the prompt in the `generate_program_notes` method to change the style or format of the generated notes
- Adjust the model parameters (temperature, max_tokens) to control the output style
- Edit the sorting options in the `sort_feeds` method to add different sorting criteria

## Requirements

- Python 3.7+
- feedparser
- python-dateutil
- anthropic
- python-dotenv

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
