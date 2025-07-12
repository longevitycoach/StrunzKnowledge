#!/usr/bin/env python3
"""
Test script for content quality filtering and improved extraction.
"""

import sys
import os
import logging
from datetime import datetime

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scraper.improved_scraper import ImprovedStrunzScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_quality_filtering():
    """Test content quality assessment and filtering."""
    scraper = ImprovedStrunzScraper()
    
    # Test cases with real-world examples
    test_cases = [
        {
            'title': 'Als Cristiano Ronaldo mein Herz eroberte',
            'content': '''Es geschah im Jahr 2021 bei der Fußball-Europameisterschaft. 
            Cristiano Ronaldo – durchtrainierter Vollprofi, 8 % Körperfett, 100 % Disziplin – setzt sich zur Pressekonferenz. 
            Vor ihm: zwei Coca-Cola-Flaschen, artig drapiert vom Sponsor. Und was macht er? 
            Er schiebt sie zur Seite. Ganz ruhig. Ohne Kommentar. Dann hebt er demonstrativ eine Wasserflasche in die Kamera und sagt mit sonorer Stimme: „Agua."
            Eine kleine Geste – mit großer Wirkung. Die Coca-Cola-Aktie rutschte innerhalb von 30 Minuten auf ein Tief von 55,22 Dollar. 
            Der Konzern verlor vier Milliarden Dollar an Börsenwert. Mit diesem Auftritt hatte Ronaldo mein Herz im Sturm erobert! 
            Wie mutig von ihm. Und so wohltuend anders als viele seiner Kollegen, die gefühlt alles bewerben, was sich in bunte Folie wickeln lässt.''',
            'expected_quality': 'high'
        },
        {
            'title': 'Omega-3 Fettsäuren',
            'content': '''Omega-3-Fettsäuren sind gesund. Aus ihnen entstehen Resolvine, sie gehören zu den sogenannten „Immunresolventen" 
            und sind entscheidend für die aktive Beendigung von Entzündungsprozessen. Sie wirken gezielt entzündungshemmend, 
            indem sie die Wanderung weißer Blutkörperchen zum Entzündungsherd blockieren und die Produktion entzündungsfördernder Botenstoffe hemmen.
            Studien zeigen, dass eine ausreichende Versorgung mit EPA und DHA wichtig für das Herz-Kreislauf-System ist.''',
            'expected_quality': 'high'
        },
        {
            'title': 'Newsletter',
            'content': 'Klicken Sie hier. Newsletter abonnieren. Cookie akzeptieren. Mehr Informationen.',
            'expected_quality': 'low'
        },
        {
            'title': 'Kurzer Text',
            'content': 'Das ist ein sehr kurzer Text ohne viel Inhalt.',
            'expected_quality': 'low'
        }
    ]
    
    print(f"\n{'='*60}")
    print("CONTENT QUALITY ASSESSMENT TEST")
    print(f"{'='*60}")
    
    for i, test_case in enumerate(test_cases, 1):
        quality = scraper._assess_content_quality(test_case['content'], test_case['title'])
        
        print(f"\nTest {i}: {test_case['title']}")
        print(f"Content length: {len(test_case['content'])} chars")
        print(f"Word count: {quality.word_count}")
        print(f"Quality score: {quality.score:.3f}")
        print(f"Meaningful content: {quality.is_meaningful}")
        print(f"Has structure: {quality.has_structure}")
        print(f"Language quality: {quality.language_quality:.3f}")
        
        # Determine quality level
        if quality.score >= 0.7:
            actual_quality = 'high'
        elif quality.score >= 0.4:
            actual_quality = 'medium'
        else:
            actual_quality = 'low'
        
        print(f"Expected: {test_case['expected_quality']}, Got: {actual_quality}")
        
        if test_case['expected_quality'] == actual_quality or \
           (test_case['expected_quality'] == 'high' and actual_quality in ['high', 'medium']):
            print("✅ PASS")
        else:
            print("❌ FAIL")
    
    scraper.close()


def test_content_cleaning():
    """Test content cleaning functionality."""
    scraper = ImprovedStrunzScraper()
    
    test_cases = [
        {
            'input': '   This   has    excessive   whitespace   ',
            'description': 'Excessive whitespace'
        },
        {
            'input': 'Cookie akzeptieren\nDatenschutzerklärung\nImpress um\nDer echte Inhalt kommt hier.',
            'description': 'Unwanted patterns'
        },
        {
            'input': 'Ã¤ Ã¶ Ã¼ ÃŸ encoding issues',
            'description': 'Encoding issues'
        }
    ]
    
    print(f"\n{'='*60}")
    print("CONTENT CLEANING TEST")
    print(f"{'='*60}")
    
    for i, test_case in enumerate(test_cases, 1):
        cleaned = scraper._clean_content(test_case['input'])
        
        print(f"\nTest {i}: {test_case['description']}")
        print(f"Input:  '{test_case['input']}'")
        print(f"Output: '{cleaned}'")
        print(f"Length: {len(test_case['input'])} -> {len(cleaned)}")
    
    scraper.close()


def analyze_existing_content():
    """Analyze the quality of already scraped content."""
    from pathlib import Path
    
    scraper = ImprovedStrunzScraper()
    
    # Read existing scraped content
    data_dir = Path('data/raw/docling_input/news')
    if not data_dir.exists():
        print("No existing content found to analyze")
        return
    
    html_files = list(data_dir.glob('*.html'))
    if not html_files:
        print("No HTML files found to analyze")
        return
    
    print(f"\n{'='*60}")
    print(f"ANALYZING {len(html_files)} EXISTING ARTICLES")
    print(f"{'='*60}")
    
    quality_scores = []
    
    for html_file in html_files[:5]:  # Analyze first 5 files
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract text content from HTML
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            title = soup.find('title')
            title_text = title.get_text() if title else ""
            
            content_div = soup.find('div', class_='content')
            content_text = content_div.get_text() if content_div else ""
            
            if content_text:
                quality = scraper._assess_content_quality(content_text, title_text)
                quality_scores.append(quality.score)
                
                print(f"\nFile: {html_file.name}")
                print(f"Title: {title_text[:50]}...")
                print(f"Content length: {len(content_text)} chars")
                print(f"Word count: {quality.word_count}")
                print(f"Quality score: {quality.score:.3f}")
                print(f"Meaningful: {quality.is_meaningful}")
        
        except Exception as e:
            print(f"Error analyzing {html_file.name}: {e}")
    
    if quality_scores:
        avg_quality = sum(quality_scores) / len(quality_scores)
        high_quality = sum(1 for s in quality_scores if s >= 0.7)
        medium_quality = sum(1 for s in quality_scores if 0.4 <= s < 0.7)
        low_quality = sum(1 for s in quality_scores if s < 0.4)
        
        print(f"\n{'='*40}")
        print("QUALITY SUMMARY")
        print(f"{'='*40}")
        print(f"Average quality score: {avg_quality:.3f}")
        print(f"High quality (≥0.7): {high_quality}")
        print(f"Medium quality (0.4-0.7): {medium_quality}")
        print(f"Low quality (<0.4): {low_quality}")
    
    scraper.close()


def main():
    """Run all quality tests."""
    from pathlib import Path
    
    print("Starting content quality and filtering tests...")
    
    test_quality_filtering()
    test_content_cleaning()
    analyze_existing_content()
    
    print(f"\nTests completed at: {datetime.now()}")


if __name__ == "__main__":
    main()