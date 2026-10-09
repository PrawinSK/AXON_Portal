import re
import time
import json
import hashlib
import requests
from bs4 import BeautifulSoup
from typing import Optional

from app.services.question_bank import get_db_connection, get_stage_for_difficulty


class InterviewScraper:
    """
    Scrapes interview Q&A content from online educational sources (GFG, GitHub)
    and saves them to the SQLite question bank with indexed keywords.
    """

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    GFG_SOURCES = {
        "machine_learning": [
            "https://www.geeksforgeeks.org/machine-learning-interview-questions/",
            "https://www.geeksforgeeks.org/data-science-interview-questions/"
        ],
        "data_structures": [
            "https://www.geeksforgeeks.org/commonly-asked-data-structure-interview-questions/"
        ],
        "python": [
            "https://www.geeksforgeeks.org/python-interview-questions/"
        ]
    }

    GITHUB_RAW_SOURCES = [
        # DopplerHQ / awesome-interview-questions
        {
            "url": "https://raw.githubusercontent.com/DopplerHQ/awesome-interview-questions/master/README.md",
            "topic": "general"
        }
    ]

    def extract_keywords_from_text(self, text: str) -> list[str]:
        """Extracts technical tokens and phrases from text."""
        normalized = text.lower()
        stopwords = {
            "the", "and", "for", "that", "this", "with", "are", "was", "not",
            "but", "has", "have", "from", "can", "will", "been", "which",
            "each", "more", "also", "than", "other", "into", "its", "they",
            "what", "when", "where", "how", "why", "who", "which", "then",
            "there", "does", "did", "used", "using", "called", "known", "make"
        }
        words = re.findall(r'\b[a-z_][a-z0-9_]{2,}\b', normalized)
        keywords = []
        for w in words:
            if w not in stopwords and len(w) > 3:
                keywords.append(w)

        # Deduplicate preserving order
        return list(dict.fromkeys(keywords))[:15]

    def estimate_difficulty(self, q_text: str, a_text: str) -> int:
        """Determines difficulty 1-5 based on complexity indicators."""
        combined = (q_text + " " + a_text).lower()

        hard_markers = [
            "architecture", "distributed", "concurrency", "internal working",
            "under the hood", "deadlock", "tradeoff", "optimization", "asymptotics",
            "amortized", "proof", "mathematical", "eigenvalues", "multiprocessing"
        ]
        med_markers = [
            "compare", "difference between", "how does", "explain", "why would",
            "pros and cons", "advantages", "disadvantages", "scenario", "implementation"
        ]

        hard_count = sum(1 for m in hard_markers if m in combined)
        med_count = sum(1 for m in med_markers if m in combined)

        if hard_count >= 2 or len(a_text.split()) > 200:
            return 4 if hard_count < 4 else 5
        elif med_count >= 1 or len(a_text.split()) > 80:
            return 3
        else:
            return 2

    def scrape_gfg_url(self, url: str, topic: str) -> list[dict]:
        """Scrapes a GeeksforGeeks interview question article."""
        try:
            resp = requests.get(url, headers=self.HEADERS, timeout=12)
            if resp.status_code != 200:
                print(f"[Scraper] GFG responded with status {resp.status_code} for {url}")
                return []

            soup = BeautifulSoup(resp.text, "html.parser")
            article = soup.select_one("article") or soup.select_one("div.entry-content") or soup
            questions = []

            # GFG usually structures questions as h2 / h3 / strong tags
            headings = article.find_all(["h2", "h3", "h4", "strong"])
            for h in headings:
                q_text = h.get_text(strip=True)
                # Clean numbered prefixes e.g. "1. What is..." or "Q1: What is..."
                cleaned_q = re.sub(r'^(?:Q\d+[:.]|\d+[\.\)])\s*', '', q_text).strip()

                # Basic validation: must be a substantive question
                if len(cleaned_q) < 15 or len(cleaned_q) > 200:
                    continue
                if not any(marker in cleaned_q.lower() for marker in ["what", "how", "why", "explain", "difference", "compare", "when", "?"]):
                    continue

                # Accumulate following paragraph siblings as model answer
                answer_paragraphs = []
                curr = h.find_next_sibling()
                while curr and curr.name not in ["h2", "h3", "h4"]:
                    if curr.name in ["p", "ul", "ol", "pre"]:
                        text = curr.get_text(strip=True)
                        if text and len(text) > 15:
                            answer_paragraphs.append(text)
                    curr = curr.find_next_sibling()
                    if len(answer_paragraphs) >= 4:
                        break

                if not answer_paragraphs:
                    continue

                model_answer = " ".join(answer_paragraphs)
                q_id = f"gfg_{hashlib.md5(cleaned_q.encode()).hexdigest()[:10]}"
                diff = self.estimate_difficulty(cleaned_q, model_answer)
                keywords = self.extract_keywords_from_text(cleaned_q + " " + model_answer)

                questions.append({
                    "id": q_id,
                    "topic": topic,
                    "subtopic": "scraped",
                    "difficulty": diff,
                    "question_text": cleaned_q if cleaned_q.endswith("?") else cleaned_q + "?",
                    "model_answer": model_answer,
                    "keywords": keywords,
                    "related_concepts": keywords[:5]
                })

            print(f"[Scraper] Successfully extracted {len(questions)} Q&As from {url}")
            return questions

        except Exception as e:
            print(f"[Scraper] Error scraping {url}: {e}")
            return []

    def save_questions(self, questions: list[dict]):
        """Persists scraped questions into SQLite database and builds inverted index."""
        if not questions:
            return

        conn = get_db_connection()
        c = conn.cursor()
        saved = 0

        for q in questions:
            stage = get_stage_for_difficulty(q["difficulty"])
            try:
                c.execute("""
                    INSERT OR IGNORE INTO questions
                    (id, topic, subtopic, difficulty, stage, question_text, model_answer, keywords, related_concepts)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    q["id"], q["topic"], q["subtopic"], q["difficulty"], stage,
                    q["question_text"], q["model_answer"],
                    json.dumps(q["keywords"]),
                    json.dumps(q.get("related_concepts", []))
                ))

                if c.rowcount > 0:
                    saved += 1
                    for kw in q["keywords"]:
                        c.execute("""
                            INSERT OR IGNORE INTO keyword_index (keyword, question_id, weight)
                            VALUES (?, ?, 1.0)
                        """, (kw.lower(), q["id"]))

            except Exception as e:
                print(f"[Scraper] Failed to save {q.get('id')}: {e}")

        conn.commit()
        conn.close()
        print(f"[Scraper] Saved {saved} new scraped questions into database.")

    def run_all(self):
        """Scrapes all configured online endpoints."""
        all_qs = []
        for topic, urls in self.GFG_SOURCES.items():
            for url in urls:
                qs = self.scrape_gfg_url(url, topic)
                all_qs.extend(qs)
                time.sleep(1.5)  # respectful delay

        self.save_questions(all_qs)
        return len(all_qs)


scraper = InterviewScraper()
