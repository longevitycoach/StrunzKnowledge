#!/usr/bin/env python3
"""
Create visualizations for forum analysis with matplotlib
"""

import json
import sys
import subprocess
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
import re

# First install matplotlib in user environment
subprocess.check_call([sys.executable, "-m", "pip", "install", 
                      "matplotlib", "seaborn", "pandas", 
                      "--user", "--break-system-packages"])

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

class ForumVisualizer:
    def __init__(self):
        self.data_dir = Path("data")
        self.forum_file = self.data_dir / "processed" / "forum" / "forum_documents_20250712_211416.json"
        
        # Set style
        plt.style.use('default')
        sns.set_palette("husl")
        
    def load_forum_data(self):
        """Load forum documents."""
        with open(self.forum_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def create_all_visualizations(self):
        """Create all visualization plots."""
        documents = self.load_forum_data()
        
        # Analyze data
        yearly_stats = self.analyze_yearly_stats(documents)
        corona_stats = self.analyze_corona_timeline(documents)
        topic_trends = self.analyze_topic_trends(documents)
        category_stats = self.analyze_categories(documents)
        
        # Create figure with subplots
        fig = plt.figure(figsize=(20, 24))
        
        # 1. Forum Activity Timeline with Events
        ax1 = plt.subplot(4, 2, 1)
        years = sorted(yearly_stats['posts_per_year'].keys())
        posts = [yearly_stats['posts_per_year'][y] for y in years]
        
        bars = ax1.bar(years, posts, color='steelblue', alpha=0.7)
        
        # Highlight Corona years
        for i, year in enumerate(years):
            if year in ['2020', '2021', '2022']:
                bars[i].set_color('red')
                bars[i].set_alpha(0.8)
        
        # Add event annotations
        events = {
            '2020': 'Corona\nPandemie',
            '2021': 'Impf-\nkampagne',
            '2022': 'Ukraine\nKrieg',
            '2023': 'ChatGPT\nRevolution',
            '2024': 'Rekord-\naktivität'
        }
        
        for year, event in events.items():
            if year in years:
                idx = years.index(year)
                ax1.annotate(event, xy=(idx, posts[idx]), 
                           xytext=(idx, posts[idx] + 100),
                           ha='center', fontsize=8,
                           arrowprops=dict(arrowstyle='->', color='black', lw=0.5))
        
        ax1.set_title('Forum-Aktivität im Zeitverlauf (2003-2025)', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Jahr')
        ax1.set_ylabel('Anzahl Beiträge')
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(True, alpha=0.3)
        
        # 2. Corona Discussion Timeline
        ax2 = plt.subplot(4, 2, 2)
        corona_years = sorted(corona_stats.keys())
        corona_posts = [corona_stats[y]['posts'] for y in corona_years]
        corona_likes = [corona_stats[y]['likes'] for y in corona_years]
        
        ax2_twin = ax2.twinx()
        
        p1 = ax2.bar(corona_years, corona_posts, alpha=0.7, color='darkred', label='Corona-Posts')
        p2 = ax2_twin.plot(corona_years, corona_likes, 'go-', linewidth=2, markersize=8, label='Total Likes')
        
        ax2.set_title('Corona-Diskussionen: Posts und Engagement', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Jahr')
        ax2.set_ylabel('Anzahl Corona-Posts', color='darkred')
        ax2_twin.set_ylabel('Total Likes', color='green')
        ax2.tick_params(axis='x', rotation=45)
        ax2.tick_params(axis='y', labelcolor='darkred')
        ax2_twin.tick_params(axis='y', labelcolor='green')
        
        # Combined legend
        lines1, labels1 = ax2.get_legend_handles_labels()
        lines2, labels2 = ax2_twin.get_legend_handles_labels()
        ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        # 3. Medical Topic Trends Heatmap
        ax3 = plt.subplot(4, 2, 3)
        
        # Prepare data for heatmap
        topics = ['epigenetics', 'longevity', 'molecular', 'functional', 
                 'vitamins', 'minerals', 'corona', 'stress']
        heatmap_data = []
        heatmap_years = sorted(topic_trends.keys())[-10:]  # Last 10 years
        
        for topic in topics:
            row = []
            for year in heatmap_years:
                count = topic_trends[year].get(topic, 0)
                row.append(count)
            heatmap_data.append(row)
        
        # Create heatmap
        sns.heatmap(heatmap_data, 
                   xticklabels=heatmap_years,
                   yticklabels=[t.capitalize() for t in topics],
                   cmap='YlOrRd',
                   annot=True,
                   fmt='d',
                   cbar_kws={'label': 'Erwähnungen'},
                   ax=ax3)
        
        ax3.set_title('Medizinische Themen Heatmap (2016-2025)', fontsize=14, fontweight='bold')
        ax3.set_xlabel('Jahr')
        
        # 4. Category Distribution Pie Chart
        ax4 = plt.subplot(4, 2, 4)
        
        categories = list(category_stats.keys())
        sizes = list(category_stats.values())
        colors = plt.cm.Set3(range(len(categories)))
        
        wedges, texts, autotexts = ax4.pie(sizes, labels=categories, colors=colors, 
                                           autopct='%1.1f%%', startangle=90)
        
        # Improve text
        for text in texts:
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
        
        ax4.set_title('Verteilung der Forum-Kategorien', fontsize=14, fontweight='bold')
        
        # 5. Top Medical Topics Evolution
        ax5 = plt.subplot(4, 2, 5)
        
        # Track specific topics over time
        years_range = sorted(topic_trends.keys())[-8:]
        
        for topic in ['vitamins', 'corona', 'diet', 'stress']:
            values = [topic_trends[y].get(topic, 0) for y in years_range]
            ax5.plot(years_range, values, marker='o', linewidth=2, label=topic.capitalize())
        
        ax5.set_title('Evolution der Hauptthemen (2018-2025)', fontsize=14, fontweight='bold')
        ax5.set_xlabel('Jahr')
        ax5.set_ylabel('Erwähnungen')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        ax5.tick_params(axis='x', rotation=45)
        
        # 6. Author Engagement Analysis
        ax6 = plt.subplot(4, 2, 6)
        
        # Get top authors by engagement
        author_stats = self.analyze_author_engagement(documents)
        top_authors = sorted(author_stats.items(), 
                           key=lambda x: x[1]['avg_likes'], 
                           reverse=True)[:10]
        
        authors = [a[0][:15] + '...' if len(a[0]) > 15 else a[0] for a in top_authors]
        avg_likes = [a[1]['avg_likes'] for a in top_authors]
        post_counts = [a[1]['posts'] for a in top_authors]
        
        x = range(len(authors))
        width = 0.35
        
        ax6_twin = ax6.twinx()
        
        bars1 = ax6.bar([i - width/2 for i in x], avg_likes, width, 
                       label='Ø Likes/Post', color='gold', alpha=0.8)
        bars2 = ax6_twin.bar([i + width/2 for i in x], post_counts, width,
                            label='Anzahl Posts', color='navy', alpha=0.8)
        
        ax6.set_xlabel('Autor')
        ax6.set_ylabel('Ø Likes pro Post', color='gold')
        ax6_twin.set_ylabel('Anzahl Posts', color='navy')
        ax6.set_title('Top 10 Autoren nach Engagement', fontsize=14, fontweight='bold')
        ax6.set_xticks(x)
        ax6.set_xticklabels(authors, rotation=45, ha='right')
        ax6.tick_params(axis='y', labelcolor='gold')
        ax6_twin.tick_params(axis='y', labelcolor='navy')
        
        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            ax6.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}', ha='center', va='bottom', fontsize=8)
        
        # 7. Monthly Activity Pattern (2024)
        ax7 = plt.subplot(4, 2, 7)
        
        monthly_2024 = self.analyze_monthly_pattern(documents, '2024')
        months = list(monthly_2024.keys())
        posts = list(monthly_2024.values())
        
        ax7.plot(months, posts, 'bo-', linewidth=2, markersize=8)
        ax7.fill_between(range(len(months)), posts, alpha=0.3)
        
        ax7.set_title('Monatliche Aktivität 2024', fontsize=14, fontweight='bold')
        ax7.set_xlabel('Monat')
        ax7.set_ylabel('Anzahl Posts')
        ax7.set_xticks(range(len(months)))
        ax7.set_xticklabels(['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 
                            'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'][:len(months)])
        ax7.grid(True, alpha=0.3)
        
        # 8. Word Cloud Alternative - Top Keywords
        ax8 = plt.subplot(4, 2, 8)
        
        # Get top keywords
        keyword_counts = self.analyze_keywords(documents)
        top_keywords = keyword_counts.most_common(20)
        
        words = [w[0] for w in top_keywords]
        counts = [w[1] for w in top_keywords]
        
        # Create horizontal bar chart
        y_pos = range(len(words))
        ax8.barh(y_pos, counts, color=plt.cm.viridis(range(len(words))))
        
        ax8.set_yticks(y_pos)
        ax8.set_yticklabels(words)
        ax8.set_xlabel('Häufigkeit')
        ax8.set_title('Top 20 Schlüsselwörter im Forum', fontsize=14, fontweight='bold')
        ax8.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        plt.savefig('forum_analysis_complete.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("Visualizations saved to forum_analysis_complete.png")
        
    def analyze_yearly_stats(self, documents):
        """Analyze posts per year."""
        posts_per_year = defaultdict(int)
        
        for doc in documents:
            date = doc.get('metadata', {}).get('post_date', '')
            if date and len(date) >= 4:
                year = date[:4]
                posts_per_year[year] += 1
        
        return {'posts_per_year': dict(posts_per_year)}
    
    def analyze_corona_timeline(self, documents):
        """Analyze Corona discussions."""
        corona_stats = defaultdict(lambda: {'posts': 0, 'likes': 0})
        corona_keywords = ['corona', 'covid', 'impf', 'spike', 'mrna']
        
        for doc in documents:
            text = doc.get('text', '').lower()
            meta = doc.get('metadata', {})
            date = meta.get('post_date', '')
            
            if date and any(kw in text for kw in corona_keywords):
                year = date[:4]
                corona_stats[year]['posts'] += 1
                corona_stats[year]['likes'] += meta.get('post_likes', 0)
        
        return dict(corona_stats)
    
    def analyze_topic_trends(self, documents):
        """Analyze medical topic trends."""
        topic_keywords = {
            'epigenetics': ['epigenet', 'methylierung', 'genexpression'],
            'longevity': ['longevity', 'langlebigkeit', 'anti-aging'],
            'molecular': ['molekular', 'mitochondri', 'atp'],
            'functional': ['funktionell', 'orthomolekular'],
            'vitamins': ['vitamin', 'vitamine'],
            'minerals': ['zink', 'magnesium', 'selen'],
            'corona': ['corona', 'covid', 'impf'],
            'stress': ['stress', 'cortisol', 'burnout'],
            'diet': ['ernährung', 'diät', 'low carb', 'keto']
        }
        
        yearly_topics = defaultdict(lambda: defaultdict(int))
        
        for doc in documents:
            text = doc.get('text', '').lower()
            date = doc.get('metadata', {}).get('post_date', '')
            
            if date and len(date) >= 4:
                year = date[:4]
                
                for topic, keywords in topic_keywords.items():
                    if any(kw in text for kw in keywords):
                        yearly_topics[year][topic] += 1
        
        return dict(yearly_topics)
    
    def analyze_categories(self, documents):
        """Analyze category distribution."""
        categories = Counter()
        
        for doc in documents:
            category = doc.get('metadata', {}).get('category', 'Unknown')
            categories[category] += 1
        
        return dict(categories)
    
    def analyze_author_engagement(self, documents):
        """Analyze author engagement metrics."""
        author_stats = defaultdict(lambda: {'posts': 0, 'likes': 0})
        
        for doc in documents:
            meta = doc.get('metadata', {})
            author = meta.get('post_author')
            
            if author:
                author_stats[author]['posts'] += 1
                author_stats[author]['likes'] += meta.get('post_likes', 0)
        
        # Calculate average likes
        for author, stats in author_stats.items():
            stats['avg_likes'] = stats['likes'] / stats['posts'] if stats['posts'] > 0 else 0
        
        return dict(author_stats)
    
    def analyze_monthly_pattern(self, documents, year):
        """Analyze monthly posting pattern for a specific year."""
        monthly_posts = defaultdict(int)
        
        for doc in documents:
            date = doc.get('metadata', {}).get('post_date', '')
            
            if date and date.startswith(year):
                month = date[5:7]
                monthly_posts[month] += 1
        
        return dict(sorted(monthly_posts.items()))
    
    def analyze_keywords(self, documents):
        """Extract top keywords."""
        word_counts = Counter()
        
        # Important health-related keywords
        keywords_to_track = [
            'vitamin', 'protein', 'aminosäure', 'magnesium', 'zink', 'eisen',
            'corona', 'covid', 'impfung', 'spike', 'immunsystem',
            'stress', 'cortisol', 'schlaf', 'meditation',
            'low-carb', 'keto', 'fasten', 'ernährung',
            'bewegung', 'sport', 'training', 'fitness',
            'krebs', 'diabetes', 'herz', 'blutdruck',
            'mitochondrien', 'atp', 'energie', 'zelle',
            'epigenetik', 'gene', 'longevity', 'alter'
        ]
        
        for doc in documents:
            text = doc.get('text', '').lower()
            
            for keyword in keywords_to_track:
                if keyword in text:
                    word_counts[keyword] += text.count(keyword)
        
        return word_counts

def main():
    visualizer = ForumVisualizer()
    visualizer.create_all_visualizations()

if __name__ == "__main__":
    main()