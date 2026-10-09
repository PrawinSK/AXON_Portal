import json
import uuid
import random
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import httpx
from fastapi import HTTPException, status

DB_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DB_PATH = DB_DIR / "question_bank.db"
EXTERNAL_ANSWER_ENDPOINT = "https://api.greeksforgeeks.com/answers"

DEFAULT_SEED_MCQS = [
    {
        "id": "mcq-cs-001",
        "question_text": "Which data structure operates on a Last-In, First-Out (LIFO) basis?",
        "options": ["Queue", "Stack", "Array", "Linked List"],
        "correct_answer": "Stack",
        "explanation": "A Stack follows the Last-In, First-Out (LIFO) order where elements are added and removed from the same end (the top).",
        "topic": "Data Structures"
    },
    {
        "id": "mcq-cs-002",
        "question_text": "What is the worst-case time complexity of QuickSort?",
        "options": ["O(n log n)", "O(n)", "O(n^2)", "O(log n)"],
        "correct_answer": "O(n^2)",
        "explanation": "QuickSort degrades to O(n^2) when the pivot choice is consistently the smallest or largest element (e.g., already sorted array without random pivoting).",
        "topic": "Algorithms"
    },
    {
        "id": "mcq-cs-003",
        "question_text": "Which HTTP status code signifies that a resource was successfully created?",
        "options": ["200 OK", "201 Created", "204 No Content", "301 Moved Permanently"],
        "correct_answer": "201 Created",
        "explanation": "HTTP 201 Created indicates that the request succeeded and resulted in the creation of a new resource.",
        "topic": "Web Architecture"
    },
    {
        "id": "mcq-cs-004",
        "question_text": "In relational databases, which normal form eliminates transitive functional dependencies?",
        "options": ["1NF", "2NF", "3NF", "BCNF"],
        "correct_answer": "3NF",
        "explanation": "Third Normal Form (3NF) requires 2NF and mandates that no non-prime attribute is transitively dependent on any candidate key.",
        "topic": "DBMS"
    },
    {
        "id": "mcq-cs-005",
        "question_text": "Which indexing data structure is most commonly used in modern relational databases like PostgreSQL and MySQL InnoDB?",
        "options": ["Red-Black Tree", "B+ Tree", "Hash Table", "Binary Search Tree"],
        "correct_answer": "B+ Tree",
        "explanation": "B+ Trees provide balanced shallow tree height and contiguous leaf node links, making range queries and disk block reads extremely efficient.",
        "topic": "DBMS"
    },
    {
        "id": "mcq-cs-006",
        "question_text": "What does ACID stand for in the context of database transactions?",
        "options": [
            "Atomicity, Consistency, Isolation, Durability",
            "Accuracy, Consistency, Integrity, Durability",
            "Atomicity, Concurrency, Isolation, Dependency",
            "Availability, Consistency, Integrity, Durability"
        ],
        "correct_answer": "Atomicity, Consistency, Isolation, Durability",
        "explanation": "ACID guarantees that database transactions are processed reliably across crashes and concurrent operations.",
        "topic": "DBMS"
    },
    {
        "id": "mcq-cs-007",
        "question_text": "In TCP/IP, which protocol provides connectionless, best-effort datagram delivery?",
        "options": ["TCP", "UDP", "SCTP", "BGP"],
        "correct_answer": "UDP",
        "explanation": "UDP (User Datagram Protocol) is connectionless and does not guarantee packet delivery, ordering, or duplicate protection.",
        "topic": "Networking"
    },
    {
        "id": "mcq-cs-008",
        "question_text": "Which process scheduling algorithm can cause starvation for high burst-time processes?",
        "options": ["Round Robin", "Shortest Job First (SJF)", "First-Come, First-Served (FCFS)", "Multilevel Feedback Queue"],
        "correct_answer": "Shortest Job First (SJF)",
        "explanation": "In Shortest Job First, long processes can starve if shorter processes arrive continuously.",
        "topic": "Operating Systems"
    },
    {
        "id": "mcq-cs-009",
        "question_text": "What is the primary role of a Mutex in concurrent programming?",
        "options": [
            "Enable inter-process socket communication",
            "Provide mutual exclusion so only one thread executes a critical section",
            "Compress memory allocated to threads",
            "Schedule thread priority on the CPU"
        ],
        "correct_answer": "Provide mutual exclusion so only one thread executes a critical section",
        "explanation": "A Mutex (mutual exclusion lock) prevents race conditions by allowing only one thread into the protected critical section at a time.",
        "topic": "Operating Systems"
    },
    {
        "id": "mcq-cs-010",
        "question_text": "Which of the following sorting algorithms is stable and guarantees O(n log n) worst-case time?",
        "options": ["HeapSort", "MergeSort", "QuickSort", "SelectionSort"],
        "correct_answer": "MergeSort",
        "explanation": "MergeSort divides the array recursively and merges sorted halves, preserving relative order of equal keys in O(n log n) time.",
        "topic": "Algorithms"
    },
    {
        "id": "mcq-cs-011",
        "question_text": "In Python, which built-in data type is immutable?",
        "options": ["List", "Dictionary", "Tuple", "Set"],
        "correct_answer": "Tuple",
        "explanation": "Tuples in Python cannot be modified (elements cannot be added, removed, or changed) once instantiated.",
        "topic": "Programming (Python)"
    },
    {
        "id": "mcq-cs-012",
        "question_text": "What is the average time complexity of searching for a key in a well-balanced Hash Map?",
        "options": ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
        "correct_answer": "O(1)",
        "explanation": "Given an efficient hash function and low load factor, hash table lookups take constant amortized O(1) time.",
        "topic": "Data Structures"
    },
    {
        "id": "mcq-cs-013",
        "question_text": "In REST architectural principles, which HTTP verb is idempotent and used to update a complete resource representation?",
        "options": ["POST", "PUT", "PATCH", "DELETE"],
        "correct_answer": "PUT",
        "explanation": "PUT replaces the resource state idempotently; repeating the same PUT request produces identical state on the server.",
        "topic": "Web Architecture"
    },
    {
        "id": "mcq-cs-014",
        "question_text": "Which design pattern is used when an object notifies dependent observers automatically of any state changes?",
        "options": ["Singleton", "Observer", "Factory", "Decorator"],
        "correct_answer": "Observer",
        "explanation": "The Observer pattern defines a one-to-many dependency between objects so that when one object changes state, all dependents are notified.",
        "topic": "Software Engineering"
    },
    {
        "id": "mcq-cs-015",
        "question_text": "In virtual memory systems, what is 'Thrashing'?",
        "options": [
            "A fast CPU cache replacement policy",
            "A state where the OS spends more time paging memory to/from disk than executing instructions",
            "High network packet loss over WiFi",
            "A security buffer overflow exploit"
        ],
        "correct_answer": "A state where the OS spends more time paging memory to/from disk than executing instructions",
        "explanation": "Thrashing occurs when active working sets exceed physical RAM, causing constant page faults and disk I/O thrash.",
        "topic": "Operating Systems"
    },
    {
        "id": "mcq-cs-016",
        "question_text": "Which graph traversal algorithm uses a FIFO Queue and finds the shortest path on unweighted graphs?",
        "options": ["Depth-First Search (DFS)", "Breadth-First Search (BFS)", "Bellman-Ford", "Prim's Algorithm"],
        "correct_answer": "Breadth-First Search (BFS)",
        "explanation": "BFS explores neighbors level-by-level using a queue, guaranteeing the shortest hop distance in unweighted graphs.",
        "topic": "Algorithms"
    },
    {
        "id": "mcq-cs-017",
        "question_text": "What is the primary benefit of Redis in modern web backend architectures?",
        "options": [
            "Permanent cold archival storage",
            "In-memory sub-millisecond key-value caching and message brokering",
            "Running complex distributed MapReduce tasks",
            "Static HTML file serving"
        ],
        "correct_answer": "In-memory sub-millisecond key-value caching and message brokering",
        "explanation": "Redis keeps datasets in RAM, providing ultra-low-latency read/write operations for session management and caching.",
        "topic": "System Design"
    },
    {
        "id": "mcq-cs-018",
        "question_text": "In public key cryptography (asymmetric encryption), which key is used to decrypt data encrypted with a user's Public Key?",
        "options": ["User's Private Key", "User's Public Key", "Symmetric Shared Key", "Certificate Authority Key"],
        "correct_answer": "User's Private Key",
        "explanation": "In asymmetric cryptography, data encrypted with the recipient's public key can only be decrypted using the corresponding private key.",
        "topic": "Security"
    },
    {
        "id": "mcq-cs-019",
        "question_text": "What does the CAP theorem state about distributed data stores?",
        "options": [
            "A system can achieve Consistency, Availability, and Partition Tolerance simultaneously",
            "A system can guarantee at most two of: Consistency, Availability, and Partition Tolerance",
            "Concurrency and Performance are inversely proportional",
            "All distributed nodes must share a single global clock"
        ],
        "correct_answer": "A system can guarantee at most two of: Consistency, Availability, and Partition Tolerance",
        "explanation": "Eric Brewer's CAP theorem proves that in the presence of a network partition (P), a distributed system must choose between Consistency (C) and Availability (A).",
        "topic": "Distributed Systems"
    },
    {
        "id": "mcq-cs-020",
        "question_text": "In Docker containerization, what is the role of a Dockerfile?",
        "options": [
            "It configures DNS routing for the physical host",
            "It is a declarative script that specifies the steps to build an immutable container image",
            "It acts as a load balancer between running microservices",
            "It encrypts the host filesystem"
        ],
        "correct_answer": "It is a declarative script that specifies the steps to build an immutable container image",
        "explanation": "A Dockerfile contains instructions (FROM, RUN, COPY, CMD) that Docker reads to assemble a container image.",
        "topic": "DevOps & Cloud"
    },
    {
        "id": "mcq-cs-021",
        "question_text": "What is the time complexity of inserting an element into a binary max-heap of size n?",
        "options": ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
        "correct_answer": "O(log n)",
        "explanation": "Insertion adds the new node at the bottom and bubbles it up along the tree height, which is log2(n).",
        "topic": "Data Structures"
    },
    {
        "id": "mcq-cs-022",
        "question_text": "Which OSI model layer is responsible for logical IP addressing and path routing?",
        "options": ["Data Link Layer", "Network Layer", "Transport Layer", "Session Layer"],
        "correct_answer": "Network Layer",
        "explanation": "Layer 3 (Network Layer) manages IP addressing, packet forwarding, and routing across internetworks.",
        "topic": "Networking"
    },
    {
        "id": "mcq-cs-023",
        "question_text": "In SQL, what is the primary difference between `WHERE` and `HAVING` clauses?",
        "options": [
            "`HAVING` filters rows before grouping, `WHERE` filters groups after `GROUP BY`",
            "`WHERE` filters individual rows before aggregation, `HAVING` filters grouped rows after aggregation",
            "`WHERE` is only for numerical columns, `HAVING` is for text columns",
            "There is no functional difference"
        ],
        "correct_answer": "`WHERE` filters individual rows before aggregation, `HAVING` filters grouped rows after aggregation",
        "explanation": "`WHERE` filters table rows prior to aggregation functions (COUNT, SUM, AVG), whereas `HAVING` applies conditions to grouped aggregate results.",
        "topic": "DBMS"
    },
    {
        "id": "mcq-cs-024",
        "question_text": "What is a Deadlock in operating systems?",
        "options": [
            "A CPU core overheating and shutting down",
            "A situation where two or more processes are permanently blocked because each holds a resource the other needs",
            "An infinite recursive function causing a stack overflow",
            "A network packet loop"
        ],
        "correct_answer": "A situation where two or more processes are permanently blocked because each holds a resource the other needs",
        "explanation": "Deadlock requires Mutual Exclusion, Hold and Wait, No Preemption, and Circular Wait.",
        "topic": "Operating Systems"
    },
    {
        "id": "mcq-cs-025",
        "question_text": "Which HTTP header is used to prevent Cross-Site Scripting (XSS) by restricting where scripts can load from?",
        "options": ["Content-Security-Policy", "Access-Control-Allow-Origin", "Cache-Control", "X-Frame-Options"],
        "correct_answer": "Content-Security-Policy",
        "explanation": "Content-Security-Policy (CSP) instructs the browser which domains are authorized sources of executable scripts, stylesheets, and images.",
        "topic": "Security"
    }
]


class MCQService:
    """
    Manages MCQ question storage, session randomization, proctored strike detection,
    and automated grading.
    """
    def __init__(self):
        DB_DIR.mkdir(parents=True, exist_ok=True)
        self.init_database()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Initializes tables for MCQ questions, candidate test sessions, and results."""
        conn = self._get_conn()
        c = conn.cursor()

        c.execute("""
            CREATE TABLE IF NOT EXISTS mcq_questions (
                id TEXT PRIMARY KEY,
                question_text TEXT NOT NULL,
                options_json TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                explanation TEXT DEFAULT '',
                topic TEXT DEFAULT 'Computer Science / IT',
                source TEXT DEFAULT 'Staff Upload',
                upload_batch_id TEXT DEFAULT 'seed-batch',
                upload_time TEXT DEFAULT '',
                is_approved INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Migration: ensure new columns exist if table was already created
        try:
            c.execute("ALTER TABLE mcq_questions ADD COLUMN upload_batch_id TEXT DEFAULT 'seed-batch'")
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE mcq_questions ADD COLUMN upload_time TEXT DEFAULT ''")
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE mcq_questions ADD COLUMN is_approved INTEGER DEFAULT 0")
        except Exception:
            pass

        c.execute("""
            CREATE TABLE IF NOT EXISTS mcq_sessions (
                session_id TEXT PRIMARY KEY,
                student_id TEXT NOT NULL,
                student_name TEXT NOT NULL,
                status TEXT DEFAULT 'in_progress', -- 'in_progress', 'completed', 'disqualified'
                strikes INTEGER DEFAULT 0,
                question_ids_json TEXT NOT NULL,
                shuffled_questions_json TEXT NOT NULL,
                answers_json TEXT DEFAULT '{}',
                score REAL DEFAULT 0.0,
                total_questions INTEGER DEFAULT 20,
                percentage REAL DEFAULT 0.0,
                passed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)

        conn.commit()

        # Seed initial questions if table has fewer than 20 items
        c.execute("SELECT COUNT(*) AS cnt FROM mcq_questions")
        row = c.fetchone()
        if not row or row["cnt"] < 20:
            self._seed_default_questions(conn)

        # Ensure seed questions are approved by default so testing works immediately
        c.execute("UPDATE mcq_questions SET is_approved = 1 WHERE upload_batch_id = 'seed-batch'")
        conn.commit()
        conn.close()

    def _seed_default_questions(self, conn: sqlite3.Connection):
        """Seeds default bank with 25 curated questions marked as approved."""
        c = conn.cursor()
        now_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        for q in DEFAULT_SEED_MCQS:
            c.execute("""
                INSERT OR IGNORE INTO mcq_questions (id, question_text, options_json, correct_answer, explanation, topic, source, upload_batch_id, upload_time, is_approved)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                q["id"],
                q["question_text"],
                json.dumps(q["options"]),
                q["correct_answer"],
                q["explanation"],
                q["topic"],
                "Axon Institutional Repository",
                "seed-batch",
                now_time,
                1
            ))
        conn.commit()

    def bulk_insert_mcqs(self, records: List[Dict[str, Any]], batch_filename: str = "Upload") -> Dict[str, Any]:
        """
        Bulk inserts parsed MCQs into the database grouped by an upload batch.
        Assigns an upload timestamp and batch id. Newly uploaded questions default to
        is_approved = 0 so Staff/HOD can verify them before exams.
        """
        conn = self._get_conn()
        c = conn.cursor()
        inserted_count = 0
        batch_id = f"batch-{uuid.uuid4().hex[:8]}"
        batch_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        for r in records:
            qid = r.get("id") or f"mcq-{uuid.uuid4().hex[:8]}"
            q_text = r.get("question_text", "").strip()
            options = r.get("options", [])
            if not q_text or len(options) < 2:
                continue

            ans = r.get("correct_answer", "").strip()
            if not ans:
                ans = self.resolve_missing_answer(q_text, options)

            explanation = r.get("explanation", "").strip() or f"Correct answer is: {ans}"
            topic = r.get("topic", "General IT / Computer Science").strip()
            source = f"{batch_filename} ({batch_time})"

            c.execute("""
                INSERT OR REPLACE INTO mcq_questions (id, question_text, options_json, correct_answer, explanation, topic, source, upload_batch_id, upload_time, is_approved)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                qid,
                q_text,
                json.dumps(options),
                ans,
                explanation,
                topic,
                source,
                batch_id,
                batch_time,
                0
            ))
            inserted_count += 1

        conn.commit()
        conn.close()
        return {
            "inserted_count": inserted_count,
            "batch_id": batch_id,
            "upload_time": batch_time
        }

    def get_all_questions(self, batch_id: Optional[str] = None, approval_status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Returns all questions with options and approval status for Staff & HOD management.
        """
        conn = self._get_conn()
        c = conn.cursor()

        query = "SELECT id, question_text, options_json, correct_answer, explanation, topic, source, upload_batch_id, upload_time, is_approved, created_at FROM mcq_questions WHERE 1=1"
        params = []

        if batch_id and batch_id != "all":
            query += " AND upload_batch_id = ?"
            params.append(batch_id)

        if approval_status == "approved":
            query += " AND is_approved = 1"
        elif approval_status == "pending":
            query += " AND is_approved = 0"

        query += " ORDER BY created_at DESC"
        c.execute(query, params)
        rows = c.fetchall()
        conn.close()

        results = []
        for r in rows:
            results.append({
                "id": r["id"],
                "question_text": r["question_text"],
                "options": json.loads(r["options_json"]),
                "correct_answer": r["correct_answer"],
                "explanation": r["explanation"],
                "topic": r["topic"],
                "source": r["source"],
                "upload_batch_id": r["upload_batch_id"],
                "upload_time": r["upload_time"],
                "is_approved": bool(r["is_approved"]),
                "created_at": r["created_at"]
            })
        return results

    def get_upload_batches(self) -> List[Dict[str, Any]]:
        """
        Returns distinct upload batches with timestamps, total questions, and approved count.
        """
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT upload_batch_id, source, upload_time,
                   COUNT(*) as total_questions,
                   SUM(CASE WHEN is_approved = 1 THEN 1 ELSE 0 END) as approved_count
            FROM mcq_questions
            GROUP BY upload_batch_id
            ORDER BY upload_time DESC
        """)
        rows = c.fetchall()
        conn.close()

        batches = []
        for r in rows:
            batches.append({
                "batch_id": r["upload_batch_id"] or "seed-batch",
                "source": r["source"] or "Default Question Bank",
                "upload_time": r["upload_time"] or "System Seed",
                "total_questions": r["total_questions"],
                "approved_count": r["approved_count"] or 0
            })
        return batches

    def update_question(
        self,
        question_id: str,
        question_text: str,
        options: List[str],
        correct_answer: str,
        explanation: str = "",
        topic: str = "General IT / Computer Science",
        is_approved: bool = True
    ) -> Dict[str, Any]:
        """
        Updates an existing MCQ question, its options, answer, and approval status.
        """
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("SELECT id FROM mcq_questions WHERE id = ?", (question_id,))
        if not c.fetchone():
            conn.close()
            raise HTTPException(status_code=404, detail=f"Question '{question_id}' not found.")

        c.execute("""
            UPDATE mcq_questions
            SET question_text = ?,
                options_json = ?,
                correct_answer = ?,
                explanation = ?,
                topic = ?,
                is_approved = ?
            WHERE id = ?
        """, (
            question_text.strip(),
            json.dumps(options),
            correct_answer.strip(),
            explanation.strip(),
            topic.strip(),
            1 if is_approved else 0,
            question_id
        ))
        conn.commit()
        conn.close()

        return {
            "id": question_id,
            "question_text": question_text,
            "options": options,
            "correct_answer": correct_answer,
            "explanation": explanation,
            "topic": topic,
            "is_approved": is_approved
        }

    def toggle_question_approval(self, question_id: str, is_approved: bool) -> Dict[str, Any]:
        """
        Toggles the verified/approved status of a question.
        """
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("SELECT id FROM mcq_questions WHERE id = ?", (question_id,))
        if not c.fetchone():
            conn.close()
            raise HTTPException(status_code=404, detail=f"Question '{question_id}' not found.")

        c.execute("UPDATE mcq_questions SET is_approved = ? WHERE id = ?", (1 if is_approved else 0, question_id))
        conn.commit()
        conn.close()
        return {"id": question_id, "is_approved": is_approved}

    def delete_question(self, question_id: str) -> bool:
        """Deletes an individual MCQ question."""
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("DELETE FROM mcq_questions WHERE id = ?", (question_id,))
        deleted = c.rowcount > 0
        conn.commit()
        conn.close()
        return deleted

    def delete_batch(self, batch_id: str) -> int:
        """Deletes all questions belonging to a specific upload batch."""
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("DELETE FROM mcq_questions WHERE upload_batch_id = ?", (batch_id,))
        deleted_count = c.rowcount
        conn.commit()
        conn.close()
        return deleted_count

    def resolve_missing_answer(self, question_text: str, options: List[str]) -> str:
        """
        Fetches answer from external endpoint (https://api.greeksforgeeks.com/answers).
        Gracefully falls back to local knowledge base / options if unavailable.
        """
        try:
            with httpx.Client(timeout=2.0) as client:
                res = client.post(
                    EXTERNAL_ANSWER_ENDPOINT,
                    json={"question": question_text, "options": options}
                )
                if res.status_code == 200:
                    data = res.json()
                    if "answer" in data and data["answer"] in options:
                        return data["answer"]
        except Exception:
            # Fallback to local heuristic / seed match
            pass

        # Try match against existing seed question keywords
        lower_q = question_text.lower()
        for seed in DEFAULT_SEED_MCQS:
            if seed["topic"].lower() in lower_q or any(w in lower_q for w in seed["question_text"].lower().split() if len(w) > 5):
                for opt in options:
                    if opt.lower() == seed["correct_answer"].lower():
                        return opt

        # Default fallback to first option
        return options[0] if options else "A"

    def get_total_questions_count(self) -> int:
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) AS cnt FROM mcq_questions")
        row = c.fetchone()
        conn.close()
        return row["cnt"] if row else 0

    def get_approved_questions_count(self) -> int:
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) AS cnt FROM mcq_questions WHERE is_approved = 1")
        row = c.fetchone()
        conn.close()
        return row["cnt"] if row else 0

    def create_shuffled_session(self, student_id: str, student_name: str, count: int = 20) -> Dict[str, Any]:
        """
        Serves exactly 20 randomized questions per session from the VERIFIED & APPROVED questions pool.
        Randomizes question selection and option order student-by-student.
        Initializes strike counter to 0.
        """
        conn = self._get_conn()
        c = conn.cursor()

        # Query only approved questions
        c.execute("SELECT id, question_text, options_json, correct_answer, explanation, topic FROM mcq_questions WHERE is_approved = 1")
        all_rows = c.fetchall()

        if len(all_rows) < count:
            # If approved pool is below 20, seed default approved questions
            self._seed_default_questions(conn)
            c.execute("UPDATE mcq_questions SET is_approved = 1 WHERE upload_batch_id = 'seed-batch'")
            conn.commit()
            c.execute("SELECT id, question_text, options_json, correct_answer, explanation, topic FROM mcq_questions WHERE is_approved = 1")
            all_rows = c.fetchall()

        # Select exactly 'count' questions at random
        sample_pool = random.sample(all_rows, min(count, len(all_rows)))

        session_id = f"mcq-sess-{uuid.uuid4().hex[:10]}"
        question_ids = []
        client_questions = []
        server_secret_questions = []

        for row in sample_pool:
            qid = row["id"]
            question_ids.append(qid)
            raw_options = json.loads(row["options_json"])

            # Shuffle options for this specific student
            shuffled_options = list(raw_options)
            random.shuffle(shuffled_options)

            # Map options to letters A, B, C, D
            option_letters = ["A", "B", "C", "D", "E"][:len(shuffled_options)]
            formatted_choices = [
                {"label": letter, "text": text}
                for letter, text in zip(option_letters, shuffled_options)
            ]

            client_questions.append({
                "id": qid,
                "question": row["question_text"],
                "choices": formatted_choices,
                "topic": row["topic"]
            })

            server_secret_questions.append({
                "id": qid,
                "question_text": row["question_text"],
                "choices": formatted_choices,
                "correct_answer": row["correct_answer"],
                "explanation": row["explanation"]
            })

        c.execute("""
            INSERT INTO mcq_sessions (
                session_id, student_id, student_name, status, strikes,
                question_ids_json, shuffled_questions_json, total_questions
            ) VALUES (?, ?, ?, 'in_progress', 0, ?, ?, ?)
        """, (
            session_id,
            student_id,
            student_name,
            json.dumps(question_ids),
            json.dumps(server_secret_questions),
            len(client_questions)
        ))

        conn.commit()
        conn.close()

        return {
            "session_id": session_id,
            "student_id": student_id,
            "student_name": student_name,
            "status": "in_progress",
            "strikes": 0,
            "total_questions": len(client_questions),
            "questions": client_questions
        }

    def record_strike(self, session_id: str) -> Dict[str, Any]:
        """
        Records a focus loss / cursor out-of-focus violation.
        Disqualifies candidate when strikes reach 3.
        """
        conn = self._get_conn()
        c = conn.cursor()

        c.execute("SELECT session_id, student_id, strikes, status FROM mcq_sessions WHERE session_id = ?", (session_id,))
        row = c.fetchone()
        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail="MCQ Session not found")

        current_strikes = row["strikes"] + 1
        new_status = row["status"]
        is_disqualified = False

        if current_strikes >= 3:
            new_status = "disqualified"
            is_disqualified = True

        c.execute("""
            UPDATE mcq_sessions
            SET strikes = ?, status = ?
            WHERE session_id = ?
        """, (current_strikes, new_status, session_id))

        conn.commit()
        conn.close()

        msg = (
            "Proctoring alert: 3 strikes exceeded! You have been disqualified from this assessment."
            if is_disqualified else
            f"Proctoring warning: Window focus lost. Strike {current_strikes} of 3."
        )

        return {
            "session_id": session_id,
            "strikes": current_strikes,
            "is_disqualified": is_disqualified,
            "status": new_status,
            "message": msg
        }

    def submit_answers(self, session_id: str, student_answers: Dict[str, str]) -> Dict[str, Any]:
        """
        Submits candidate answers and computes score.
        Blocks submission if the candidate has 3 strikes.
        """
        conn = self._get_conn()
        c = conn.cursor()

        c.execute("""
            SELECT session_id, student_id, student_name, status, strikes,
                   shuffled_questions_json, total_questions
            FROM mcq_sessions WHERE session_id = ?
        """, (session_id,))
        row = c.fetchone()

        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail="MCQ Session not found")

        if row["strikes"] >= 3 or row["status"] == "disqualified":
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Assessment disqualified due to 3 proctoring strikes. Submission rejected. You must restart the assessment from Question 1."
            )

        secret_questions = json.loads(row["shuffled_questions_json"])
        correct_count = 0
        breakdown = []

        for q in secret_questions:
            qid = q["id"]
            selected_val = student_answers.get(qid, "").strip()
            correct_ans = q["correct_answer"].strip()

            # Determine whether student answer matches text or label
            is_correct = False
            selected_text = ""

            for choice in q["choices"]:
                if selected_val in [choice["label"], choice["text"]]:
                    selected_text = choice["text"]
                    if (choice["text"].lower() == correct_ans.lower() or
                            choice["label"].lower() == correct_ans.lower()):
                        is_correct = True
                        break

            # Direct string comparison fallback
            if not is_correct and selected_val.lower() == correct_ans.lower():
                is_correct = True
                selected_text = selected_val

            if is_correct:
                correct_count += 1

            breakdown.append({
                "question_id": qid,
                "question_text": q["question_text"],
                "selected_answer": selected_text or selected_val or "(No answer)",
                "correct_answer": correct_ans,
                "is_correct": is_correct,
                "explanation": q.get("explanation", "")
            })

        total_q = len(secret_questions)
        pct = round((correct_count / total_q) * 100, 1) if total_q > 0 else 0.0
        passed = 1 if pct >= 60.0 else 0
        now_iso = datetime.now(timezone.utc).isoformat()

        c.execute("""
            UPDATE mcq_sessions
            SET status = 'completed',
                answers_json = ?,
                score = ?,
                percentage = ?,
                passed = ?,
                completed_at = ?
            WHERE session_id = ?
        """, (
            json.dumps(student_answers),
            correct_count,
            pct,
            passed,
            now_iso,
            session_id
        ))

        conn.commit()
        conn.close()

        return {
            "session_id": session_id,
            "student_id": row["student_id"],
            "student_name": row["student_name"],
            "status": "completed",
            "score": correct_count,
            "total_questions": total_q,
            "percentage": pct,
            "passed": bool(passed),
            "strikes": row["strikes"],
            "completed_at": now_iso,
            "breakdown": breakdown
        }

    def get_student_results(self, student_id: str) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT session_id, student_id, student_name, status, strikes,
                   score, total_questions, percentage, passed, created_at, completed_at
            FROM mcq_sessions
            WHERE student_id = ? AND status = 'completed'
            ORDER BY completed_at DESC
        """, (student_id,))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_all_results(self) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT session_id, student_id, student_name, status, strikes,
                   score, total_questions, percentage, passed, created_at, completed_at
            FROM mcq_sessions
            ORDER BY created_at DESC
        """)
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]


mcq_service = MCQService()
