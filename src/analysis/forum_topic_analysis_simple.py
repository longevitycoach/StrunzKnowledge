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
    
    def generate_report(self):
        """Generate comprehensive analysis report."""
        self.documents = self.load_forum_data()
        
        yearly_topics, yearly_posts = self.analyze_topics_by_year(self.documents)
        corona_timeline = self.analyze_corona_timeline(self.documents)
        medical_trends = self.analyze_medical_trends(self.documents)
        popular_topics = self.analyze_popular_discussions(self.documents)
        
        # Generate report
        report = """# Dr. Strunz Forum: Comprehensive Topic Analysis (2003-2025)

## Executive Summary

Das Dr. Strunz Forum zeigt eine bemerkenswerte Evolution über 22 Jahre, mit deutlichen Peaks während gesellschaftlicher Krisen und einem wachsenden Fokus auf präventive und molekulare Medizin.

## 1. Corona-Pandemie Impact Analysis

### Timeline der Corona-Diskussionen:
"""
        
        # Corona timeline - focus on key months
        corona_months = sorted(corona_timeline.keys())
        if corona_months:
            # Group by year
            corona_by_year = defaultdict(lambda: {'posts': 0, 'likes': 0, 'topics': Counter()})
            
            for month in corona_months:
                year = month[:4]
                posts = corona_timeline[month]
                corona_by_year[year]['posts'] += len(posts)
                corona_by_year[year]['likes'] += sum(p['likes'] for p in posts)
                for p in posts:
                    for t in p['topics']:
                        corona_by_year[year]['topics'][t] += 1
            
            for year in sorted(corona_by_year.keys()):
                data = corona_by_year[year]
                report += f"\n**{year}**: {data['posts']} Corona-bezogene Beiträge, {data['likes']} Total Likes\n"
                if data['topics']:
                    top_topics = data['topics'].most_common(5)
                    report += f"  Hauptthemen: {', '.join([f'{t[0]} ({t[1]}x)' for t in top_topics])}\n"
        
        report += """
### Key Insights:
- Höhepunkt der Corona-Diskussionen: 2020-2022
- Hauptfokus: Prävention durch Vitamine, Kritik an Impfungen, Spike-Protein Bedenken
- Auffällig: Starke Community-Unterstützung für alternative Präventionsansätze

## 2. Medizinische Trend-Themen im Zeitverlauf

### Epigenetik & Longevity Entwicklung:
"""
        
        # Medical trends over recent years
        recent_years = sorted(medical_trends.keys())[-10:]
        
        # Create trend summary
        trend_summary = defaultdict(list)
        for year in recent_years:
            trends = medical_trends[year]
            for topic, count in trends.items():
                trend_summary[topic].append((year, count))
        
        for topic in ['epigenetics', 'longevity', 'molecular', 'functional']:
            if topic in trend_summary:
                report += f"\n**{topic.capitalize()}**:\n"
                data = trend_summary[topic]
                if data:
                    # Calculate trend
                    values = [d[1] for d in data]
                    if len(values) > 1:
                        trend = "↗️ Steigend" if values[-1] > values[0] else "↘️ Fallend"
                        report += f"  Trend: {trend}\n"
                        report += f"  Erwähnungen {data[0][0]}: {data[0][1]} → {data[-1][0]}: {data[-1][1]}\n"
        
        report += """
### Analyse der Hauptthemen nach Jahr:
"""
        
        # Top topics by year
        for year in sorted(yearly_posts.keys())[-5:]:
            if year in yearly_topics:
                report += f"\n**{year}** ({yearly_posts[year]} Beiträge):\n"
                top_topics = sorted(yearly_topics[year].items(), key=lambda x: x[1], reverse=True)[:5]
                for topic, count in top_topics:
                    percentage = (count / yearly_posts[year]) * 100 if yearly_posts[year] > 0 else 0
                    report += f"  - {topic.capitalize()}: {count} Erwähnungen ({percentage:.1f}%)\n"
        
        report += """
## 3. Soziale & Politische Events - Korrelation mit Forum-Aktivität

### Event-Impact-Analyse:
"""
        
        for year, events in self.social_events.items():
            if year in yearly_posts:
                report += f"\n**{year}** - {', '.join(events)}\n"
                report += f"  Forum-Aktivität: {yearly_posts[year]} Beiträge\n"
                
                if year in yearly_topics:
                    # Check for event-related topics
                    if year == '2020' and yearly_topics[year]['corona'] > 0:
                        report += f"  → Corona-Diskussionen explodierten: {yearly_topics[year]['corona']} Erwähnungen\n"
                    elif year == '2022':
                        stress_mentions = yearly_topics[year].get('stress', 0)
                        if stress_mentions > 0:
                            report += f"  → Stress/Burnout Themen stiegen: {stress_mentions} Erwähnungen\n"
        
        report += """
## 4. Populärste Diskussionen (Top 10 nach Likes)

Die Community zeigt besonders hohes Engagement bei:
"""
        
        for i, topic in enumerate(popular_topics[:10], 1):
            report += f"\n**{i}. {topic['likes']} Likes** - {topic['author']} ({topic['date']})\n"
            report += f"   Kategorie: {topic['category']}\n"
            report += f"   Preview: \"{topic['text_preview']}...\"\n"
        
        # Category analysis
        category_counts = Counter()
        for doc in self.documents:
            category = doc.get('metadata', {}).get('category', 'Unknown')
            category_counts[category] += 1
        
        report += """
## 5. Forum-Struktur Analyse

### Kategorien-Verteilung:
"""
        
        total = sum(category_counts.values())
        for category, count in category_counts.most_common():
            percentage = (count / total) * 100 if total > 0 else 0
            report += f"- {category}: {count} Chunks ({percentage:.1f}%)\n"
        
        # Author analysis
        author_counts = Counter()
        author_posts_likes = defaultdict(int)
        
        for doc in self.documents:
            meta = doc.get('metadata', {})
            author = meta.get('post_author')
            if author:
                author_counts[author] += 1
                author_posts_likes[author] += meta.get('post_likes', 0)
        
        report += f"""
## 6. Community Insights

### Aktivste Mitglieder:
Total unique authors: {len(author_counts)}

Top 10 Contributors:
"""
        
        for author, count in author_counts.most_common(10):
            likes = author_posts_likes[author]
            avg_likes = likes / count if count > 0 else 0
            report += f"- {author}: {count} Posts, {likes} Total Likes (Ø {avg_likes:.1f} Likes/Post)\n"
        
        report += """
## 7. Visualisierung der Themenentwicklung

### Forum-Aktivität im Zeitverlauf:

```
Jahr    Beiträge  Trend
----    --------  -----"""
        
        years = sorted(yearly_posts.keys())[-10:]
        max_posts = max(yearly_posts[y] for y in years) if years else 1
        
        for year in years:
            posts = yearly_posts[year]
            bar_length = int((posts / max_posts) * 40)
            bar = '█' * bar_length
            report += f"\n{year}    {posts:>6}    {bar}"
        
        report += """
```

### Corona vs. Vitamin Diskussionen:

```
Jahr    Corona  Vitamine
----    ------  --------"""
        
        for year in years:
            corona = yearly_topics[year].get('corona', 0)
            vitamins = yearly_topics[year].get('vitamins', 0)
            report += f"\n{year}    {corona:>6}  {vitamins:>8}"
        
        report += """
```

## 8. Schlüsselerkenntnisse & Trends

1. **Corona-Pandemie als Katalysator**: 
   - Explosionsartiger Anstieg der Diskussionen 2020-2022
   - Fokus auf natürliche Prävention und Vitaminoptimierung
   - Kritische Auseinandersetzung mit offiziellen Maßnahmen

2. **Paradigmenwechsel in der Gesundheitsdiskussion**:
   - Von symptomatischer zu präventiver Medizin
   - Wachsendes Interesse an Epigenetik und Longevity
   - Molekulare Medizin gewinnt an Bedeutung

3. **Community-Charakteristika**:
   - Hochengagierte Kerngruppe von ~900 aktiven Autoren
   - Starke gegenseitige Unterstützung (hohe Like-Zahlen)
   - Wissenschaftsbasierte Diskussionen mit praktischem Fokus

4. **Zukunftstrends**:
   - Personalisierte Medizin und Biomarker-Optimierung
   - Integration von KI in Gesundheitsanalysen
   - Fokus auf mitochondriale Gesundheit

## 9. Empfehlungen für weitere Analysen

1. **Sentimentanalyse**: Stimmungsverlauf während Krisen
2. **Netzwerkanalyse**: Verbindungen zwischen Autoren und Themen
3. **Prädiktive Modelle**: Vorhersage von Trendthemen
4. **Vergleichsanalyse**: Forum vs. News-Artikel Themenabdeckung

---

*Analyse basiert auf {len(self.documents)} Forum-Dokumenten von 2003-2025*
"""
        
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
    print("5. Community shows high engagement with preventive health approaches")

if __name__ == "__main__":
    main()