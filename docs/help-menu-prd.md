# Product Requirements Document (PRD)
## Help Menu System for Human-in-the-Loop Data Labeler

**Document Version:** 1.0
**Date:** October 29, 2025
**Author:** Claude Code Assistant
**Status:** Implemented

---

## Executive Summary

This PRD documents the implementation of a comprehensive help menu system for the human-in-the-loop data labeler. The system provides users with contextual help, workflow-specific guidance, and the ability to recall introduction messages during labeling sessions. This enhancement addresses user experience gaps and reduces friction during the labeling process.

---

## Problem Statement

### Current Issues
1. **No in-app help** - Users have no way to get assistance during labeling sessions
2. **Unclear workflows** - Users may forget instructions or get confused about task requirements
3. **Limited guidance** - No explanation of metrics, validation rules, or output file organization
4. **No keyboard shortcuts reference** - Users may not know available navigation options

### User Pain Points
- Users forget what the different metrics mean (accuracy, precision, recall, F1)
- Users don't understand why certain records are automatically skipped
- Users need to remember input validation rules and field requirements
- Users may want to re-read the introduction message but can't
- Users lack context about how the system handles data privacy and reproducibility

---

## Solution Overview

### Proposed Solution
Implement an interactive help menu system accessible via the 'h' key that provides:
1. **Context-sensitive help** based on current workflow (classification or ranking)
2. **Introduction message recall** for users who need task refreshers
3. **General system help** covering validation, outputs, and metrics
4. **Comprehensive keyboard shortcuts reference**

### Key Features
- **Interactive help menu** with numbered options
- **Workflow-specific guidance** for classification and ranking tasks
- **Introduction message recall** functionality
- **Privacy and validation explanations**
- **Metrics and output file explanations**

---

## User Experience Flow

### Help Menu Access
1. User presses 'h' during any labeling workflow
2. Interactive help menu appears with 3 options
3. User selects desired help option
4. Help content is displayed
5. User can select additional help options or press Enter to return to labeling

### Help Menu Options

#### Option 1: Task-Specific Help
Shows workflow-specific guidance combined with general system help.

#### Option 2: Recall Introduction Message
Redisplays the original introduction message for the current workflow.

#### Option 3: General Help
Shows system-wide help covering validation, outputs, and metrics.

---

## User Interface Preview

### Classification Workflow Help Menu

```
======================================================================
HELP MENU
======================================================================

Help options:
  1 - Show task-specific help
  2 - Recall introduction message
  3 - Show general help

Select help option (1-3) or Enter to exit help:
```

**Option 1: Classification-Specific Help**
```
GENERAL HELP
----------------------------------------

KEYBOARD SHORTCUTS:
  h     - Show this help menu
  s     - Skip current item (continue to next)
  Ctrl+C - Exit the program

INPUT VALIDATION:
  • All text is normalized to 7-bit ASCII for console compatibility
  • Records longer than max_len characters are skipped automatically
  • Missing or empty required fields are skipped automatically
  • All skipped items are logged with privacy-preserving hashes

OUTPUT FILES:
  • outputs/ - Human-labeled data files
  • logs/    - Structured JSON logs with metrics and metadata
  • reports/ - Human-readable text reports

REPRODUCIBILITY:
  • Items are shuffled using the seed value (--seed)
  • Same seed = same order across different runs
  • Default seed is 42

METRICS EXPLANATION:
  • Accuracy: Overall correct labeling rate
  • Precision: Of items labeled X, how many were actually X
  • Recall: Of actual X items, how many were labeled X
  • F1 Score: Harmonic mean of precision and recall

PRIVACY NOTES:
  • Logs store text previews with SHA256 hashes, not full text
  • Human output files contain original text content
  • No personal data is collected or transmitted

CLASSIFICATION WORKFLOW HELP:
----------------------------------------

YOUR TASK:
  Determine if two sentences have similar semantic meaning

LABELING OPTIONS:
  t, true  - Sentences ARE semantically similar
  f, false - Sentences are NOT semantically similar
  s        - Skip this item

INPUT FORMAT:
  • sentence_base: The reference sentence
  • sentence_test: The sentence to compare against base
  • label_semantic_similarity: Gold label (hidden from you)

EXAMPLES:
  Base: 'The cat sits on the mat'
  Test: 'A feline rests on the rug'
  Label: t (true - similar meaning)

  Base: 'I love programming'
  Test: 'The weather is cold today'
  Label: f (false - different meaning)
```

**Option 2: Introduction Message Recall**
```
======================================================================
CLASSIFICATION Workflow: Semantic Similarity Labeling
======================================================================
You will label whether sentence pairs are semantically similar.
For each item, you'll see:
  • A base sentence
  • A test sentence to compare against the base

Your task: Determine if the test sentence has similar meaning to the base sentence.
  • Type 't' (true) if they ARE semantically similar
  • Type 'f' (false) if they are NOT semantically similar
  • Type 's' to skip the current item
  • Type 'h' to show help menu

Example:
  Base: 'The cat sits on the mat'
  Test: 'A feline is resting on the rug'
  Label: 't' (true - they have similar meaning)

All outputs are saved to outputs/, logs/, and reports/ directories
Press Ctrl+C to exit at any time

Starting classification workflow...
```

### Ranking Workflow Help Menu

**Option 1: Ranking-Specific Help**
```
GENERAL HELP
----------------------------------------

KEYBOARD SHORTCUTS:
  h     - Show this help menu
  s     - Skip current item (continue to next)
  Ctrl+C - Exit the program

INPUT VALIDATION:
  • All text is normalized to 7-bit ASCII for console compatibility
  • Records longer than max_len characters are skipped automatically
  • Missing or empty required fields are skipped automatically
  • All skipped items are logged with privacy-preserving hashes

OUTPUT FILES:
  • outputs/ - Human-labeled data files
  • logs/    - Structured JSON logs with metrics and metadata
  • reports/ - Human-readable text reports

REPRODUCIBILITY:
  • Items are shuffled using the seed value (--seed)
  • Same seed = same order across different runs
  • Default seed is 42

METRICS EXPLANATION:
  • Accuracy: Overall correct labeling rate
  • Precision: Of items labeled X, how many were actually X
  • Recall: Of actual X items, how many were labeled X
  • F1 Score: Harmonic mean of precision and recall

PRIVACY NOTES:
  • Logs store text previews with SHA256 hashes, not full text
  • Human output files contain original text content
  • No personal data is collected or transmitted

RANKING WORKFLOW HELP:
----------------------------------------

YOUR TASK:
  Choose which sentence is more similar to the base sentence

LABELING OPTIONS:
  a - Sentence (a) is more similar to base
  b - Sentence (b) is more similar to base
  s - Skip this item

INPUT FORMAT:
  • sentence_base: The reference sentence
  • sentence_a: First comparison option
  • sentence_b: Second comparison option
  • label_more_similar: Gold label (hidden from you)

EXAMPLES:
  Base: 'The weather is nice today'
  (a): 'It\'s a beautiful sunny day'
  (b): 'I need to buy groceries'
  Label: a (sentence a is more similar)

  Base: 'Programming in Python is fun'
  (a): 'Java is also a programming language'
  (b): 'The cat is sleeping'
  Label: a (sentence a is more similar to programming)
```

**Option 2: Introduction Message Recall**
```
======================================================================
RANKING Workflow: Pairwise Similarity Comparison
======================================================================
You will choose which of two sentences is more similar to a base sentence.
For each item, you'll see:
  • A base sentence
  • Sentence (a): First comparison option
  • Sentence (b): Second comparison option

Your task: Determine which sentence (a or b) is more similar to the base.
  • Type 'a' if sentence (a) is more similar to the base
  • Type 'b' if sentence (b) is more similar to the base
  • Type 's' to skip the current item
  • Type 'h' to show help menu

Example:
  Base: 'The weather is nice today'
  (a): 'It's a beautiful sunny day'
  (b): 'I need to buy groceries'
  Label: 'a' (sentence a is more similar to the base)

All outputs are saved to outputs/, logs/, and reports/ directories
Press Ctrl+C to exit at any time

Starting ranking workflow...
```

---

## Technical Implementation

### Architecture Changes
1. **Help System Module** (`label_sentences.py:154-295`)
   - `print_help_menu()`: Interactive help menu interface
   - `print_general_help()`: System-wide help information
   - `print_classification_help()`: Classification-specific guidance
   - `print_ranking_help()`: Ranking-specific guidance
   - `print_introduction_message()`: Introduction message recall

2. **Workflow Integration**
   - Updated input prompts to include 'h' option
   - Modified workflow loops to handle help menu access
   - Added current item redisplay after help menu exit

### Code Locations
- **Help System**: `label_sentences.py:154-295`
- **Classification Integration**: `label_sentences.py:371-381`
- **Ranking Integration**: `label_sentences.py:472-483`
- **Introduction Messages**: `label_sentences.py:296-330`

### Key Functions
```python
# Help menu interface (label_sentences.py:156)
def print_help_menu(workflow_type="general")

# General system help (label_sentences.py:197)
def print_general_help()

# Workflow-specific help (label_sentences.py:235, 264)
def print_classification_help()
def print_ranking_help()

# Introduction message recall (label_sentences.py:296)
def print_introduction_message(workflow_type)
```

---

## Success Metrics

### User Experience Metrics
1. **Reduced confusion** - Users understand task requirements and input validation
2. **Faster onboarding** - New users can reference help during initial sessions
3. **Fewer errors** - Clearer understanding of valid inputs and expectations
4. **Improved confidence** - Users feel supported with accessible help

### Technical Metrics
1. **Zero external dependencies** - Help system uses only existing Python standard library
2. **Backward compatibility** - Existing workflows and outputs remain unchanged
3. **Performance** - Help menu access has negligible impact on labeling performance
4. **Maintainability** - Clean separation of help content from core logic

---

## Requirements

### Functional Requirements
- [x] Users can access help menu by pressing 'h' during labeling
- [x] Help menu provides 3 clear options (task-specific, intro recall, general)
- [x] Help content is contextual to current workflow (classification vs ranking)
- [x] Users can navigate between help options and return to labeling
- [x] Introduction messages can be recalled on demand
- [x] Help covers keyboard shortcuts, validation, outputs, and metrics

### Non-Functional Requirements
- [x] Help system maintains zero external dependencies
- [x] Help menu performance is instantaneous
- [x] Help content is comprehensive and clear
- [x] System remains backward compatible
- [x] Help is accessible at any point during labeling

### Accessibility Requirements
- [x] Clear, readable formatting with consistent visual hierarchy
- [x] Simple keyboard navigation (numbered options, Enter to exit)
- [x] Comprehensive explanations for technical concepts
- [x] Examples for complex concepts (metrics, validation)

---

## Implementation Status

### Completed Features
- [x] Interactive help menu interface
- [x] General system help covering all workflows
- [x] Classification-specific help with examples
- [x] Ranking-specific help with examples
- [x] Introduction message recall functionality
- [x] Integration with existing workflow loops
- [x] Updated input prompts with 'h' option
- [x] Current item redisplay after help menu

### Ready for Hotkey Integration
- [x] Help menu infrastructure is complete and functional
- [x] Integration points established for 'h' key handling
- [x] Help content covers all identified user needs

---

## Future Enhancements

### Potential Improvements
1. **Search functionality** - Allow users to search help content
2. **Contextual tooltips** - Brief help hints for specific fields
3. **Video tutorials** - Visual guidance for complex workflows
4. **FAQ section** - Common questions and troubleshooting
5. **Progress indicators** - Show user progress through help sections

### Long-term Vision
- Expand help system to cover additional workflows
- Implement analytics to track help usage patterns
- Create comprehensive user documentation portal
- Develop interactive tutorials for new users

---

## Conclusion

The help menu system successfully addresses user experience gaps in the human-in-the-loop data labeler. By providing comprehensive, contextual help accessible via a simple keyboard shortcut, users can now get immediate assistance during labeling sessions. The implementation maintains the tool's zero-dependency philosophy while significantly improving usability and reducing user friction.

The system is fully implemented and ready for the 'h' hotkey integration, providing users with a complete help experience that covers task-specific guidance, system information, and introduction message recall.