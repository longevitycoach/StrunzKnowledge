import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict


class MarkdownGenerator:
    def __init__(self, input_dir: str = "data/raw", output_dir: str = "data/processed"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.category_descriptions = {
            'news': 'Aktuelle Neuigkeiten und Artikel von Dr. Ulrich Strunz zu Gesundheit, Ernährung und Fitness.',
            'forum_fitness': 'Diskussionen und Expertenwissen zum Thema Sport, Training und körperliche Fitness.',
            'forum_gesundheit': 'Gesundheitliche Themen, Krankheitsprävention und ganzheitliche Heilansätze.',
            'forum_ernaehrung': 'Ernährungswissenschaft, Diätempfehlungen und praktische Ernährungstipps.',
            'forum_bluttuning': 'Optimierung der Blutwerte durch gezielte Supplementierung und Ernährung.',
            'forum_mental': 'Mentale Gesundheit, Stressbewältigung und psychisches Wohlbefinden.',
            'forum_infektion-und-praevention': 'Immunsystem stärken, Infektionsschutz und präventive Maßnahmen.'
        }
        
        self.source_urls = {
            'news': 'https://www.strunz.com/news.html',
            'forum_fitness': 'https://www.strunz.com/forum/fitness',
            'forum_gesundheit': 'https://www.strunz.com/forum/gesundheit',
            'forum_ernaehrung': 'https://www.strunz.com/forum/ernaehrung',
            'forum_bluttuning': 'https://www.strunz.com/forum/bluttuning',
            'forum_mental': 'https://www.strunz.com/forum/mental',
            'forum_infektion-und-praevention': 'https://www.strunz.com/forum/infektion-und-praevention'
        }
    
    def generate_all(self):
        """Generate markdown files for all sections."""
        json_files = list(self.input_dir.glob("*.json"))
        
        for json_file in json_files:
            if json_file.stem == "scraping_stats":
                continue
                
            self._generate_markdown(json_file)
    
    def _generate_markdown(self, json_file: Path):
        """Generate markdown file from JSON data."""
        section = json_file.stem
        
        # Load data
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Sort by date (newest first)
        data.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        # Create markdown content
        markdown_lines = [
            f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Source URL: {self.source_urls.get(section, 'Unknown')}",
            f"Summary: {self.category_descriptions.get(section, 'Keine Beschreibung verfügbar.')}",
            "",
            f"# {self._format_section_title(section)}",
            "",
            f"Anzahl der Einträge: {len(data)}",
            "",
            "---",
            ""
        ]
        
        # Add content
        for item in data:
            # Date
            if item.get('date'):
                try:
                    date = datetime.fromisoformat(item['date'])
                    date_str = date.strftime('%d.%m.%Y')
                except:
                    date_str = item['date']
            else:
                date_str = "Datum unbekannt"
            
            markdown_lines.append(f"## {date_str}")
            
            # Title
            if item.get('title'):
                markdown_lines.append(f"### {item['title']}")
            
            # Author (for forum posts)
            if item.get('author'):
                markdown_lines.append(f"**Autor:** {item['author']}")
            
            # Content
            if item.get('content'):
                # Clean up content
                content = item['content'].strip()
                # Ensure proper paragraph spacing
                content = content.replace('\n\n\n', '\n\n')
                markdown_lines.append("")
                markdown_lines.append(content)
            
            # Source URL
            if item.get('source_url'):
                markdown_lines.append("")
                markdown_lines.append(f"*Quelle: {item['source_url']}*")
            
            markdown_lines.append("")
            markdown_lines.append("---")
            markdown_lines.append("")
        
        # Write markdown file
        output_file = self.output_dir / f"{section}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(markdown_lines))
        
        print(f"Generated {output_file}")
    
    def _format_section_title(self, section: str) -> str:
        """Format section name for display."""
        title_map = {
            'news': 'News & Artikel',
            'forum_fitness': 'Forum: Fitness & Sport',
            'forum_gesundheit': 'Forum: Gesundheit',
            'forum_ernaehrung': 'Forum: Ernährung',
            'forum_bluttuning': 'Forum: Bluttuning',
            'forum_mental': 'Forum: Mental & Psyche',
            'forum_infektion-und-praevention': 'Forum: Infektion & Prävention'
        }
        return title_map.get(section, section.replace('_', ' ').title())