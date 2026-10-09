# Axon MCQ Assessment & Proctored Examination Engine

## 1. Overview
Axon provides a proctored, randomized Multiple Choice Question (MCQ) assessment framework alongside bulk roster uploading and directory hygiene tools. This replaces the legacy conversational Graded Mode.

---

## 2. MCQ Assessment Workflow

1. **Question Pool & Randomization**:
   - Every candidate session starts by pulling **20 randomized questions** from the local SQLite question bank (`data/question_bank.db`).
   - The order of options (A, B, C, D) is independently shuffled for every candidate to prevent screen sharing or side-by-side cheating.
   
2. **Proctored Anti-Cheat Controls**:
   - `window.onblur`, `document.onvisibilitychange`, and cursor departure triggers record strikes in real-time.
   - **Strike 1 & 2**: Candidate receives warning banners indicating remaining strikes.
   - **Strike 3**: The session is immediately flagged as `disqualified`. Submission is permanently locked, and the candidate must restart the test from the beginning.

3. **Instant Evaluation & Breakdown**:
   - Scores, percentages, and question-by-question explanations are displayed immediately upon submission.
   - Faculty and HOD can inspect candidate attempts, pass/fail metrics, scores, and strike histories from the **MCQ Results** directory tab.

---

## 3. API Contract

| Method | Endpoint | Role | Description |
|---|---|---|---|
| `POST` | `/mcq/upload` | `staff`, `hod` | Uploads question banks in Excel (`.xlsx`, `.xls`, `.csv`) or PDF formats (max 50 MiB). |
| `POST` | `/mcq/session/start` | `student`, `staff`, `hod` | Generates a 20-question randomized session with strike counters set to 0. |
| `POST` | `/mcq/session/{id}/strike` | `student` | Logs a proctoring violation. Flags disqualification when `strikes >= 3`. |
| `POST` | `/mcq/session/{id}/submit` | `student` | Grades answers. Throws HTTP 403 if disqualified. |
| `GET` | `/mcq/results/all` | `staff`, `hod` | Lists all candidate submissions with scores, strike counts, and dates. |
| `GET` | `/mcq/results/my` | `student` | Returns the student's historical attempts and scorecards. |
| `GET` | `/mcq/questions/count` | `student`, `staff`, `hod` | Returns total questions available in the question bank pool. |
| `POST` | `/auth/students/bulk-upload` | `staff`, `hod` | Bulk registers students from PDF or Excel files (max 50 MiB, max 300 records). |
| `POST` | `/auth/students/cleanup` | `hod` | Purges dummy/sample accounts, retaining exclusively student `11234003`. |

---

## 4. Bulk Upload Formats

### A. MCQ Question Bank
- **Excel (`.xlsx`, `.xls`, `.csv`)**:
  - Expected Columns: `question`, `option_a`, `option_b`, `option_c`, `option_d`, `answer` (optional), `topic` (optional), `explanation` (optional).
  - If `answer` is omitted or empty, Axon automatically looks up the answer from `https://api.greeksforgeeks.com/answers` or uses local heuristics.
- **PDF**:
  - Formatted with question numbers followed by options:
    ```
    1. What is the time complexity of binary search?
    A) O(n)
    B) O(log n)
    C) O(n^2)
    D) O(1)
    Answer: B
    ```

### B. Student Bulk Roster
- **Excel / PDF**:
  - Columns: `name`, `roll_number`, `dept` (or `department`), `password`.
  - Max upload size: 50 MiB (enforces HTTP 413 Payload Too Large if exceeded).
  - Capped at 300 records per upload batch.

---

## 5. Standardized Error Handling
All API endpoints return JSON conforming to:
```json
{
  "detail": "Descriptive message",
  "error": "Descriptive message",
  "status_code": 400
}
```
The frontend API client checks both `error` and `detail` properties, surfacing notifications seamlessly to users.
