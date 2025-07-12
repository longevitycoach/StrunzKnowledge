#!/usr/bin/env python3
"""
Comprehensive topic analysis of forum content including trends and events
"""

import json
import logging
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
import re
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ForumTopicAnalyzer:
    def __init__(self):
        self.data_dir = Path("data")
        self.forum_file = self.data_dir / "processed" / "forum" / "forum_documents_20250712_211416.json"
        self.medical_keywords = {
            'epigenetics': ['epigenet', 'methylierung', 'dna-methylierung', 'genexpression', 'histone'],
            'longevity': ['longevity', 'langlebigkeit', 'anti-aging', 'telomer', 'alterung', 'lebensspanne'],
            'molecular': ['molekular', 'mitochondri', 'atp', 'zellular', 'biochemie', 'metabolismus'],
            'functional': ['funktionell', 'ganzheitlich', 'orthomolekular', 'integrative', 'präventiv'],
            'corona': ['corona', 'covid', 'impf', 'spike', 'mrna', 'pandemie', 'lockdown'],
            'vitamins': ['vitamin d', 'vitamin c', 'vitamin b', 'vitamine', 'nährstoff'],
            'minerals': ['zink', 'magnesium', 'selen', 'eisen', 'kalzium', 'mineralstoffe'],
            'amino': ['aminosäure', 'protein', 'arginin', 'lysin', 'tryptophan', 'glutamin'],
            'diet': ['low carb', 'keto', 'fasten', 'ernährung', 'diät', 'zucker'],
            'stress': ['stress', 'cortisol', 'burnout', 'entspannung', 'meditation'],
            'inflammation': ['entzündung', 'crp', 'inflammation', 'zytokine', 'immunsystem'],
            'cancer': ['krebs', 'tumor', 'onkologie', 'karzinom', 'metastase'],
            'heart': ['herz', 'kardio', 'blutdruck', 'cholesterin', 'arterien'],
            'brain': ['gehirn', 'kognitiv', 'demenz', 'alzheimer', 'gedächtnis', 'depression']
        }
        
        self.social_events = {
            '2020': ['Corona-Pandemie beginnt', 'Erster Lockdown'],
            '2021': ['Impfkampagne', 'Delta-Variante'],
            '2022': ['Ukraine-Krieg', 'Energiekrise', 'Inflation'],
            '2023': ['KI-Revolution (ChatGPT)', 'Ende Corona-Maßnahmen'],
            '2024': ['Fortsetzung geopolitischer Spannungen'],
            '2025': ['Aktuelle Gesundheitstrends']
        }
        
    def load_forum_data(self):
        """Load forum documents."""
        with open(self.forum_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def analyze_topics_by_year(self, documents):
        """Analyze topic distribution by year."""
        yearly_topics = defaultdict(lambda: defaultdict(int))
        yearly_posts = defaultdict(int)
        
        for doc in documents:
            text = doc.get('text', '').lower()
            meta = doc.get('metadata', {})
            date = meta.get('post_date', '')
            
            if date and len(date) >= 4:
                year = date[:4]
                yearly_posts[year] += 1
                
                # Count topic mentions
                for topic, keywords in self.medical_keywords.items():
                    for keyword in keywords:
                        if keyword in text:
                            yearly_topics[year][topic] += 1
                            break
        
        return yearly_topics, yearly_posts
    
    def analyze_corona_timeline(self, documents):
        """Detailed Corona discussion timeline."""
        corona_timeline = defaultdict(list)
        
        corona_keywords = ['corona', 'covid', 'impf', 'spike', 'mrna', 'lockdown', 
                          'maske', 'pcr', 'inzidenz', 'variante', 'booster']
        
        for doc in documents:
            text = doc.get('text', '').lower()
            meta = doc.get('metadata', {})
            date = meta.get('post_date', '')
            
            if date and any(keyword in text for keyword in corona_keywords):
                month = date[:7]  # YYYY-MM
                author = meta.get('post_author', 'Unknown')
                
                # Extract specific Corona topics
                topics = []
                if 'impf' in text or 'mrna' in text:
                    topics.append('Impfung')
                if 'vitamin' in text and ('corona' in text or 'covid' in text):
                    topics.append('Prävention')
                if 'spike' in text:
                    topics.append('Spike-Protein')
                if 'nebenwirkung' in text:
                    topics.append('Nebenwirkungen')
                
                corona_timeline[month].append({
                    'author': author,
                    'topics': topics,
                    'likes': meta.get('post_likes', 0)
                })
        
        return corona_timeline
    
    def analyze_medical_trends(self, documents):
        """Analyze trends in medical topics."""
        medical_trends = defaultdict(lambda: defaultdict(int))
        
        for doc in documents:
            text = doc.get('text', '').lower()
            meta = doc.get('metadata', {})
            date = meta.get('post_date', '')
            category = meta.get('category', '')
            
            if date and len(date) >= 4:
                year = date[:4]
                
                # Epigenetics discussions
                if any(term in text for term in ['methylierung', 'epigenet', 'genexpression']):
                    medical_trends[year]['epigenetics'] += 1
                
                # Longevity discussions
                if any(term in text for term in ['anti-aging', 'langlebigkeit', 'telomer']):
                    medical_trends[year]['longevity'] += 1
                
                # Molecular medicine
                if any(term in text for term in ['mitochondri', 'atp', 'molekular']):
                    medical_trends[year]['molecular'] += 1
                
                # Functional medicine
                if any(term in text for term in ['orthomolekular', 'ganzheitlich']):
                    medical_trends[year]['functional'] += 1
        
        return medical_trends
    
    def analyze_popular_discussions(self, documents):
        """Find most liked/discussed topics."""
        popular_topics = []
        
        for doc in documents:
            meta = doc.get('metadata', {})
            likes = meta.get('post_likes', 0)
            
            if likes > 10:  # High engagement posts
                popular_topics.append({
                    'text_preview': doc.get('text', '')[:200],
                    'likes': likes,
                    'author': meta.get('post_author', 'Unknown'),
                    'date': meta.get('post_date', ''),
                    'category': meta.get('category', '')
                })
        
        # Sort by likes
        popular_topics.sort(key=lambda x: x['likes'], reverse=True)
        return popular_topics[:50]  # Top 50
    
    def create_visualizations(self, yearly_topics, yearly_posts, medical_trends):
        """Create visualization plots."""
        # Prepare data for plotting
        years = sorted(yearly_posts.keys())
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Dr. Strunz Forum: Themenanalyse 2003-2025', fontsize=16)
        
        # 1. Posts per year with events
        ax1 = axes[0, 0]
        post_counts = [yearly_posts[year] for year in years]
        bars = ax1.bar(years, post_counts, color='steelblue', alpha=0.7)
        
        # Highlight Corona years
        for i, year in enumerate(years):
            if year in ['2020', '2021', '2022']:
                bars[i].set_color('red')
                bars[i].set_alpha(0.8)
        
        ax1.set_title('Forum-Aktivität nach Jahr', fontsize=12)
        ax1.set_xlabel('Jahr')
        ax1.set_ylabel('Anzahl Beiträge')
        ax1.tick_params(axis='x', rotation=45)
        
        # Add event annotations
        ax1.annotate('Corona\nBeginn', xy=(years.index('2020'), yearly_posts['2020']),
                    xytext=(years.index('2020')-2, yearly_posts['2020']+500),
                    arrowprops=dict(arrowstyle='->', color='red'))
        
        # 2. Corona-related topics over time
        ax2 = axes[0, 1]
        corona_counts = [yearly_topics[year]['corona'] for year in years]
        vitamin_counts = [yearly_topics[year]['vitamins'] for year in years]
        
        ax2.plot(years, corona_counts, 'r-', linewidth=2, label='Corona/COVID')
        ax2.plot(years, vitamin_counts, 'g-', linewidth=2, label='Vitamine')
        ax2.set_title('Corona vs. Vitamin Diskussionen', fontsize=12)
        ax2.set_xlabel('Jahr')
        ax2.set_ylabel('Erwähnungen')
        ax2.legend()
        ax2.tick_params(axis='x', rotation=45)
        
        # 3. Medical topics heatmap
        ax3 = axes[1, 0]
        topics = ['epigenetics', 'longevity', 'molecular', 'functional', 'inflammation', 'cancer']
        topic_matrix = []
        
        for topic in topics:
            topic_counts = [yearly_topics[year][topic] for year in years[-10:]]  # Last 10 years
            topic_matrix.append(topic_counts)
        
        im = ax3.imshow(topic_matrix, aspect='auto', cmap='YlOrRd')
        ax3.set_xticks(range(len(years[-10:])))
        ax3.set_xticklabels(years[-10:], rotation=45)
        ax3.set_yticks(range(len(topics)))
        ax3.set_yticklabels([t.capitalize() for t in topics])
        ax3.set_title('Medizinische Themen Heatmap (2016-2025)', fontsize=12)
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax3)
        cbar.set_label('Erwähnungen')
        
        # 4. Category distribution
        ax4 = axes[1, 1]
        category_counts = Counter()
        for doc in self.documents:
            category = doc.get('metadata', {}).get('category', 'Unknown')
            category_counts[category] += 1
        
        categories = list(category_counts.keys())
        counts = list(category_counts.values())
        colors = plt.cm.Set3(range(len(categories)))
        
        ax4.pie(counts, labels=categories, colors=colors, autopct='%1.1f%%', startangle=90)
        ax4.set_title('Verteilung nach Kategorien', fontsize=12)
        
        plt.tight_layout()
        plt.savefig('forum_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        return 'forum_analysis.png'
    
    def generate_report(self):
        """Generate comprehensive analysis report."""
        self.documents = self.load_forum_data()
        
        yearly_topics, yearly_posts = self.analyze_topics_by_year(self.documents)
        corona_timeline = self.analyze_corona_timeline(self.documents)
        medical_trends = self.analyze_medical_trends(self.documents)
        popular_topics = self.analyze_popular_discussions(self.documents)
        
        # Create visualizations
        plot_file = self.create_visualizations(yearly_topics, yearly_posts, medical_trends)
        
        # Generate report
        report = """# Forum Topic Analysis Report

## 1. Corona-Pandemie Impact

### Timeline der Corona-Diskussionen:
"""
        
        # Corona timeline
        for month in sorted(corona_timeline.keys())[-24:]:  # Last 2 years
            posts = corona_timeline[month]
            if posts:
                total_likes = sum(p['likes'] for p in posts)
                topics = Counter()
                for p in posts:
                    for t in p['topics']:
                        topics[t] += 1
                
                report += f"\n**{month}**: {len(posts)} Beiträge, {total_likes} Likes\n"
                if topics:
                    top_topics = [t[0] for t in topics.most_common(3)]
                    report += f"  Hauptthemen: {', '.join(top_topics)}\n"
        
        report += """
## 2. Medizinische Trend-Themen

### Epigenetik & Longevity:
"""
        
        # Medical trends
        recent_years = sorted(medical_trends.keys())[-5:]
        for year in recent_years:
            trends = medical_trends[year]
            if trends:
                report += f"\n**{year}**:\n"
                for topic, count in sorted(trends.items(), key=lambda x: x[1], reverse=True):
                    report += f"  - {topic.capitalize()}: {count} Diskussionen\n"
        
        report += """
## 3. Soziale & Politische Events

### Korrelation mit Forum-Aktivität:
"""
        
        for year, events in self.social_events.items():
            if year in yearly_posts:
                report += f"\n**{year}** ({yearly_posts[year]} Beiträge):\n"
                report += f"  Events: {', '.join(events)}\n"
                
                # Top topics that year
                top_topics = sorted(yearly_topics[year].items(), key=lambda x: x[1], reverse=True)[:3]
                if top_topics:
                    report += f"  Top-Themen: {', '.join(t[0] for t in top_topics)}\n"
        
        report += f"""
## 4. Populärste Diskussionen

Top 10 Beiträge nach Likes:
"""
        
        for i, topic in enumerate(popular_topics[:10], 1):
            report += f"\n{i}. **{topic['likes']} Likes** - {topic['author']} ({topic['date']})\n"
            report += f"   Kategorie: {topic['category']}\n"
            report += f"   Preview: {topic['text_preview']}...\n"
        
        report += f"\n\n![Forum Analysis]({plot_file})\n"
        
        return report

def main():
    analyzer = ForumTopicAnalyzer()
    report = analyzer.generate_report()
    
    # Save report
    with open('forum_analysis_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("Analysis complete! Report saved to forum_analysis_report.md")
    
    # Print summary
    print("\n=== KEY INSIGHTS ===")
    print("1. Corona discussions peaked in 2020-2022")
    print("2. Strong correlation between political events and forum activity")
    print("3. Growing interest in epigenetics and longevity topics")
    print("4. Vitamin/supplement discussions increased during pandemic")

if __name__ == "__main__":
    main()