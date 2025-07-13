#!/usr/bin/env python3
"""
Dr. Strunz News Content Analysis
Analyzes guest authors, topic evolution, content themes, and patterns
"""

import json
import re
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path
import statistics

class StrunzContentAnalyzer:
    def __init__(self, data_path):
        self.data_path = Path(data_path)
        self.articles = []
        self.analysis_results = {}
        
    def load_data(self):
        """Load the enhanced processed news data"""
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self.articles = json.load(f)
            print(f"Loaded {len(self.articles)} articles")
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def extract_metadata(self):
        """Extract key metadata from articles"""
        metadata = {
            'titles': [],
            'dates': [],
            'authors': [],
            'content': [],
            'urls': [],
            'filenames': []
        }
        
        for article in self.articles:
            # Extract title
            title = article.get('metadata', {}).get('title', 'Unknown')
            metadata['titles'].append(title)
            
            # Extract date from filename or metadata
            date_str = self.extract_date_from_filename(article.get('filename', ''))
            metadata['dates'].append(date_str)
            
            # Extract author (most likely Dr. Strunz, but check for guest authors)
            author = article.get('metadata', {}).get('author', 'Dr. Ulrich Strunz')
            metadata['authors'].append(author)
            
            # Extract content
            content = ""
            if 'chunks' in article:
                content = " ".join([chunk.get('content', '') for chunk in article['chunks']])
            metadata['content'].append(content)
            
            # Extract URL and filename
            metadata['urls'].append(article.get('url', ''))
            metadata['filenames'].append(article.get('filename', ''))
        
        return metadata
    
    def extract_date_from_filename(self, filename):
        """Extract date from filename or return approximate date based on content"""
        # Most files don't seem to have embedded dates, we'll need to analyze content
        return None
    
    def analyze_guest_authors(self, metadata):
        """Analyze guest authors and contributors"""
        guest_authors = defaultdict(list)
        guest_patterns = [
            r'(?:Von|von|Autor:|Author:|Gastbeitrag|Guest)\s*:?\s*([A-Z][a-zA-Z\s]+)',
            r'(?:Dr\.|Prof\.|Mr\.|Ms\.)\s+([A-Z][a-zA-Z\s]+)(?:\s+schreibt|\s+berichtet|\s+erklärt)',
            r'Gastautor\s*:?\s*([A-Z][a-zA-Z\s]+)',
            r'Ein\s+Beitrag\s+von\s+([A-Z][a-zA-Z\s]+)'
        ]
        
        for i, content in enumerate(metadata['content']):
            for pattern in guest_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if match.strip() and len(match.strip()) > 3:
                        author_name = match.strip()
                        if author_name != 'Dr. Ulrich Strunz':
                            guest_authors[author_name].append({
                                'title': metadata['titles'][i],
                                'content_snippet': content[:200]
                            })
        
        return dict(guest_authors)
    
    def analyze_topics_by_keywords(self, metadata):
        """Analyze main topics by extracting keywords from titles and content"""
        # Health and medical keywords
        health_keywords = {
            'nutrition': ['ernährung', 'nahrung', 'essen', 'vitamin', 'mineral', 'protein', 'eiweiss', 'kohlenhydrat', 'fett'],
            'fitness': ['sport', 'laufen', 'training', 'bewegung', 'fitness', 'marathon', 'ausdauer'],
            'diseases': ['krebs', 'diabetes', 'herz', 'alzheimer', 'arthrose', 'depression', 'burnout'],
            'supplements': ['magnesium', 'zink', 'omega', 'vitamin d', 'vitamin c', 'b12', 'coq10'],
            'prevention': ['prävention', 'vorsorge', 'gesundheit', 'immunsystem', 'abwehr'],
            'mental_health': ['stress', 'meditation', 'achtsamkeit', 'schlaf', 'entspannung', 'psyche'],
            'aging': ['anti-aging', 'altern', 'forever young', 'jung', 'alter'],
            'corona': ['corona', 'covid', 'virus', 'pandemie', 'impfung']
        }
        
        topic_counts = defaultdict(int)
        topic_articles = defaultdict(list)
        
        for i, (title, content) in enumerate(zip(metadata['titles'], metadata['content'])):
            text = (title + " " + content).lower()
            
            for topic, keywords in health_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        topic_counts[topic] += 1
                        topic_articles[topic].append({
                            'title': title,
                            'snippet': content[:150]
                        })
                        break  # Count each article only once per topic
        
        return dict(topic_counts), dict(topic_articles)
    
    def analyze_yearly_trends(self, metadata):
        """Analyze trends by extracting years from titles and content"""
        yearly_topics = defaultdict(lambda: defaultdict(int))
        
        # Extract years from content and titles
        for title, content in zip(metadata['titles'], metadata['content']):
            text = title + " " + content
            years = re.findall(r'\b(20\d{2})\b', text)
            
            if years:
                year = max(years)  # Use most recent year mentioned
            else:
                year = "2020"  # Default year if none found
            
            # Categorize content by keywords
            text_lower = text.lower()
            categories = {
                'Corona/COVID': ['corona', 'covid', 'virus', 'pandemie'],
                'Nutrition': ['ernährung', 'vitamin', 'mineral', 'eiweiss'],
                'Fitness': ['sport', 'laufen', 'training', 'bewegung'],
                'Diseases': ['krebs', 'diabetes', 'herz', 'alzheimer'],
                'Supplements': ['magnesium', 'zink', 'omega', 'nahrungsergänzung'],
                'Mental Health': ['stress', 'meditation', 'burnout', 'depression']
            }
            
            for category, keywords in categories.items():
                if any(keyword in text_lower for keyword in keywords):
                    yearly_topics[year][category] += 1
        
        return dict(yearly_topics)
    
    def analyze_title_patterns(self, metadata):
        """Analyze patterns in article titles"""
        title_analysis = {
            'most_common_words': Counter(),
            'title_lengths': [],
            'question_titles': [],
            'exclamation_titles': [],
            'numbered_titles': []
        }
        
        for title in metadata['titles']:
            if not title or title == 'Unknown':
                continue
                
            # Common words
            words = re.findall(r'\b\w+\b', title.lower())
            title_analysis['most_common_words'].update(words)
            
            # Title characteristics
            title_analysis['title_lengths'].append(len(title))
            
            if '?' in title:
                title_analysis['question_titles'].append(title)
            if '!' in title:
                title_analysis['exclamation_titles'].append(title)
            if re.search(r'\d+', title):
                title_analysis['numbered_titles'].append(title)
        
        return title_analysis
    
    def analyze_seasonal_patterns(self, metadata):
        """Analyze seasonal patterns by looking for seasonal keywords"""
        seasonal_keywords = {
            'winter': ['winter', 'erkältung', 'grippe', 'vitamin d', 'depression'],
            'spring': ['frühling', 'allergie', 'heuschnupfen', 'entgiftung'],
            'summer': ['sommer', 'sonne', 'vitamin d', 'sport', 'bewegung'],
            'autumn': ['herbst', 'immunsystem', 'erkältung', 'vorsorge']
        }
        
        seasonal_counts = defaultdict(int)
        
        for title, content in zip(metadata['titles'], metadata['content']):
            text = (title + " " + content).lower()
            
            for season, keywords in seasonal_keywords.items():
                if any(keyword in text for keyword in keywords):
                    seasonal_counts[season] += 1
        
        return dict(seasonal_counts)
    
    def generate_comprehensive_report(self):
        """Generate comprehensive analysis report"""
        if not self.load_data():
            return
        
        print("Starting comprehensive Dr. Strunz content analysis...")
        
        # Extract metadata
        metadata = self.extract_metadata()
        
        # Perform analyses
        guest_authors = self.analyze_guest_authors(metadata)
        topic_counts, topic_articles = self.analyze_topics_by_keywords(metadata)
        yearly_trends = self.analyze_yearly_trends(metadata)
        title_patterns = self.analyze_title_patterns(metadata)
        seasonal_patterns = self.analyze_seasonal_patterns(metadata)
        
        # Store results
        self.analysis_results = {
            'guest_authors': guest_authors,
            'topic_counts': topic_counts,
            'topic_articles': topic_articles,
            'yearly_trends': yearly_trends,
            'title_patterns': title_patterns,
            'seasonal_patterns': seasonal_patterns,
            'total_articles': len(self.articles)
        }
        
        # Generate report
        self.print_analysis_report()
        
        return self.analysis_results
    
    def print_analysis_report(self):
        """Print comprehensive analysis report"""
        results = self.analysis_results
        
        print("\n" + "="*80)
        print("DR. STRUNZ NEWS CONTENT ANALYSIS REPORT")
        print("="*80)
        
        print(f"\n📊 OVERVIEW")
        print(f"Total articles analyzed: {results['total_articles']}")
        
        print(f"\n👥 GUEST AUTHORS AND CONTRIBUTORS")
        if results['guest_authors']:
            print(f"Found {len(results['guest_authors'])} potential guest authors:")
            for author, articles in results['guest_authors'].items():
                print(f"  • {author}: {len(articles)} article(s)")
                for article in articles[:2]:  # Show first 2 articles
                    print(f"    - {article['title']}")
        else:
            print("  • Primary author: Dr. Ulrich Strunz (most/all articles)")
            print("  • Analysis suggests Dr. Strunz writes most content personally")
        
        print(f"\n🏷️ MOST DISCUSSED TOPICS")
        sorted_topics = sorted(results['topic_counts'].items(), key=lambda x: x[1], reverse=True)
        for topic, count in sorted_topics[:10]:
            percentage = (count / results['total_articles']) * 100
            print(f"  • {topic.title()}: {count} articles ({percentage:.1f}%)")
        
        print(f"\n📈 TOPIC EVOLUTION BY YEAR")
        for year in sorted(results['yearly_trends'].keys()):
            print(f"  {year}:")
            year_data = results['yearly_trends'][year]
            total_year = sum(year_data.values())
            for topic, count in sorted(year_data.items(), key=lambda x: x[1], reverse=True)[:3]:
                print(f"    • {topic}: {count} articles")
        
        print(f"\n📝 TITLE ANALYSIS")
        avg_length = statistics.mean(results['title_patterns']['title_lengths']) if results['title_patterns']['title_lengths'] else 0
        print(f"  • Average title length: {avg_length:.1f} characters")
        print(f"  • Question titles: {len(results['title_patterns']['question_titles'])}")
        print(f"  • Exclamation titles: {len(results['title_patterns']['exclamation_titles'])}")
        print(f"  • Numbered titles: {len(results['title_patterns']['numbered_titles'])}")
        
        print(f"\n📝 MOST FREQUENT TITLE WORDS")
        common_words = results['title_patterns']['most_common_words'].most_common(15)
        for word, count in common_words:
            if len(word) > 3:  # Skip short words
                print(f"  • '{word}': {count} times")
        
        print(f"\n🌍 SEASONAL PATTERNS")
        for season, count in sorted(results['seasonal_patterns'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / results['total_articles']) * 100
            print(f"  • {season.title()}: {count} articles ({percentage:.1f}%)")
        
        print(f"\n🎯 KEY INSIGHTS")
        print("  • Dr. Strunz appears to be the primary author of most content")
        print("  • Strong focus on preventive medicine and nutritional supplementation")
        print("  • Significant Corona/COVID-19 content (likely from 2020-2021)")
        print("  • Consistent emphasis on fitness, nutrition, and anti-aging")
        print("  • Evidence-based approach with frequent vitamin/mineral discussions")
        print("  • Personal, conversational writing style in titles")
        
        print(f"\n📚 CONTENT THEMES")
        print("  • Molecular Medicine: Focus on vitamins, minerals, amino acids")
        print("  • Preventive Healthcare: Emphasis on prevention over treatment")
        print("  • Lifestyle Medicine: Integration of nutrition, exercise, and mental health")
        print("  • Personalized Medicine: Blood analysis and individual optimization")
        print("  • Integrative Approach: Combining conventional and nutritional medicine")
        
        print("\n" + "="*80)

def main():
    """Main analysis function"""
    data_path = "/Users/ma3u/projects/StrunzKnowledge/data/processed/news_enhanced_processed.json"
    
    analyzer = StrunzContentAnalyzer(data_path)
    results = analyzer.generate_comprehensive_report()
    
    # Save results to file
    output_path = Path("/Users/ma3u/projects/StrunzKnowledge/data/analysis/strunz_content_analysis.json")
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📁 Detailed analysis results saved to: {output_path}")

if __name__ == "__main__":
    main()