# StrunzKnowledge Update System Guide

## Overview

The StrunzKnowledge Update System is a comprehensive solution for managing content updates, monitoring system health, and maintaining the FAISS knowledge base. It implements the complete update process with testing, incremental updates, monitoring, and automated maintenance.

## 🚀 Quick Start

### 1. Check System Status
```bash
python src/scripts/integrated_update_system.py check-status
```

### 2. Test Updates (Recommended First Step)
```bash
# Test news updates
python src/scripts/integrated_update_system.py test-update --news-only

# Test forum updates  
python src/scripts/integrated_update_system.py test-update --forums-only

# Test all content
python src/scripts/integrated_update_system.py test-update
```

### 3. Run Production Updates
```bash
# Full update with monitoring
python src/scripts/integrated_update_system.py full-update --monitor

# News only update
python src/scripts/integrated_update_system.py full-update --news-only --monitor

# Unlimited scraping (use with caution)
python src/scripts/integrated_update_system.py full-update --unlimited --monitor
```

## 📊 System Components

### 1. Update Manager (`src/scripts/update_manager.py`)
- Orchestrates the complete update process
- Implements test-first approach
- Handles production updates with safety checks
- Manages FAISS index rebuilding

### 2. Incremental Updater (`src/scripts/incremental_updater.py`)
- Tracks content changes with hashing
- Performs efficient incremental FAISS updates
- Maintains update history and statistics
- Provides rollback capabilities

### 3. Monitoring System (`src/scripts/monitoring_system.py`)
- Real-time performance monitoring
- Resource usage tracking
- Alert system for thresholds
- Comprehensive reporting

### 4. Integrated System (`src/scripts/integrated_update_system.py`)
- Main entry point combining all components
- Simplified command-line interface
- Automated workflows
- System health reporting

## 🔧 Command Reference

### System Status
```bash
# Check overall system health
python src/scripts/integrated_update_system.py check-status

# Generate comprehensive report
python src/scripts/integrated_update_system.py report
```

### Content Updates
```bash
# Test updates (always run first)
python src/scripts/integrated_update_system.py test-update [--news-only|--forums-only] [--monitor]

# Production updates
python src/scripts/integrated_update_system.py full-update [--news-only|--forums-only] [--unlimited] [--monitor]
```

### Forum Analysis
```bash
# Analyze forum structure
python src/scripts/integrated_update_system.py analyze-forums

# Analyze and attempt fixes
python src/scripts/integrated_update_system.py analyze-forums --fix-issues
```

### Monitoring
```bash
# Run monitoring for 60 minutes (default)
python src/scripts/integrated_update_system.py monitor

# Run monitoring for specific duration
python src/scripts/integrated_update_system.py monitor --duration 120
```

### Maintenance
```bash
# Cleanup old data (keep 30 days)
python src/scripts/integrated_update_system.py cleanup

# Cleanup with custom retention
python src/scripts/integrated_update_system.py cleanup --keep-days 14
```

## 🔍 Individual Component Usage

### Update Manager
```bash
# Test scraping
python src/scripts/update_manager.py test-news
python src/scripts/update_manager.py test-forums

# Production updates
python src/scripts/update_manager.py update-news
python src/scripts/update_manager.py update-forums
python src/scripts/update_manager.py full-update

# Analysis and maintenance
python src/scripts/update_manager.py analyze-forums
python src/scripts/update_manager.py rebuild-indices
python src/scripts/update_manager.py check-updates
```

### Scraping Manager
```bash
# Direct scraping operations
python -m src.scripts.scraping_manager --test --news-only
python -m src.scripts.scraping_manager --news-only --max-pages 10
python -m src.scripts.scraping_manager --forum-only --unlimited
```

## 📋 Update Process Flow

### 1. Pre-Update Checks
- System health verification
- Resource availability check
- Previous update status review
- Backup creation

### 2. Test Phase
- Limited scraping (2 pages per category)
- Content quality validation
- Performance metrics collection
- Error detection

### 3. Production Phase
- Full scraping based on test results
- Incremental change detection
- Content processing and integration
- FAISS index updates

### 4. Post-Update
- Validation of new indices
- Performance report generation
- Cleanup of old data
- System health check

## 🔄 Incremental Updates

### Content Change Detection
- SHA256 hashing of content
- URL-based tracking
- Modification timestamps
- Deletion detection (7-day grace period)

### FAISS Index Updates
- Automatic backups before updates
- Incremental additions/modifications
- Efficient removal of deleted content
- Rollback capabilities on failure

### Update History
- Detailed tracking of all changes
- Success/failure statistics
- Performance metrics
- Audit trail maintenance

## 📊 Monitoring and Alerting

### Performance Metrics
- CPU and memory usage
- Disk space utilization
- Network activity
- Process statistics

### Scraping Metrics
- Items processed per second
- Success rates
- Error counts
- Response times

### Alert Thresholds
- CPU usage > 80%
- Memory usage > 85%
- Disk usage > 90%
- Error rate > 10%
- Low performance < 0.5 items/sec

### Reporting
- Real-time metrics collection
- Periodic report generation
- Historical trend analysis
- Health status summaries

## 🛠️ Forum Structure Analysis

### Current Issues Detection
- Missing thread links
- Pagination problems
- Accessibility issues
- Selector mismatches

### Automatic Fixes
- URL pattern updates
- Selector corrections
- Timeout adjustments
- Retry logic improvements

### Manual Intervention
- Complex structure changes
- New forum categories
- Authentication requirements
- Anti-scraping measures

## 📂 Directory Structure

```
src/scripts/
├── update_manager.py              # Main update orchestrator
├── incremental_updater.py         # Incremental update system
├── monitoring_system.py           # Monitoring and alerting
├── integrated_update_system.py    # Combined interface
├── scraping_manager.py            # Scraping operations
└── check_new_content.py           # Content change detection

data/
├── scraped/                       # Scraping results
├── tracking/                      # Change tracking data
├── faiss_indices/                 # FAISS indices
│   └── incremental_backups/       # Index backups
└── processed/                     # Processed content

logs/
├── update_manager.log             # Update operations
├── monitoring.log                 # Monitoring events
├── monitoring/                    # Monitoring reports
│   ├── monitoring_report_*.json   # Periodic reports
│   └── final_monitoring_report_*.json  # Session summaries
└── system_report_*.json           # System status reports
```

## 🔐 Best Practices

### 1. Testing First
- Always run test updates before production
- Review test results for quality and errors
- Check system resources before full updates

### 2. Monitoring
- Enable monitoring for all production updates
- Review alerts and performance metrics
- Investigate any unusual patterns

### 3. Incremental Updates
- Use incremental updates for efficiency
- Monitor backup creation and validation
- Keep update history for troubleshooting

### 4. Maintenance
- Run regular cleanup to manage disk space
- Monitor system health continuously
- Review and act on recommendations

### 5. Error Handling
- Check logs for detailed error information
- Use rollback capabilities when needed
- Report persistent issues for investigation

## 🚨 Troubleshooting

### Common Issues

#### 1. Forum Scraping Failures
```bash
# Analyze forum structure
python src/scripts/integrated_update_system.py analyze-forums --fix-issues

# Check logs for specific errors
tail -f logs/update_manager.log
```

#### 2. FAISS Index Problems
```bash
# Rebuild indices from scratch
python src/scripts/update_manager.py rebuild-indices

# Check index health
python src/scripts/integrated_update_system.py check-status
```

#### 3. Performance Issues
```bash
# Monitor system resources
python src/scripts/integrated_update_system.py monitor --duration 30

# Review performance metrics
python src/scripts/integrated_update_system.py report
```

#### 4. Memory Issues
- Reduce scraping page limits
- Enable incremental updates
- Monitor memory usage during operations
- Clean up old data regularly

### Error Codes
- **Status 1**: Operation failed
- **Status 0**: Success
- **SIGINT**: User interruption (Ctrl+C)
- **SIGTERM**: System termination

## 🔮 Future Enhancements

### Planned Features
1. **Web Dashboard**: Real-time monitoring interface
2. **API Integration**: REST API for external systems
3. **Scheduled Updates**: Cron-based automation
4. **Cloud Integration**: Cloud storage and processing
5. **Machine Learning**: Content quality prediction

### Improvement Areas
1. **Parallel Processing**: Multi-threaded scraping
2. **Caching**: Intelligent content caching
3. **Compression**: Efficient data storage
4. **Notifications**: Email/Slack alerts
5. **Analytics**: Advanced usage analytics

## 📞 Support

For issues and questions:
1. Check the logs in `logs/` directory
2. Review system status with `check-status`
3. Generate detailed report with `report`
4. Check GitHub issues for similar problems
5. Create new issue with logs and system report

## 📝 License

This update system is part of the StrunzKnowledge project and follows the same license terms.