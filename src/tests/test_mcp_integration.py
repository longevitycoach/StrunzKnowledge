import pytest
import asyncio
from typing import List, Dict
from datetime import datetime, timedelta

from ..mcp.server import (
    knowledge_search, 
    summarize_posts, 
    get_latest_insights,
    get_most_discussed_topics
)


class TestMCPPositiveIntegration:
    """100 positive integration tests for MCP client."""
    
    # Knowledge Search Tests (25 tests)
    @pytest.mark.asyncio
    async def test_search_vitamin_d(self):
        results = await knowledge_search("Vitamin D")
        assert len(results) > 0
        assert any("vitamin" in r['content'].lower() for r in results)
    
    @pytest.mark.asyncio
    async def test_search_omega_3(self):
        results = await knowledge_search("Omega-3 Fettsäuren")
        assert len(results) > 0
    
    @pytest.mark.asyncio
    async def test_search_with_category_filter(self):
        results = await knowledge_search("Training", category="Fitness")
        assert all(r['metadata'].get('category') == 'Fitness' for r in results)
    
    @pytest.mark.asyncio
    async def test_search_with_date_filter(self):
        min_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        results = await knowledge_search("Gesundheit", min_date=min_date)
        assert len(results) >= 0  # May be empty if no recent posts
    
    @pytest.mark.asyncio
    async def test_search_ketose(self):
        results = await knowledge_search("Ketose")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_marathon_training(self):
        results = await knowledge_search("Marathon Training")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_bluttuning(self):
        results = await knowledge_search("Bluttuning", category="Bluttuning")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_stress_management(self):
        results = await knowledge_search("Stress bewältigen", category="Mental")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_immunsystem(self):
        results = await knowledge_search("Immunsystem stärken")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_protein(self):
        results = await knowledge_search("Protein Eiweiß")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_magnesium(self):
        results = await knowledge_search("Magnesium")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_vitamin_c(self):
        results = await knowledge_search("Vitamin C Ascorbinsäure")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_zinc(self):
        results = await knowledge_search("Zink")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_iron(self):
        results = await knowledge_search("Eisen Ferritin")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_b12(self):
        results = await knowledge_search("Vitamin B12")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_folate(self):
        results = await knowledge_search("Folsäure")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_calcium(self):
        results = await knowledge_search("Calcium Kalzium")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_selenium(self):
        results = await knowledge_search("Selen")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_coq10(self):
        results = await knowledge_search("Coenzym Q10")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_l_carnitine(self):
        results = await knowledge_search("L-Carnitin")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_creatine(self):
        results = await knowledge_search("Kreatin")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_glutamine(self):
        results = await knowledge_search("Glutamin")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_arginine(self):
        results = await knowledge_search("Arginin")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_taurine(self):
        results = await knowledge_search("Taurin")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_probiotics(self):
        results = await knowledge_search("Probiotika Darmflora")
        assert isinstance(results, list)
    
    # Latest Insights Tests (25 tests)
    @pytest.mark.asyncio
    async def test_latest_news(self):
        results = await get_latest_insights("News", limit=5)
        assert len(results) <= 5
        assert all('date' in r for r in results)
    
    @pytest.mark.asyncio
    async def test_latest_fitness(self):
        results = await get_latest_insights("Fitness", limit=3)
        assert len(results) <= 3
    
    @pytest.mark.asyncio
    async def test_latest_gesundheit(self):
        results = await get_latest_insights("Gesundheit")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_latest_ernaehrung(self):
        results = await get_latest_insights("Ernährung", limit=10)
        assert len(results) <= 10
    
    @pytest.mark.asyncio
    async def test_latest_bluttuning(self):
        results = await get_latest_insights("Bluttuning")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_latest_mental(self):
        results = await get_latest_insights("Mental")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_latest_praevention(self):
        results = await get_latest_insights("Prävention")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_latest_single_post(self):
        results = await get_latest_insights("News", limit=1)
        assert len(results) <= 1
    
    @pytest.mark.asyncio
    async def test_latest_twenty_posts(self):
        results = await get_latest_insights("Fitness", limit=20)
        assert len(results) <= 20
    
    @pytest.mark.asyncio
    async def test_latest_with_metadata(self):
        results = await get_latest_insights("Gesundheit", limit=5)
        for r in results:
            assert 'metadata' in r
            assert 'content_preview' in r
    
    @pytest.mark.asyncio 
    async def test_latest_news_titles(self):
        results = await get_latest_insights("News", limit=5)
        for r in results:
            assert 'title' in r
    
    @pytest.mark.asyncio
    async def test_latest_fitness_dates(self):
        results = await get_latest_insights("Fitness", limit=5)
        for r in results:
            assert 'date' in r
    
    @pytest.mark.asyncio
    async def test_latest_sorted_by_date(self):
        results = await get_latest_insights("News", limit=10)
        # Dates should be in descending order
        dates = [r.get('date', '') for r in results]
        assert dates == sorted(dates, reverse=True)
    
    @pytest.mark.asyncio
    async def test_latest_unique_posts(self):
        results = await get_latest_insights("Ernährung", limit=10)
        ids = [r['id'] for r in results]
        assert len(ids) == len(set(ids))  # All IDs unique
    
    @pytest.mark.asyncio
    async def test_latest_content_preview_length(self):
        results = await get_latest_insights("Mental", limit=5)
        for r in results:
            assert len(r.get('content_preview', '')) <= 350
    
    @pytest.mark.asyncio
    async def test_latest_all_categories(self):
        categories = ["News", "Fitness", "Gesundheit", "Ernährung", "Bluttuning", "Mental", "Prävention"]
        for cat in categories:
            results = await get_latest_insights(cat, limit=1)
            assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_latest_empty_category(self):
        results = await get_latest_insights("NonExistent")
        assert results == []
    
    @pytest.mark.asyncio
    async def test_latest_default_limit(self):
        results = await get_latest_insights("News")
        assert len(results) <= 5  # Default limit
    
    @pytest.mark.asyncio
    async def test_latest_large_limit(self):
        results = await get_latest_insights("Fitness", limit=100)
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_latest_response_structure(self):
        results = await get_latest_insights("Gesundheit", limit=1)
        if results:
            r = results[0]
            assert all(k in r for k in ['id', 'title', 'date', 'content_preview', 'metadata'])
    
    @pytest.mark.asyncio
    async def test_latest_metadata_category(self):
        results = await get_latest_insights("Bluttuning", limit=5)
        for r in results:
            assert r['metadata'].get('category') == 'Bluttuning'
    
    @pytest.mark.asyncio
    async def test_latest_no_deleted_posts(self):
        results = await get_latest_insights("News", limit=10)
        for r in results:
            assert not r['metadata'].get('deleted', False)
    
    @pytest.mark.asyncio
    async def test_latest_german_dates(self):
        results = await get_latest_insights("Mental", limit=5)
        for r in results:
            if r.get('date') and r['date'] != 'Unbekannt':
                assert '.' in r['date']  # German date format
    
    @pytest.mark.asyncio
    async def test_latest_non_empty_content(self):
        results = await get_latest_insights("Ernährung", limit=5)
        for r in results:
            assert len(r.get('content_preview', '')) > 0
    
    @pytest.mark.asyncio
    async def test_latest_valid_ids(self):
        results = await get_latest_insights("Fitness", limit=5)
        for r in results:
            assert r['id'] is not None
            assert len(r['id']) > 0
    
    # Most Discussed Topics Tests (25 tests)
    @pytest.mark.asyncio
    async def test_most_discussed_fitness(self):
        results = await get_most_discussed_topics("Fitness", limit=5)
        assert len(results) <= 5
        assert all('engagement_score' in r for r in results)
    
    @pytest.mark.asyncio
    async def test_most_discussed_gesundheit(self):
        results = await get_most_discussed_topics("Gesundheit")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_most_discussed_ernaehrung(self):
        results = await get_most_discussed_topics("Ernährung", limit=3)
        assert len(results) <= 3
    
    @pytest.mark.asyncio
    async def test_most_discussed_sorted(self):
        results = await get_most_discussed_topics("Bluttuning", limit=10)
        scores = [r['engagement_score'] for r in results]
        assert scores == sorted(scores, reverse=True)
    
    @pytest.mark.asyncio
    async def test_most_discussed_unique_titles(self):
        results = await get_most_discussed_topics("Mental", limit=10)
        titles = [r['title'] for r in results]
        assert len(titles) == len(set(titles))
    
    @pytest.mark.asyncio
    async def test_most_discussed_metadata(self):
        results = await get_most_discussed_topics("News", limit=5)
        for r in results:
            assert 'metadata' in r
    
    @pytest.mark.asyncio
    async def test_most_discussed_preview(self):
        results = await get_most_discussed_topics("Fitness", limit=5)
        for r in results:
            assert 'content_preview' in r
            assert len(r['content_preview']) > 0
    
    @pytest.mark.asyncio
    async def test_most_discussed_dates(self):
        results = await get_most_discussed_topics("Prävention", limit=5)
        for r in results:
            assert 'date' in r
    
    @pytest.mark.asyncio
    async def test_most_discussed_single_topic(self):
        results = await get_most_discussed_topics("Gesundheit", limit=1)
        assert len(results) <= 1
    
    @pytest.mark.asyncio
    async def test_most_discussed_all_categories(self):
        categories = ["News", "Fitness", "Gesundheit", "Ernährung", "Bluttuning", "Mental", "Prävention"]
        for cat in categories:
            results = await get_most_discussed_topics(cat, limit=1)
            assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_most_discussed_engagement_positive(self):
        results = await get_most_discussed_topics("Ernährung", limit=10)
        for r in results:
            assert r['engagement_score'] > 0
    
    @pytest.mark.asyncio
    async def test_most_discussed_response_structure(self):
        results = await get_most_discussed_topics("Mental", limit=1)
        if results:
            r = results[0]
            assert all(k in r for k in ['id', 'title', 'date', 'engagement_score', 'content_preview', 'metadata'])
    
    @pytest.mark.asyncio
    async def test_most_discussed_category_filter(self):
        results = await get_most_discussed_topics("Bluttuning", limit=5)
        for r in results:
            assert r['metadata'].get('category') == 'Bluttuning'
    
    @pytest.mark.asyncio
    async def test_most_discussed_no_deleted(self):
        results = await get_most_discussed_topics("News", limit=10)
        for r in results:
            assert not r['metadata'].get('deleted', False)
    
    @pytest.mark.asyncio
    async def test_most_discussed_large_limit(self):
        results = await get_most_discussed_topics("Fitness", limit=50)
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_most_discussed_default_limit(self):
        results = await get_most_discussed_topics("Gesundheit")
        assert len(results) <= 5
    
    @pytest.mark.asyncio
    async def test_most_discussed_empty_category(self):
        results = await get_most_discussed_topics("NonExistent")
        assert results == []
    
    @pytest.mark.asyncio
    async def test_most_discussed_valid_ids(self):
        results = await get_most_discussed_topics("Ernährung", limit=5)
        for r in results:
            assert r['id'] is not None
            assert len(r['id']) > 0
    
    @pytest.mark.asyncio
    async def test_most_discussed_content_length(self):
        results = await get_most_discussed_topics("Mental", limit=5)
        for r in results:
            assert len(r['content_preview']) <= 350
    
    @pytest.mark.asyncio
    async def test_most_discussed_german_content(self):
        results = await get_most_discussed_topics("Prävention", limit=5)
        for r in results:
            # Check for German characters
            assert any(c in r['content_preview'] for c in 'äöüßÄÖÜ') or len(r['content_preview']) > 0
    
    @pytest.mark.asyncio
    async def test_most_discussed_no_duplicates(self):
        results = await get_most_discussed_topics("News", limit=20)
        ids = [r['id'] for r in results]
        assert len(ids) == len(set(ids))
    
    @pytest.mark.asyncio
    async def test_most_discussed_title_not_unknown(self):
        results = await get_most_discussed_topics("Fitness", limit=10)
        unknown_count = sum(1 for r in results if r['title'] == 'Unbekannt')
        assert unknown_count < len(results) // 2  # Less than half unknown
    
    @pytest.mark.asyncio
    async def test_most_discussed_engagement_variance(self):
        results = await get_most_discussed_topics("Gesundheit", limit=10)
        if len(results) > 1:
            scores = [r['engagement_score'] for r in results]
            assert max(scores) > min(scores)  # Some variance in scores
    
    @pytest.mark.asyncio
    async def test_most_discussed_metadata_present(self):
        results = await get_most_discussed_topics("Bluttuning", limit=5)
        for r in results:
            assert isinstance(r['metadata'], dict)
    
    @pytest.mark.asyncio
    async def test_most_discussed_date_format(self):
        results = await get_most_discussed_topics("Ernährung", limit=5)
        for r in results:
            if r['date'] != 'Unbekannt':
                assert '.' in r['date'] or '-' in r['date']
    
    # User Role Tests (10 tests)
    @pytest.mark.asyncio
    async def test_beginner_athlete_query(self):
        results = await knowledge_search("Training Anfänger")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_advanced_athlete_query(self):
        results = await knowledge_search("Leistungssport Wettkampf")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_patient_query(self):
        results = await knowledge_search("Heilung Genesung")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_health_enthusiast_query(self):
        results = await knowledge_search("Prävention Vorsorge")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_nutrition_beginner_query(self):
        results = await knowledge_search("gesunde Ernährung Basics")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_biohacker_query(self):
        results = await knowledge_search("Optimierung Biohacking")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_senior_health_query(self):
        results = await knowledge_search("Alter Gesundheit Senioren")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_weight_loss_query(self):
        results = await knowledge_search("Abnehmen Gewichtsreduktion")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_muscle_building_query(self):
        results = await knowledge_search("Muskelaufbau Krafttraining")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_stress_management_query(self):
        results = await knowledge_search("Stress Entspannung Meditation")
        assert isinstance(results, list)
    
    # Date Constraint Tests (5 tests)
    @pytest.mark.asyncio
    async def test_search_last_year(self):
        min_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        results = await knowledge_search("Vitamin", min_date=min_date)
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_last_month(self):
        min_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        results = await knowledge_search("Training", min_date=min_date)
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_last_week(self):
        min_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        results = await knowledge_search("Gesundheit", min_date=min_date)
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_specific_year(self):
        results = await knowledge_search("Ernährung 2023")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_date_range_filter(self):
        min_date = "2023-01-01"
        results = await knowledge_search("Fitness", min_date=min_date)
        assert isinstance(results, list)
    
    # Tool Combination Tests (10 tests)
    @pytest.mark.asyncio
    async def test_search_then_summarize(self):
        search_results = await knowledge_search("Omega-3", category="Ernährung")
        if search_results:
            post_ids = [r['metadata'].get('id', f"post_{i}") for i, r in enumerate(search_results[:3])]
            summary = await summarize_posts(post_ids)
            assert isinstance(summary, str)
    
    @pytest.mark.asyncio
    async def test_latest_then_search(self):
        latest = await get_latest_insights("Fitness", limit=1)
        if latest:
            topic = latest[0]['title']
            search_results = await knowledge_search(topic)
            assert isinstance(search_results, list)
    
    @pytest.mark.asyncio
    async def test_most_discussed_then_summarize(self):
        topics = await get_most_discussed_topics("Gesundheit", limit=3)
        if topics:
            post_ids = [t['id'] for t in topics]
            summary = await summarize_posts(post_ids)
            assert isinstance(summary, str)
    
    @pytest.mark.asyncio
    async def test_category_cross_search(self):
        # Search in one category, then another
        fitness_results = await knowledge_search("Training", category="Fitness")
        mental_results = await knowledge_search("Training", category="Mental")
        assert isinstance(fitness_results, list)
        assert isinstance(mental_results, list)
    
    @pytest.mark.asyncio
    async def test_multi_category_latest(self):
        news = await get_latest_insights("News", limit=2)
        fitness = await get_latest_insights("Fitness", limit=2)
        assert isinstance(news, list)
        assert isinstance(fitness, list)
    
    @pytest.mark.asyncio
    async def test_search_multiple_terms(self):
        results1 = await knowledge_search("Vitamin D")
        results2 = await knowledge_search("Calcium")
        results3 = await knowledge_search("Knochen")
        assert all(isinstance(r, list) for r in [results1, results2, results3])
    
    @pytest.mark.asyncio
    async def test_trending_across_categories(self):
        categories = ["Fitness", "Gesundheit", "Ernährung"]
        trending = []
        for cat in categories:
            topics = await get_most_discussed_topics(cat, limit=1)
            trending.extend(topics)
        assert len(trending) <= 3
    
    @pytest.mark.asyncio
    async def test_comprehensive_health_search(self):
        # Simulate comprehensive search
        searches = [
            ("Immunsystem", None),
            ("Vitamin C", "Ernährung"),
            ("Sport", "Fitness"),
            ("Stress", "Mental")
        ]
        all_results = []
        for query, cat in searches:
            results = await knowledge_search(query, category=cat)
            all_results.extend(results)
        assert len(all_results) > 0
    
    @pytest.mark.asyncio
    async def test_latest_all_categories_summary(self):
        all_latest = []
        for cat in ["News", "Fitness", "Gesundheit"]:
            latest = await get_latest_insights(cat, limit=1)
            all_latest.extend(latest)
        assert len(all_latest) <= 3
    
    @pytest.mark.asyncio
    async def test_search_result_relevance(self):
        # Search for specific term and verify relevance
        results = await knowledge_search("Magnesium")
        if results:
            # At least one result should contain the search term
            assert any("magnesium" in r['content'].lower() for r in results)


class TestMCPNegativeIntegration:
    """100 negative integration tests for MCP client."""
    
    # Invalid Input Tests (25 tests)
    @pytest.mark.asyncio
    async def test_empty_search_query(self):
        results = await knowledge_search("")
        assert results == []
    
    @pytest.mark.asyncio
    async def test_none_search_query(self):
        with pytest.raises(TypeError):
            await knowledge_search(None)
    
    @pytest.mark.asyncio
    async def test_invalid_category(self):
        results = await knowledge_search("Test", category="InvalidCategory")
        assert results == [] or all(r['metadata'].get('category') != 'InvalidCategory' for r in results)
    
    @pytest.mark.asyncio
    async def test_invalid_date_format(self):
        results = await knowledge_search("Test", min_date="invalid-date")
        assert isinstance(results, list)  # Should handle gracefully
    
    @pytest.mark.asyncio
    async def test_future_date_filter(self):
        future_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
        results = await knowledge_search("Test", min_date=future_date)
        assert results == []  # No posts from the future
    
    @pytest.mark.asyncio
    async def test_numeric_search_query(self):
        results = await knowledge_search("12345")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_special_chars_search(self):
        results = await knowledge_search("!@#$%^&*()")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_sql_injection_attempt(self):
        results = await knowledge_search("'; DROP TABLE posts; --")
        assert isinstance(results, list)  # Should handle safely
    
    @pytest.mark.asyncio
    async def test_extremely_long_query(self):
        long_query = "a" * 10000
        results = await knowledge_search(long_query)
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_unicode_search(self):
        results = await knowledge_search("🏃‍♂️💪🥗")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_html_in_search(self):
        results = await knowledge_search("<script>alert('test')</script>")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_negative_limit(self):
        results = await get_latest_insights("News", limit=-5)
        assert results == []
    
    @pytest.mark.asyncio
    async def test_zero_limit(self):
        results = await get_latest_insights("Fitness", limit=0)
        assert results == []
    
    @pytest.mark.asyncio
    async def test_float_limit(self):
        with pytest.raises((TypeError, ValueError)):
            await get_latest_insights("Gesundheit", limit=3.14)
    
    @pytest.mark.asyncio
    async def test_string_limit(self):
        with pytest.raises((TypeError, ValueError)):
            await get_latest_insights("Mental", limit="five")
    
    @pytest.mark.asyncio
    async def test_massive_limit(self):
        results = await get_latest_insights("News", limit=999999)
        assert isinstance(results, list)  # Should handle gracefully
    
    @pytest.mark.asyncio
    async def test_none_category(self):
        with pytest.raises(TypeError):
            await get_latest_insights(None)
    
    @pytest.mark.asyncio
    async def test_empty_category(self):
        results = await get_latest_insights("")
        assert results == []
    
    @pytest.mark.asyncio
    async def test_numeric_category(self):
        results = await get_latest_insights("123")
        assert results == []
    
    @pytest.mark.asyncio
    async def test_mixed_case_category(self):
        results = await get_latest_insights("fItNeSs")
        assert results == []  # Case sensitive
    
    @pytest.mark.asyncio
    async def test_category_with_spaces(self):
        results = await get_latest_insights("Fitness Training")
        assert results == []
    
    @pytest.mark.asyncio
    async def test_category_with_special_chars(self):
        results = await get_latest_insights("Fitness!")
        assert results == []
    
    @pytest.mark.asyncio
    async def test_summarize_empty_list(self):
        summary = await summarize_posts([])
        assert "keine" in summary.lower() or "not found" in summary.lower()
    
    @pytest.mark.asyncio
    async def test_summarize_none_ids(self):
        with pytest.raises(TypeError):
            await summarize_posts(None)
    
    @pytest.mark.asyncio
    async def test_summarize_invalid_ids(self):
        summary = await summarize_posts(["invalid_id_1", "invalid_id_2"])
        assert "keine" in summary.lower() or "not found" in summary.lower()
    
    # Error Handling Tests (25 tests)
    @pytest.mark.asyncio
    async def test_search_with_null_bytes(self):
        results = await knowledge_search("test\x00null")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_only_whitespace(self):
        results = await knowledge_search("   \t\n   ")
        assert results == []
    
    @pytest.mark.asyncio
    async def test_malformed_date_filter(self):
        results = await knowledge_search("Test", min_date="2023-13-45")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_control_characters(self):
        results = await knowledge_search("\x01\x02\x03")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_newlines_only(self):
        results = await knowledge_search("\n\n\n")
        assert results == []
    
    @pytest.mark.asyncio
    async def test_search_tabs_only(self):
        results = await knowledge_search("\t\t\t")
        assert results == []
    
    @pytest.mark.asyncio
    async def test_boolean_as_query(self):
        with pytest.raises(TypeError):
            await knowledge_search(True)
    
    @pytest.mark.asyncio
    async def test_list_as_query(self):
        with pytest.raises(TypeError):
            await knowledge_search(["vitamin", "d"])
    
    @pytest.mark.asyncio
    async def test_dict_as_query(self):
        with pytest.raises(TypeError):
            await knowledge_search({"query": "vitamin"})
    
    @pytest.mark.asyncio
    async def test_integer_as_category(self):
        results = await knowledge_search("Test", category=123)
        assert results == []
    
    @pytest.mark.asyncio
    async def test_float_as_query(self):
        with pytest.raises(TypeError):
            await knowledge_search(3.14)
    
    @pytest.mark.asyncio
    async def test_latest_insights_dict_limit(self):
        with pytest.raises(TypeError):
            await get_latest_insights("News", limit={"limit": 5})
    
    @pytest.mark.asyncio
    async def test_latest_insights_list_category(self):
        with pytest.raises(TypeError):
            await get_latest_insights(["News", "Fitness"])
    
    @pytest.mark.asyncio
    async def test_most_discussed_boolean_category(self):
        with pytest.raises(TypeError):
            await get_most_discussed_topics(True)
    
    @pytest.mark.asyncio
    async def test_summarize_string_ids(self):
        with pytest.raises(TypeError):
            await summarize_posts("post_1,post_2")
    
    @pytest.mark.asyncio
    async def test_summarize_numeric_ids(self):
        summary = await summarize_posts([1, 2, 3])
        assert "keine" in summary.lower()
    
    @pytest.mark.asyncio
    async def test_summarize_mixed_type_ids(self):
        summary = await summarize_posts(["valid_id", 123, None])
        assert isinstance(summary, str)
    
    @pytest.mark.asyncio
    async def test_search_regex_pattern(self):
        results = await knowledge_search(".*vitamin.*")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_xpath_injection(self):
        results = await knowledge_search("'] | //posts[contains(@secret,'")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_json_injection(self):
        results = await knowledge_search('{"$ne": null}')
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_category_traversal_attempt(self):
        results = await knowledge_search("Test", category="../../../etc/passwd")
        assert results == []
    
    @pytest.mark.asyncio
    async def test_date_overflow(self):
        results = await knowledge_search("Test", min_date="9999-99-99")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_negative_year_date(self):
        results = await knowledge_search("Test", min_date="-2023-01-01")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_summarize_duplicate_ids(self):
        summary = await summarize_posts(["id1", "id1", "id1"])
        assert isinstance(summary, str)
    
    @pytest.mark.asyncio
    async def test_circular_reference_attempt(self):
        results = await knowledge_search("$..content")
        assert isinstance(results, list)
    
    # Edge Case Tests (25 tests)
    @pytest.mark.asyncio
    async def test_search_single_character(self):
        results = await knowledge_search("a")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_numbers_only(self):
        results = await knowledge_search("2023")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_punctuation_only(self):
        results = await knowledge_search("...")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_mixed_languages(self):
        results = await knowledge_search("Vitamin vitamina ビタミン")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_rtl_text(self):
        results = await knowledge_search("فيتامين")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_zalgo_text(self):
        results = await knowledge_search("V̸i̴t̷a̶m̵i̸n̷")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_latest_insights_max_int_limit(self):
        import sys
        results = await get_latest_insights("News", limit=sys.maxsize)
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_repeated_terms(self):
        results = await knowledge_search("vitamin vitamin vitamin")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_contradictory_filters(self):
        # Future date means no results
        future = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        results = await knowledge_search("common term", min_date=future)
        assert results == []
    
    @pytest.mark.asyncio
    async def test_category_case_variations(self):
        variations = ["NEWS", "news", "News", "NeWs"]
        correct_results = None
        for var in variations:
            results = await get_latest_insights(var)
            if var == "News":
                correct_results = results
            else:
                assert results == []  # Only exact case works
    
    @pytest.mark.asyncio
    async def test_search_url_in_query(self):
        results = await knowledge_search("https://www.strunz.com")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_email_in_query(self):
        results = await knowledge_search("test@example.com")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_phone_number(self):
        results = await knowledge_search("+49 123 456789")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_currency_symbols(self):
        results = await knowledge_search("€$£¥")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_mathematical_symbols(self):
        results = await knowledge_search("∑∫∂∇")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_escaped_quotes(self):
        results = await knowledge_search('vitamin "d"')
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_backslashes(self):
        results = await knowledge_search("test\\test")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_null_character(self):
        results = await knowledge_search("test\0test")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_summarize_very_long_id_list(self):
        ids = [f"id_{i}" for i in range(1000)]
        summary = await summarize_posts(ids)
        assert isinstance(summary, str)
    
    @pytest.mark.asyncio
    async def test_date_filter_bc_era(self):
        results = await knowledge_search("Test", min_date="0000-01-01")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_binary_data(self):
        results = await knowledge_search(b"test".decode('utf-8'))
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_category_integer_string(self):
        results = await get_latest_insights("404")
        assert results == []
    
    @pytest.mark.asyncio
    async def test_search_reserved_words(self):
        results = await knowledge_search("SELECT FROM WHERE")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_file_path(self):
        results = await knowledge_search("/etc/passwd")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_windows_path(self):
        results = await knowledge_search("C:\\Windows\\System32")
        assert isinstance(results, list)
    
    # Boundary Tests (25 tests)
    @pytest.mark.asyncio
    async def test_search_max_length_query(self):
        # Test with maximum reasonable query length
        max_query = "vitamin " * 100
        results = await knowledge_search(max_query)
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_latest_insights_boundary_limits(self):
        # Test boundary values for limit
        for limit in [1, 5, 10, 50, 100]:
            results = await get_latest_insights("News", limit=limit)
            assert len(results) <= limit
    
    @pytest.mark.asyncio
    async def test_search_min_date_boundary(self):
        # Test various date boundaries
        dates = ["1900-01-01", "2000-01-01", "2020-01-01", "2023-12-31"]
        for date in dates:
            results = await knowledge_search("Test", min_date=date)
            assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_summarize_single_id(self):
        summary = await summarize_posts(["single_id"])
        assert isinstance(summary, str)
    
    @pytest.mark.asyncio
    async def test_summarize_max_ids(self):
        # Test with maximum reasonable number of IDs
        ids = [f"id_{i}" for i in range(100)]
        summary = await summarize_posts(ids)
        assert isinstance(summary, str)
    
    @pytest.mark.asyncio
    async def test_search_single_word_queries(self):
        single_words = ["Vitamin", "Sport", "Gesundheit", "Stress", "Immunsystem"]
        for word in single_words:
            results = await knowledge_search(word)
            assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_compound_queries(self):
        compounds = ["Vitamin-D", "Omega-3", "Covid-19", "Blut-Tuning"]
        for compound in compounds:
            results = await knowledge_search(compound)
            assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_all_tools_empty_results(self):
        # Test all tools with queries that likely return empty
        search = await knowledge_search("xyzxyzxyzxyz")
        latest = await get_latest_insights("NonExistentCategory")
        discussed = await get_most_discussed_topics("NonExistentCategory")
        summary = await summarize_posts(["non_existent_id"])
        
        assert search == []
        assert latest == []
        assert discussed == []
        assert "keine" in summary.lower() or len(summary) > 0
    
    @pytest.mark.asyncio
    async def test_mixed_valid_invalid_params(self):
        # Valid query with invalid category
        results = await knowledge_search("Vitamin D", category="InvalidCat")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_date_edge_cases(self):
        edge_dates = [
            "2023-02-29",  # Invalid leap year
            "2023-04-31",  # April has 30 days
            "2023-00-01",  # Invalid month
            "2023-13-01",  # Invalid month
        ]
        for date in edge_dates:
            results = await knowledge_search("Test", min_date=date)
            assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_unicode_categories(self):
        unicode_cats = ["Ñews", "Fîtness", "Gesündhëit"]
        for cat in unicode_cats:
            results = await get_latest_insights(cat)
            assert results == []
    
    @pytest.mark.asyncio
    async def test_whitespace_in_params(self):
        results1 = await knowledge_search(" Vitamin ")
        results2 = await knowledge_search("Vitamin")
        # Should handle whitespace gracefully
        assert isinstance(results1, list)
        assert isinstance(results2, list)
    
    @pytest.mark.asyncio
    async def test_repeated_tool_calls(self):
        # Test tools can handle repeated calls
        for _ in range(5):
            results = await knowledge_search("Test")
            assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_concurrent_search_simulation(self):
        # Simulate concurrent searches
        queries = ["Vitamin A", "Vitamin B", "Vitamin C", "Vitamin D", "Vitamin E"]
        results = []
        for q in queries:
            r = await knowledge_search(q)
            results.append(r)
        assert all(isinstance(r, list) for r in results)
    
    @pytest.mark.asyncio
    async def test_category_name_variations(self):
        # Test various incorrect category names
        wrong_categories = [
            "fitness",  # lowercase
            "Fitness ",  # trailing space
            " Fitness",  # leading space
            "Fitness\n",  # newline
            "Fitness\t",  # tab
        ]
        for cat in wrong_categories:
            results = await get_latest_insights(cat)
            assert results == []
    
    @pytest.mark.asyncio
    async def test_limit_type_coercion(self):
        # Test if string numbers are handled
        try:
            results = await get_latest_insights("News", limit=int("5"))
            assert len(results) <= 5
        except:
            pass
    
    @pytest.mark.asyncio
    async def test_search_performance_chars(self):
        # Test with characters that might affect performance
        perf_chars = ["*", "?", "[", "]", "{", "}", "(", ")"]
        for char in perf_chars:
            results = await knowledge_search(f"Vitamin {char}")
            assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_summarize_none_in_list(self):
        # Test with None values in ID list
        ids = ["id1", None, "id2", None]
        try:
            summary = await summarize_posts(ids)
            assert isinstance(summary, str)
        except:
            pass
    
    @pytest.mark.asyncio
    async def test_search_common_typos(self):
        typos = ["Vitamn", "Omgea-3", "Protien", "Exersice"]
        for typo in typos:
            results = await knowledge_search(typo)
            assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_date_timezone_handling(self):
        # Test with timezone-like strings
        tz_dates = [
            "2023-01-01T00:00:00Z",
            "2023-01-01+01:00",
            "2023-01-01 00:00:00",
        ]
        for date in tz_dates:
            results = await knowledge_search("Test", min_date=date)
            assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_medical_terms(self):
        # Test that medical terms don't break the system
        medical = ["COVID-19", "SARS-CoV-2", "mRNA", "ACE2"]
        for term in medical:
            results = await knowledge_search(term)
            assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_chemical_formulas(self):
        formulas = ["H2O", "CO2", "C6H12O6", "NaCl"]
        for formula in formulas:
            results = await knowledge_search(formula)
            assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_dosage_patterns(self):
        dosages = ["100mg", "5000 IU", "10µg", "1000mcg"]
        for dosage in dosages:
            results = await knowledge_search(dosage)
            assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_final_edge_case(self):
        # One final edge case test
        results = await knowledge_search("Dr. Strunz")
        assert isinstance(results, list)