#!/usr/bin/env python3
"""
Analysis Manager - Production Ready
==================================

MCP-compliant analysis manager for comprehensive content analysis and reporting.
Handles all analysis operations for scraped content.

Status: PRODUCTION
Usage: Called by main.py analyze command
Dependencies: Various analysis modules

Author: Claude Code
Last Updated: 2025-07-11
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class AnalysisManager:
    """Production-ready analysis manager following MCP standards."""
    
    def __init__(self):
        """Initialize analysis manager."""
        self.output_dir = Path("data/analysis")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Data source directories
        self.data_sources = [
            Path("data/raw"),
            Path("data/scraped"),
            Path("data/phase2_deployment"),
            Path("data/raw/improved_output"),
            Path("data/raw/docling_input")
        ]
        
        logger.info("AnalysisManager initialized")
        logger.info(f"Output directory: {self.output_dir}")
    
    def generate_comprehensive_report(self) -> Dict:
        """Generate comprehensive analysis report of all available data."""
        logger.info("📊 Generating comprehensive analysis report")
        
        analysis_data = {
            'timestamp': datetime.now().isoformat(),
            'data_sources': [],
            'content_inventory': {},
            'quality_analysis': {},
            'recommendations': [],
            'statistics': {}
        }
        
        # Analyze each data source
        for data_source in self.data_sources:
            if data_source.exists():
                logger.info(f"Analyzing data source: {data_source}")
                source_analysis = self._analyze_data_source(data_source)
                analysis_data['data_sources'].append({
                    'path': str(data_source),
                    'analysis': source_analysis
                })
        
        # Generate content inventory
        analysis_data['content_inventory'] = self._create_content_inventory()
        
        # Perform quality analysis
        analysis_data['quality_analysis'] = self._analyze_content_quality()
        
        # Generate recommendations
        analysis_data['recommendations'] = self._generate_recommendations(analysis_data)
        
        # Calculate statistics
        analysis_data['statistics'] = self._calculate_statistics(analysis_data)
        
        # Save report
        report_file = self._save_analysis_report(analysis_data)
        
        return {
            'status': 'success',
            'report_file': str(report_file),
            'summary': analysis_data['statistics'],
            'total_content_sources': len(analysis_data['data_sources'])
        }
    
    def _analyze_data_source(self, data_path: Path) -> Dict:
        """Analyze a specific data source directory."""
        analysis = {
            'json_files': 0,
            'html_files': 0,
            'content_items': 0,
            'categories_found': set(),
            'sample_content': []
        }
        
        # Count JSON files and analyze content
        json_files = list(data_path.rglob('*.json'))
        analysis['json_files'] = len(json_files)
        
        for json_file in json_files[:5]:  # Sample first 5 files
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    analysis['content_items'] += len(data)
                    
                    # Sample content
                    for item in data[:2]:  # First 2 items per file
                        if isinstance(item, dict):
                            category = item.get('category', 'unknown')
                            analysis['categories_found'].add(category)
                            
                            analysis['sample_content'].append({
                                'title': item.get('title', 'Untitled')[:50],
                                'category': category,
                                'content_length': len(item.get('content', ''))
                            })
            
            except Exception as e:
                logger.warning(f"Could not analyze {json_file}: {e}")
        
        # Count HTML files
        html_files = list(data_path.rglob('*.html'))
        analysis['html_files'] = len(html_files)
        
        # Sample HTML content
        for html_file in html_files[:3]:  # Sample first 3 HTML files
            try:
                html_analysis = self._analyze_html_file(html_file)
                if html_analysis:
                    analysis['sample_content'].append(html_analysis)
            except Exception as e:
                logger.warning(f"Could not analyze HTML {html_file}: {e}")
        
        # Convert set to list for JSON serialization
        analysis['categories_found'] = list(analysis['categories_found'])
        
        return analysis
    
    def _analyze_html_file(self, html_file: Path) -> Optional[Dict]:
        """Analyze individual HTML file."""
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract metadata
            title = soup.find('title')
            title_text = title.get_text() if title else ""
            
            category_meta = soup.find('meta', attrs={'name': 'category'})
            category = category_meta.get('content') if category_meta else 'html'
            
            # Extract content
            content_div = soup.find('div', class_='content')
            content_text = content_div.get_text() if content_div else ""
            
            return {
                'title': title_text[:50],
                'category': category,
                'content_length': len(content_text),
                'file_type': 'html'
            }
        
        except Exception as e:
            logger.warning(f"Failed to analyze HTML file {html_file}: {e}")
            return None
    
    def _create_content_inventory(self) -> Dict:
        """Create comprehensive content inventory."""
        inventory = {
            'total_files': 0,
            'total_content_items': 0,
            'by_category': {},
            'by_file_type': {},
            'ready_for_processing': []
        }
        
        # Check for Docling-ready content
        docling_dir = Path("data/raw/docling_input/news")
        if docling_dir.exists():
            html_files = list(docling_dir.glob('*.html'))
            if html_files:
                inventory['ready_for_processing'].append({
                    'type': 'Docling-ready HTML',
                    'location': str(docling_dir),
                    'file_count': len(html_files),
                    'status': 'Ready for OCR processing'
                })
        
        # Count all files by type
        for data_source in self.data_sources:
            if data_source.exists():
                json_files = list(data_source.rglob('*.json'))
                html_files = list(data_source.rglob('*.html'))
                
                inventory['total_files'] += len(json_files) + len(html_files)
                inventory['by_file_type'][f'{data_source.name}_json'] = len(json_files)
                inventory['by_file_type'][f'{data_source.name}_html'] = len(html_files)
        
        return inventory
    
    def _analyze_content_quality(self) -> Dict:
        """Analyze overall content quality."""
        quality_analysis = {
            'high_quality_sources': [],
            'content_length_distribution': {},
            'category_coverage': {},
            'format_quality': {}
        }
        
        # Check Docling-ready content quality
        docling_dir = Path("data/raw/docling_input/news")
        if docling_dir.exists():
            html_files = list(docling_dir.glob('*.html'))
            if html_files:
                # Sample quality analysis
                content_lengths = []
                categories = set()
                
                for html_file in html_files[:10]:  # Sample 10 files
                    try:
                        with open(html_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        soup = BeautifulSoup(content, 'html.parser')
                        content_div = soup.find('div', class_='content')
                        if content_div:
                            content_text = content_div.get_text()
                            content_lengths.append(len(content_text))
                        
                        category_meta = soup.find('meta', attrs={'name': 'category'})
                        if category_meta:
                            categories.add(category_meta.get('content'))
                    
                    except Exception as e:
                        logger.warning(f"Quality analysis failed for {html_file}: {e}")
                
                if content_lengths:
                    avg_length = sum(content_lengths) / len(content_lengths)
                    quality_analysis['high_quality_sources'].append({
                        'source': 'Docling-ready HTML',
                        'file_count': len(html_files),
                        'average_content_length': int(avg_length),
                        'categories': list(categories),
                        'quality_score': 'High' if avg_length > 1000 else 'Medium'
                    })
        
        return quality_analysis
    
    def _generate_recommendations(self, analysis_data: Dict) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        
        # Check for ready content
        ready_content = analysis_data['content_inventory'].get('ready_for_processing', [])
        if ready_content:
            for content in ready_content:
                if content['type'] == 'Docling-ready HTML':
                    recommendations.append(f"✅ {content['file_count']} files ready for Docling processing in {content['location']}")
                    recommendations.append("🚀 IMMEDIATE ACTION: Process existing content through Docling OCR")
        
        # Check content coverage
        total_items = analysis_data['statistics'].get('total_content_items', 0)
        if total_items > 0:
            recommendations.append(f"📊 {total_items} total content items available for knowledge base")
        
        # Forum scraping status
        forum_success = False
        for source_data in analysis_data['data_sources']:
            source_analysis = source_data['analysis']
            if any('forum' in cat for cat in source_analysis.get('categories_found', [])):
                forum_success = True
                break
        
        if not forum_success:
            recommendations.append("⚠️  Forum scraping needs enhancement:")
            recommendations.append("   • Implement session-based authentication")
            recommendations.append("   • Add JavaScript content handling")
            recommendations.append("   • Consider alternative parsing strategies")
        
        # Next steps
        recommendations.extend([
            "📋 DEVELOPMENT ROADMAP:",
            "   1. Process existing news content through Docling",
            "   2. Build FAISS vector database from processed content",
            "   3. Test MCP server with real knowledge base",
            "   4. Enhance forum scraping capabilities",
            "   5. Deploy complete system to production"
        ])
        
        return recommendations
    
    def _calculate_statistics(self, analysis_data: Dict) -> Dict:
        """Calculate comprehensive statistics."""
        stats = {
            'total_data_sources': len(analysis_data['data_sources']),
            'total_content_items': 0,
            'total_files': analysis_data['content_inventory']['total_files'],
            'content_by_source': {},
            'ready_for_processing': len(analysis_data['content_inventory']['ready_for_processing'])
        }
        
        # Calculate content items per source
        for source_data in analysis_data['data_sources']:
            source_path = source_data['path']
            source_analysis = source_data['analysis']
            content_count = source_analysis['content_items'] + source_analysis['html_files']
            
            stats['content_by_source'][source_path] = content_count
            stats['total_content_items'] += content_count
        
        return stats
    
    def _save_analysis_report(self, analysis_data: Dict) -> Path:
        """Save comprehensive analysis report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON report
        json_report_file = self.output_dir / f"comprehensive_analysis_{timestamp}.json"
        with open(json_report_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False, default=str)
        
        # Generate human-readable markdown report
        markdown_report = self._generate_markdown_report(analysis_data)
        markdown_file = self.output_dir / f"analysis_report_{timestamp}.md"
        with open(markdown_file, 'w', encoding='utf-8') as f:
            f.write(markdown_report)
        
        logger.info(f"📋 Analysis reports saved:")
        logger.info(f"   JSON: {json_report_file}")
        logger.info(f"   Markdown: {markdown_file}")
        
        return json_report_file
    
    def _generate_markdown_report(self, analysis_data: Dict) -> str:
        """Generate human-readable markdown report."""
        stats = analysis_data['statistics']
        
        report = f"""# StrunzKnowledge Analysis Report
Generated: {analysis_data['timestamp']}

## 📊 Executive Summary

- **Total Data Sources**: {stats['total_data_sources']}
- **Total Content Items**: {stats['total_content_items']}
- **Total Files**: {stats['total_files']}
- **Ready for Processing**: {stats['ready_for_processing']} sources

## 📁 Data Sources Analysis

"""
        
        for source_data in analysis_data['data_sources']:
            source_analysis = source_data['analysis']
            report += f"""### {source_data['path']}
- JSON files: {source_analysis['json_files']}
- HTML files: {source_analysis['html_files']}
- Content items: {source_analysis['content_items']}
- Categories: {', '.join(source_analysis['categories_found']) if source_analysis['categories_found'] else 'None'}

"""
        
        # Quality analysis
        if analysis_data['quality_analysis']['high_quality_sources']:
            report += "## 🎯 Content Quality Analysis\n\n"
            for source in analysis_data['quality_analysis']['high_quality_sources']:
                report += f"""**{source['source']}:**
- Files: {source['file_count']}
- Average length: {source['average_content_length']} characters
- Quality score: {source['quality_score']}
- Categories: {', '.join(source['categories'])}

"""
        
        # Recommendations
        if analysis_data['recommendations']:
            report += "## 🚀 Recommendations\n\n"
            for rec in analysis_data['recommendations']:
                report += f"{rec}\n"
            report += "\n"
        
        # Ready for processing
        ready_content = analysis_data['content_inventory']['ready_for_processing']
        if ready_content:
            report += "## ✅ Ready for Processing\n\n"
            for content in ready_content:
                report += f"- **{content['type']}**: {content['file_count']} files in {content['location']}\n"
                report += f"  Status: {content['status']}\n\n"
        
        report += """## 💡 Next Steps

1. **Immediate**: Process Docling-ready content through OCR
2. **Short-term**: Build FAISS vector database
3. **Medium-term**: Enhance forum scraping
4. **Long-term**: Deploy complete MCP server

---
*Generated by StrunzKnowledge Analysis Manager*
"""
        
        return report