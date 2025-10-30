# 🧠 Review/Summary Feature — Technical Design

### 🌟 **Goal**
Add a **post-labeling intelligence layer** that:
1. **Summarizes labeling sessions** (stats, time, balance, quality).  
2. **Reviews uncertain or inconsistent labels.**  
3. **Optionally uses AI (Gemini)** to generate a natural-language summary or insights.

---

## ⚙️ 1. Overview

**Feature Name:** `Review/Summary`  
**Main Script:** `review_summary.py`  
**Input:** JSON log from labeling session  
**Output:**  
- Console summary  
- JSON + Markdown/HTML report  
- Optional Gemini-generated text summary  

---

## 🧩 2. Data Flow

```text
label_sentences.py 
     ↓
outputs/session_log.json 
     ↓
review_summary.py 
     ↓
reports/session_summary.json / .md / .html
```

---

## 🧠 3. Core Steps

| Step | Function | Description |
|------|-----------|-------------|
| 1️⃣ | `load_data()` | Load JSON logs of labeled items |
| 2️⃣ | `compute_stats()` | Count total labels, average time, label distribution |
| 3️⃣ | `detect_conflicts()` | Find inconsistent / long-duration / low-confidence labels |
| 4️⃣ | `generate_summary()` | Print concise stats to terminal |
| 5️⃣ | `save_report()` | Export JSON + human-readable Markdown/HTML summary |
| 6️⃣ *(optional)* | `ai_summary()` | Use Gemini API to generate text review summary |

---

## 💻 4. Example CLI Usage

```bash
python review_summary.py --input logs/session_2025-10-29.json
```

**With AI Summary:**
```bash
python review_summary.py --input logs/session_2025-10-29.json --ai
```

---

## 🧮 5. Key Functions (Pseudocode)

```python
def compute_stats(data):
    total = len(data)
    avg_time = sum(item["duration"] for item in data) / total
    label_counts = Counter(item["label"] for item in data)
    return {"total": total, "avg_time": avg_time, "label_counts": label_counts}

def ai_summary(stats):
    from google import generativeai as genai
    import os
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    prompt = f"Summarize labeling session insights:\n{stats}"
    model = genai.GenerativeModel("gemini-1.5-pro")
    return model.generate_content(prompt).text
```

---

## 📊 6. Example Output (Console)

```
🧾 Review Summary — session_2025-10-29
--------------------------------------
Total pairs labeled: 320
Average time per label: 5.2 s
Label balance: Positive 62% | Negative 38%
Disagreements detected: 4
--------------------------------------
AI Insight: "You labeled efficiently, but some negatives show high hesitation — consider clarifying class definitions."
```

---

## 🧱 7. Folder Structure

```
human-in-the-loop-data-labeler/
│
├── label_sentences.py
├── review_summary.py      # <-- new feature
├── utils/
│   ├── stats.py
│   ├── visualize.py
│   └── ai_summary.py
├── logs/
│   └── session_2025-10-29.json
├── reports/
│   └── summary_2025-10-29.md
└── README.md
```

---

## 🚀 8. Expansion Ideas

| Future Upgrade | Description |
|----------------|-------------|
| 📈 **Charts (optional)** | Add simple bar chart or pie chart via `matplotlib` |
| 🔁 **Interactive Review** | Filter and re-label flagged items |
| 🤝 **Multi-Labeler Comparison** | Add inter-annotator agreement metrics |
| 📦 **Export Skill (MCP)** | Wrap report generation as a Skill or MCP endpoint for AI systems |

---

## 💬 9. AI-Vibecoding Philosophy

Keep it **simple, modular, and observable**:
- *Human-readable → Machine-actionable.*
- *Every function can stand alone as a “Skill.”*
- *Outputs are explainable by both humans and AI collaborators.*
