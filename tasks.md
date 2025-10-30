# Tasks: Human-in-the-Loop Data Labeler Enhancement

This document outlines four key task components to enhance the human-in-the-loop data labeling tool with progress tracking, performance monitoring, and quality assurance capabilities.

## 1. Progress Tracking

### Purpose
Track the current position within the labeling workflow to provide users with clear visibility into their progress.

### Implementation
- **Format**: `(x/n)` where `x` is current question number and `n` is total number of questions
- **Display**: Show progress prominently in the UI (e.g., "Progress: 15/100 (15%)")
- **Navigation**: Allow users to see remaining work and estimate completion time
- **Persistence**: Save current position to enable resuming interrupted sessions

### Features
- Real-time progress updates after each label
- Percentage completion calculation
- Estimated remaining time based on current pace
- Progress bar visualization
- Session resumption capability

## 2. Time Tracking

### Purpose
Monitor and record how long users take to complete each labeling task for performance analysis and workflow optimization.

### Implementation
- **Per-question timing**: Record start and end times for each individual labeling decision
- **Session timing**: Track total session duration and active labeling time
- **Granular data**: Store timestamps with millisecond precision
- **Background processing**: Timing continues even if users pause or take breaks

### Data Storage
- Create `./performance/timing_data.json` with structure:
```json
{
  "session_id": "timestamp-based-id",
  "task_type": "classify|rank",
  "total_questions": 100,
  "question_times": [
    {
      "question_id": 1,
      "start_time": "2025-01-15T10:30:15.123Z",
      "end_time": "2025-01-15T10:30:22.456Z",
      "duration_seconds": 7.333,
      "user_label": "true|false|a|b|skip"
    }
  ],
  "session_metrics": {
    "total_time_seconds": 1200,
    "active_time_seconds": 800,
    "average_time_per_question": 12.5,
    "break_time_seconds": 400
  }
}
```

### Features
- Automatic pause detection when user is inactive
- Time-based warnings for unusually fast/slow responses
- Cumulative time tracking across multiple sessions
- Export timing data for analysis

## 3. Ground Truth Comparison

### Purpose
Secretly compare user responses against ground truth labels to assess labeling quality and consistency without revealing the correct answers during the labeling process.

### Implementation
- **Blind comparison**: Users don't see ground truth during labeling
- **Accuracy tracking**: Calculate real-time accuracy scores
- **Discrepancy logging**: Record cases where user disagrees with ground truth
- **Quality thresholds**: Define minimum accuracy requirements for continued participation

### Data Storage
- Extend `./performance/` directory with `./performance/accuracy_data.json`:
```json
{
  "session_id": "timestamp-based-id",
  "task_type": "classify|rank",
  "total_questions": 100,
  "accuracy_metrics": {
    "overall_accuracy": 0.92,
    "correct_count": 92,
    "incorrect_count": 8,
    "skipped_count": 0,
    "confidence_scores": [0.9, 0.95, 0.88, ...]
  },
  "question_results": [
    {
      "question_id": 1,
      "user_label": "true",
      "ground_truth": "true",
      "is_correct": true,
      "response_time_seconds": 7.333
    }
  ],
  "quality_assessment": {
    "meets_minimum_threshold": true,
    "quality_score": 0.92,
    "reliability_rating": "high"
  }
}
```

### Features
- Statistical analysis of labeling patterns
- Identification of systematic biases
- Confidence interval calculations
- Early warning system for poor performance
- Comparison against historical performance

## 4. Summary and Reviewer Scoring

### Purpose
Analyze user performance across time and accuracy metrics to provide comprehensive feedback and assign reviewer quality scores.

### Implementation
- **Multi-dimensional scoring**: Combine speed and accuracy into unified quality metrics
- **Performance categorization**: Classify reviewers as fast/slow and good/bad
- **Trend analysis**: Track performance improvement or degradation over time
- **Comparative analysis**: Benchmark against other reviewers or historical averages

### Scoring Matrix
| Speed \ Accuracy | Excellent (>95%) | Good (85-95%) | Fair (70-85%) | Poor (<70%) |
|------------------|------------------|---------------|---------------|-------------|
| Fast (<5s)       | Fast & Good      | Fast & Fair   | Fast & Poor   | Very Poor   |
| Normal (5-15s)   | Excellent        | Good          | Fair          | Poor        |
| Slow (>15s)      | Slow & Good      | Slow & Fair   | Slow & Poor   | Very Poor   |

### Summary Report Generation
- Create `./reports/performance_summary_{timestamp}.md`:
```markdown
# Labeling Performance Summary

## Overall Score: 8.2/10 (Excellent)

### Time Metrics
- Average time per question: 8.5 seconds
- Total session time: 25 minutes
- Speed rating: Normal

### Accuracy Metrics
- Overall accuracy: 94.5%
- Correct responses: 47/50
- Accuracy rating: Excellent

### Reviewer Classification
**Result: Good & Normal**
- Consistent performance with high accuracy
- Response times within expected range
- Meets quality standards for continued participation

### Recommendations
- Maintain current pace and accuracy
- Consider advanced labeling tasks
- Potential for training new reviewers
```

### Features
- Performance trends over multiple sessions
- Personalized recommendations for improvement
- Qualification levels for different task complexities
- Automated performance alerts
- Integration with quality control workflows

## Integration Points

### UI Enhancements
- Progress indicator in main interface
- Subtle performance indicators (optional display)
- Session summary on completion
- Historical performance viewing

### Data Management
- Automatic cleanup of old performance data
- Aggregated reporting across sessions
- Privacy-preserving data storage
- Export capabilities for external analysis

### Quality Control
- Minimum accuracy thresholds for task assignment
- Performance-based routing to appropriate task difficulties
- Automatic reviewer tier management
- Intervention triggers for poor performance

## File Structure Additions

```
performance/
├── timing_data.json          # Per-session timing information
├── accuracy_data.json        # Ground truth comparison results
├── reviewer_profile.json     # Long-term performance tracking
└── aggregated_metrics.json   # Cross-session analysis

reports/
├── performance_summary_*.md  # Per-session performance reports
└── reviewer_trends_*.md      # Long-term trend analysis
```

## Privacy and Ethical Considerations

- Store timing data securely and anonymize where appropriate
- Provide users with access to their own performance data
- Allow users to opt-out of detailed performance tracking
- Use performance data only for quality improvement purposes
- Maintain transparency about data collection and usage