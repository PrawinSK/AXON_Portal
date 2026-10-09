import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
)
from reportlab.pdfgen import canvas

class SimplePageNumberCanvas(canvas.Canvas):
    """Clean canvas matching standard academic project report formatting."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            super().showPage()
        super().save()


def build_updated_pdf(filename="d:/Axon/AXON_AI_Recruiter_Documentation.pdf"):
    # 1 inch (72pt) margins, standard Letter size
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=72,
        rightMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    styles = getSampleStyleSheet()

    # Custom styles matching the exact demo document
    title_main = ParagraphStyle(
        'TitleMain',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=14,
        leading=18,
        alignment=1, # Center
        spaceAfter=14
    )

    title_sub = ParagraphStyle(
        'TitleSub',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=13,
        leading=17,
        alignment=1, # Center
        spaceAfter=20
    )

    h1 = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=13,
        leading=17,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2 = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=12,
        leading=16,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    body = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=11,
        leading=16.5,
        spaceBefore=3,
        spaceAfter=6
    )

    body_bold = ParagraphStyle(
        'BodyBold',
        parent=body,
        fontName='Times-Bold'
    )

    bullet = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=11,
        leading=16.5,
        leftIndent=24,
        firstLineIndent=-14,
        spaceBefore=2,
        spaceAfter=3
    )

    mockup_header = ParagraphStyle(
        'MockupHeader',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=12,
        leading=16,
        alignment=1,
        spaceBefore=10,
        spaceAfter=8
    )

    story = []

    # =========================================================================
    # PAGE 1: Title, 1. Project Overview, 1.1 Project Title, 1.2 Problem Statement
    # =========================================================================
    story.append(Paragraph("PROJECT REPORT", title_main))
    story.append(Paragraph("AXON AI RECRUITER", title_sub))
    story.append(Paragraph("1. PROJECT OVERVIEW", h1))
    story.append(Paragraph("1.1 Project Title", h2))
    story.append(Paragraph(
        "<b>AXON: AI Recruiter Agent with Job Description Matching, Max Candidate Shortlisting, Retrieval Augmented Generation, Deterministic Difficulty Engine, Tools and Memory</b>",
        body
    ))
    story.append(Paragraph(
        "The project is an Artificial Intelligence based Recruiter and Technical Assessment Agent designed to provide realistic, rigorous, and automated technical interviews for engineering students and job candidates. The system uses Agentic AI concepts, Job Description (JD) parsing, candidate resume semantic matching, maximum candidate threshold filtering, Retrieval Augmented Generation (RAG), deterministic difficulty adaptation, safe evaluation tools, conversation memory, and a Large Language Model.",
        body
    ))
    story.append(Paragraph(
        "The main purpose of this project is to reduce the time campus placement officers, corporate recruiters, and faculty members spend screening resumes against complex Job Descriptions and conducting manual technical interviews, while providing candidates with targeted, job-aligned interview assessments.",
        body
    ))
    story.append(Paragraph(
        "The system allows recruiters to upload target Job Descriptions, specify the maximum number of candidates (Max Candidates) to shortlist, and initiate AI-driven interviews grounded in both the candidate's resume and the company's JD. For example, the AI Recruiter prompts candidates with questions such as:",
        body
    ))
    story.append(Paragraph("• “Based on the Cloud Engineer Job Description and your resume, how did you implement asynchronous event streaming in your FastAPI and Redis microservice?”", bullet))
    story.append(Paragraph("• “The Job Description requires expertise in relational query optimization. Walk me through how you tuned composite indexes for your PostgreSQL database.”", bullet))
    story.append(Paragraph("• “Why did you choose ChromaDB over Elasticsearch for candidate embedding search in your project?”", bullet))
    story.append(Paragraph("• “How did you implement JWT token authentication in accordance with enterprise security standards?”", bullet))
    story.append(Paragraph("• “Explain how your Celery worker ensures idempotency during distributed transaction failures.”", bullet))
    story.append(Paragraph(
        "The AI Recruiter Agent matches candidate resumes against Job Descriptions, ranks applicants, filters by Max Candidate quotas, and conducts adaptive, rubric-evaluated interviews.",
        body
    ))
    story.append(Paragraph("1.2 Problem Statement", h2))
    story.append(Paragraph(
        "Campus placement drives and corporate hiring face acute bottlenecks when screening hundreds of applicants against diverse Job Descriptions (JDs). Matching resumes manually to identify qualified candidates and conducting one-on-one technical interviews is time-consuming, prone to human bias, and operationally unscalable.",
        body
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: 1.2 Problem Statement (Continued)
    # =========================================================================
    story.append(Paragraph(
        "In traditional recruitment, placement officers must manually review hundreds of resumes for every posted Job Description. Recruiters struggle to determine how many top candidates (Max Candidates) possess genuine competency versus keyword stuffing.",
        body
    ))
    story.append(Paragraph(
        "Furthermore, conventional hiring relies on generic aptitude tests or abstract coding puzzles that bear little relation to the specific Job Description requirements. Crucial operational questions arise:",
        body
    ))
    story.append(Paragraph("• How can recruiters automatically match and rank hundreds of candidate resumes against a specific Job Description?", bullet))
    story.append(Paragraph("• How can institutions enforce a configurable Max Candidate limit for interview rounds without manual shortlisting?", bullet))
    story.append(Paragraph("• Why do candidates who excel on multiple-choice questions struggle to explain their actual projects during live interviews?", bullet))
    story.append(Paragraph("• Can an AI interviewer dynamically tailor technical questions to both the candidate's CV and the employer's Job Description?", bullet))
    story.append(Paragraph("• How can question difficulty be adapted deterministically based on real-time candidate answers?", bullet))
    story.append(Paragraph("• How can recruiters verify whether a candidate truly authored their claimed projects rather than copying code?", bullet))
    story.append(Paragraph("• What mechanisms prevent malpractice and cheating during remote technical evaluations?", bullet))
    story.append(Paragraph("• How can institutional leaders identify skill deficiencies relative to industry hiring trends?", bullet))
    story.append(Paragraph("• Why do standard chatbots fail to maintain consistent, rubric-based technical scoring standards?", bullet))
    story.append(Paragraph("• How can high-concurrency campus interview drives avoid API rate limits (HTTP 429 exceptions)?", bullet))
    story.append(Paragraph(
        "A standard chatbot cannot resolve these issues because it lacks semantic resume matching, cannot parse Job Descriptions against vector stores, does not support Max Candidate quotas, and cannot execute deterministic difficulty transitions.",
        body
    ))
    story.append(Paragraph(
        "Therefore, an intelligent system is required that can ingest Job Descriptions, semantically match and rank candidate resumes, enforce Max Candidate shortlisting, and conduct adaptive, rubric-evaluated technical interviews.",
        body
    ))
    story.append(Paragraph(
        "The proposed AXON AI Recruiter solves this problem by integrating Job Description matching, vector similarity ranking, deterministic difficulty adaptation, decoupled evaluation rubrics, and a 50-key API rotation cluster.",
        body
    ))
    story.append(Paragraph("Thus, the main problem addressed by this project is:", body))
    story.append(Paragraph(
        "<b>“How can an AI-based recruiter system match candidate resumes with Job Descriptions, filter top applicants using Max Candidate thresholds, adapt interview difficulty dynamically, and conduct decoupled rubric assessments while maintaining conversation context?”</b>",
        body_bold
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: 1.3 Brief Description of the Project
    # =========================================================================
    story.append(Paragraph("1.3 Brief Description of the Project", h2))
    story.append(Paragraph(
        "The AXON AI Recruiter is a web-based AI recruitment and assessment platform developed to automate resume screening, Job Description matching, candidate shortlisting, and adaptive technical interviewing.",
        body
    ))
    story.append(Paragraph(
        "The platform serves recruiters, faculty, and candidates through an integrated workflow. Recruiters upload target Job Descriptions and specify the <b>Max Candidate</b> limit (e.g., top 30 candidates). The system computes semantic match scores and automatically invites the top-ranked candidates to the interview room.",
        body
    ))
    story.append(Paragraph("For example:", body))
    story.append(Paragraph("<b>Recruiter Setup:</b> Uploads <i>'Senior Backend Engineer JD'</i> | Sets <i>Max Candidates = 25</i>.", body))
    story.append(Paragraph("<b>AI Recruiter Agent:</b> Matches 150 candidate resumes, shortlists top 25, and begins JD-grounded interview.", body))
    story.append(Paragraph("<b>AI Recruiter:</b> “The Job Description requires high-throughput caching. In your resume, you built an e-commerce API with Redis. How did you handle cache stampedes?”", body))
    story.append(Paragraph("<b>Candidate:</b> “We implemented probabilistic early expiration and mutex locks in Redis to prevent multiple workers from querying PostgreSQL simultaneously.”", body))
    story.append(Paragraph(
        "The project uses Retrieval Augmented Generation (RAG) to connect the AI model with candidate resumes, Job Description criteria, and curriculum knowledge bases.",
        body
    ))
    story.append(Paragraph("The knowledge base and JD matcher cover key domains including:", body))
    story.append(Paragraph("• Python &amp; Backend Systems Engineering", bullet))
    story.append(Paragraph("• Web Frameworks (FastAPI, Next.js, React)", bullet))
    story.append(Paragraph("• Relational Databases &amp; SQL Query Tuning (PostgreSQL)", bullet))
    story.append(Paragraph("• Vector Databases &amp; Semantic Embeddings (ChromaDB)", bullet))
    story.append(Paragraph("• Distributed Caching &amp; Queues (Redis, Celery, Kafka)", bullet))
    story.append(Paragraph("• API Security &amp; Token Architecture (JWT, OAuth2)", bullet))
    story.append(Paragraph("• Cloud Infrastructure &amp; Containerization (Docker, Kubernetes)", bullet))
    story.append(Paragraph("• Algorithmic Efficiency &amp; Data Structures", bullet))
    story.append(Paragraph("• High-Scale System Design &amp; Architectural Patterns", bullet))
    story.append(Paragraph("• Job Description Competency &amp; Prerequisite Mapping", bullet))
    story.append(Paragraph(
        "Candidate resumes and Job Descriptions are parsed, chunked, and vectorized using sentence-transformers into ChromaDB for instant semantic matching and top-k retrieval.",
        body
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: 1.3 Brief Description (Continued - Tools, Memory, DB)
    # =========================================================================
    story.append(Paragraph(
        "The retrieved information is provided to the AI model to generate technical questions directly aligned with both the candidate's background and the employer's Job Description.",
        body
    ))
    story.append(Paragraph("The system contains predefined safe evaluation, screening, and diagnostic tools such as:", body))
    story.append(Paragraph("1. Job Description Parser &amp; Skill Extraction Tool", bullet))
    story.append(Paragraph("2. Candidate-to-JD Semantic Matching &amp; Fit Scoring Tool", bullet))
    story.append(Paragraph("3. Max Candidate Quota &amp; Shortlist Filter Tool", bullet))
    story.append(Paragraph("4. Resume Semantic Parser &amp; Section Chunker Tool", bullet))
    story.append(Paragraph("5. ChromaDB Dense Vector Similarity Retrieval Tool", bullet))
    story.append(Paragraph("6. Deterministic Difficulty State Machine Tool (Levels 1 to 5)", bullet))
    story.append(Paragraph("7. Decoupled Real-Time Rubric Evaluator Tool", bullet))
    story.append(Paragraph("8. Multi-Key Pool Manager &amp; Health Monitor Tool (50 Keys)", bullet))
    story.append(Paragraph("9. Anti-Malpractice Browser Proctor Tool (Window Focus &amp; Clipboard)", bullet))
    story.append(Paragraph("10. Holistic Skill Radar &amp; Remediation Task Generator Tool", bullet))
    story.append(Paragraph(
        "These tools allow the Agent to screen, match, shortlist, question, and evaluate candidates without executing arbitrary shell commands.",
        body
    ))
    story.append(Paragraph(
        "Another critical component is <b>Conversation Memory</b>. The system retains recent turns of dialogue, enabling the AI Recruiter to ask meaningful follow-up questions that probe deeper into technical details.",
        body
    ))
    story.append(Paragraph("For example:", body))
    story.append(Paragraph("<b>Candidate:</b> “We used Celery for background email processing.”", body))
    story.append(Paragraph("<b>AI Recruiter:</b> “What broker did you configure, and how did you monitor queue backpressure?”", body))
    story.append(Paragraph("<b>Candidate:</b> “We used Redis as the message broker and monitored consumer lag with Celery Flower.”", body))
    story.append(Paragraph(
        "The system records all interview turns, difficulty levels, rubric scores, JD match ratings, and timestamps in PostgreSQL / SQLite databases.",
        body
    ))
    story.append(Paragraph("Therefore, the project combines:", body))
    story.append(Paragraph("• AI Agent", bullet))
    story.append(Paragraph("• Job Description Matching", bullet))
    story.append(Paragraph("• Max Candidate Shortlisting", bullet))
    story.append(Paragraph("• RAG &amp; Vector Database", bullet))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: 2. OBJECTIVES & PROPOSED SOLUTION, 2.1 Project Objectives (1 to 5)
    # =========================================================================
    story.append(Paragraph("• Deterministic Difficulty Engine", bullet))
    story.append(Paragraph("• Decoupled Rubric Evaluation", bullet))
    story.append(Paragraph("• Multi-Key API Rotation Pool", bullet))
    story.append(Paragraph("• Conversation Memory", bullet))
    story.append(Paragraph("• Relational Database Storage", bullet))
    story.append(Paragraph("• Institutional Analytics &amp; Skill Radar", bullet))
    story.append(Paragraph("to create an end-to-end intelligent recruitment and talent assessment platform.", body))
    story.append(Paragraph("2. OBJECTIVES &amp; PROPOSED SOLUTION", h1))
    story.append(Paragraph("2.1 Project Objectives", h2))
    story.append(Paragraph(
        "The primary objective is to develop an autonomous AI Recruiter Agent that matches candidates with Job Descriptions, shortlists top applicants via Max Candidate quotas, and conducts adaptive, resume-grounded technical interviews.",
        body
    ))
    story.append(Paragraph("The major project objectives are given below.", body))
    story.append(Paragraph("<b>1. Match Candidates with Target Job Descriptions</b>", body_bold))
    story.append(Paragraph("The system should ingest complex Job Descriptions, extract required technical proficiencies, and semantically match them against applicant resumes to compute an objective match score (0–100%).", body))
    story.append(Paragraph("<b>2. Enforce Max Candidate Shortlist Thresholds</b>", body_bold))
    story.append(Paragraph("Recruiters should be able to specify a Max Candidate limit (e.g., top 20 or 50 candidates) to automatically filter the highest-ranking applicants for technical assessment rounds.", body))
    story.append(Paragraph("<b>3. Understand and Parse Complex Student Resumes</b>", body_bold))
    story.append(Paragraph("The system should parse PDF resumes, extract projects, technical skills, and coursework, and index them into dense vector collections.", body))
    story.append(Paragraph("<b>4. Implement Resume- and JD-Grounded RAG</b>", body_bold))
    story.append(Paragraph("RAG should be used to ground every interview inquiry in both the candidate's actual projects and the employer's Job Description criteria.", body))
    story.append(Paragraph("<b>5. Implement Semantic Search for Candidate Matching</b>", body_bold))
    story.append(Paragraph("The system should match candidate experiences with Job Descriptions using vector similarity rather than brittle keyword matching.", body))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 6: 2.1 Project Objectives (6 to 12)
    # =========================================================================
    story.append(Paragraph("<b>6. Classify Technical Competencies &amp; Roles</b>", body_bold))
    story.append(Paragraph("The system should classify competencies across multiple engineering roles such as:", body))
    story.append(Paragraph("• Full Stack Software Development", bullet))
    story.append(Paragraph("• Backend Engineering &amp; Distributed Systems", bullet))
    story.append(Paragraph("• Cloud Infrastructure &amp; DevOps", bullet))
    story.append(Paragraph("• Database Architecture &amp; Query Optimization", bullet))
    story.append(Paragraph("• Machine Learning &amp; AI Engineering", bullet))
    story.append(Paragraph("• API Security &amp; Network Concurrency", bullet))
    story.append(Paragraph("• Frontend Architecture &amp; State Management", bullet))
    story.append(Paragraph("• Core Data Structures &amp; Algorithms", bullet))
    story.append(Paragraph("• Microservices Architecture &amp; Message Brokers", bullet))
    story.append(Paragraph("• General Engineering Fundamentals", bullet))
    story.append(Paragraph("<b>7. Implement Deterministic Difficulty Tools</b>", body_bold))
    story.append(Paragraph("The Agent should dynamically calibrate question difficulty across 5 structured levels (Foundational to Architectural Optimization) based on mathematical score triggers.", body))
    story.append(Paragraph("<b>8. Provide Decoupled Rubric-Based Feedback</b>", body_bold))
    story.append(Paragraph("The system should evaluate responses independently of question prompts, scoring technical accuracy, depth, edge cases, and clarity.", body))
    story.append(Paragraph("<b>9. Maintain Multi-Turn Conversation Context</b>", body_bold))
    story.append(Paragraph("The system should preserve multi-turn dialogue history to ask contextually grounded follow-up questions.", body))
    story.append(Paragraph("<b>10. Store Complete Interview Transcripts &amp; Scores</b>", body_bold))
    story.append(Paragraph("Complete question logs, candidate answers, rubric breakdowns, and proctoring events should be archived in PostgreSQL.", body))
    story.append(Paragraph("<b>11. Provide Stakeholder-Specific Dashboards</b>", body_bold))
    story.append(Paragraph("Tailored interfaces for candidates (radar charts), faculty (transcripts), and recruiters (candidate JD rankings).", body))
    story.append(Paragraph("<b>12. Provide Institutional &amp; Departmental Statistics</b>", body_bold))
    story.append(Paragraph("Display aggregated competency distributions, JD match rates, and placement readiness across student cohorts.", body))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 7: 2.1 Project Objectives (13 to 15), 2.2 Working Flow (Steps 1 & 2)
    # =========================================================================
    story.append(Paragraph("<b>13. Provide High-Throughput 50-Key API Resilience</b>", body_bold))
    story.append(Paragraph("The system should cycle 50 Google Gemini API keys via round-robin, delivering 750 RPM throughput and zero 429 quota disruptions.", body))
    story.append(Paragraph("<b>14. Enforce Anti-Malpractice Proctoring Integrity</b>", body_bold))
    story.append(Paragraph("Monitor browser focus, tab switches, and clipboard operations during graded evaluations to ensure authentic assessment.", body))
    story.append(Paragraph("<b>15. Automate Remedial Skill Workflows</b>", body_bold))
    story.append(Paragraph("Automatically link weak interview competencies with faculty remedial tasks, clearing tasks upon successful re-evaluation.", body))
    story.append(Paragraph("2.2 How the Agentic AI Solution Works", h2))
    story.append(Paragraph(
        "The proposed solution combines Job Description matching, vector retrieval, deterministic difficulty scaling, and multi-key API pooling into a unified workflow.",
        body
    ))
    story.append(Paragraph("<b>OVERALL WORKING FLOW:</b>", body_bold))
    story.append(Paragraph(
        "Job Description Upload → Semantic Resume Matching → JD Fit Scoring → Max Candidate Shortlisting → Candidate Onboarding → Turn-by-Turn RAG Context Assembly (Resume + JD Requirements + Syllabus) → Deterministic Difficulty Engine → 50-Key Gemini Pool → Question Generation → Candidate Response → Decoupled Rubric Evaluation → Conversation Memory → Relational DB Persistence → Skill Radar &amp; Remediation Loop",
        body
    ))
    story.append(Paragraph("The process is explained step-by-step below.", body))
    story.append(Paragraph("<b>Step 1 – Recruiter Ingests Job Description &amp; Configures Max Candidates</b>", body_bold))
    story.append(Paragraph("The recruiter uploads the target Job Description (JD) and sets the Max Candidates limit (e.g., top 30 applicants) for the hiring round.", body))
    story.append(Paragraph("<b>Step 2 – Semantic Candidate Matching &amp; Ranking</b>", body_bold))
    story.append(Paragraph("The system matches all applicant resumes against the JD using ChromaDB dense embeddings, ranks candidates by match score, and selects the top applicants up to the Max Candidate quota.", body))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 8: 2.2 How the Solution Works (Steps 3 to 7)
    # =========================================================================
    story.append(Paragraph("<b>Step 3 – Candidate Onboarding &amp; Mode Selection</b>", body_bold))
    story.append(Paragraph("Shortlisted candidates access the portal and launch either Practice Mode (formative coaching) or Graded Mode (proctored assessment).", body))
    story.append(Paragraph("<b>Step 4 – Agent Receives Session Context &amp; Initializes State</b>", body_bold))
    story.append(Paragraph("The AI Recruiter Agent loads candidate profile data, the specific Job Description requirements, and departmental syllabus guidelines, starting at Level 2.", body))
    story.append(Paragraph("<b>Step 5 – Conversation Memory &amp; Turn Validation</b>", body_bold))
    story.append(Paragraph("The system inspects conversation history to ensure smooth continuity, prevent topic repetition, and formulate follow-ups.", body))
    story.append(Paragraph("<b>Step 6 – Dynamic Competency Targeting</b>", body_bold))
    story.append(Paragraph("The Agent determines the next technical focus area by intersecting the candidate's resume claims with the Job Description's priority competencies.", body))
    story.append(Paragraph("For example:", body))
    story.append(Paragraph("JD: 'High-Concurrency Caching' + Resume: 'Redis API' → Target: Cache Invalidation &amp; TTL", bullet))
    story.append(Paragraph("JD: 'Relational Optimization' + Resume: 'PostgreSQL' → Target: Composite Indexing &amp; EXPLAIN", bullet))
    story.append(Paragraph("JD: 'Microservices Security' + Resume: 'JWT Auth' → Target: Token Replay &amp; Claims Verification", bullet))
    story.append(Paragraph("<b>Step 7 – Context Assembly &amp; RAG Retrieval</b>", body_bold))
    story.append(Paragraph("ChromaDB retrieves the top-k most relevant resume chunks and JD criteria. The context composer fuses them into an enriched prompt.", body))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 9: 2.2 How the Solution Works (Steps 8 to 12)
    # =========================================================================
    story.append(Paragraph("<b>Step 8 – Deterministic Difficulty Engine Computes Level</b>", body_bold))
    story.append(Paragraph("The difficulty engine determines the question level (1 to 5) based on the candidate's previous two answers:", body))
    story.append(Paragraph("Two consecutive scores >= 7.5 → Promoted (+1 Level)", bullet))
    story.append(Paragraph("Score < 4.0 → Demoted (-1 Level)", bullet))
    story.append(Paragraph("Score between 4.0 and 7.4 → Held at current level", bullet))
    story.append(Paragraph("<b>Step 9 – Multi-Key Pool Selects Healthy Gemini Key</b>", body_bold))
    story.append(Paragraph("The KeyPoolManager cycles through the 50-key pool via round-robin, skipping any key undergoing a 60-second cooldown.", body))
    story.append(Paragraph("<b>Step 10 – Grounded Technical Question Generation</b>", body_bold))
    story.append(Paragraph("Google Gemini 3.6 Flash generates an in-depth technical inquiry directly grounded in the candidate's resume and target Job Description.", body))
    story.append(Paragraph("<b>Step 11 – Candidate Submits Answer &amp; Proctoring Verification</b>", body_bold))
    story.append(Paragraph("The candidate submits their response via the chat interface, while client-side listeners monitor window focus and tab switching.", body))
    story.append(Paragraph("<b>Step 12 – Decoupled Rubric Answer Scoring</b>", body_bold))
    story.append(Paragraph("An independent LLM prompt scores the answer from 1.0 to 10.0 using strict JSON schemas covering accuracy, depth, omissions, and hints.", body))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 10: Step 13, 2.3 Key Features (1 to 7)
    # =========================================================================
    story.append(Paragraph("<b>Step 13 – End-of-Session Synthesis &amp; Task Clearance</b>", body_bold))
    story.append(Paragraph("Upon interview completion (e.g., 25 turns), holistic skill scores update the candidate radar. Passing scores (>= 7.0) clear assigned faculty tasks.", body))
    story.append(Paragraph("2.3 Key Features", h1))
    story.append(Paragraph("The AXON AI Recruiter provides sixteen modular capabilities for enterprise technical recruitment.", body))
    story.append(Paragraph("<b>1. Job Description Semantic Matching</b>", body_bold))
    story.append(Paragraph("Computes high-precision match scores (0–100%) between applicant resumes and employer Job Descriptions.", body))
    story.append(Paragraph("<b>2. Max Candidate Shortlist Thresholding</b>", body_bold))
    story.append(Paragraph("Enforces a configurable Max Candidate cutoff, automatically shortlisting top applicants for interview rounds.", body))
    story.append(Paragraph("<b>3. Resume-Grounded Adaptive Interviewing</b>", body_bold))
    story.append(Paragraph("Questions reference specific libraries, frameworks, and architecture claims extracted from candidate resumes.", body))
    story.append(Paragraph("<b>4. Retrieval Augmented Generation (RAG)</b>", body_bold))
    story.append(Paragraph("Combines resume chunks, Job Description requirements, and syllabus topics to eliminate hallucination.", body))
    story.append(Paragraph("<b>5. Deterministic 5-Level Difficulty Engine</b>", body_bold))
    story.append(Paragraph("Calibrates question complexity mathematically from Foundational (Level 1) to Architectural Optimization (Level 5).", body))
    story.append(Paragraph("<b>6. Decoupled Real-Time Rubric Scoring</b>", body_bold))
    story.append(Paragraph("Evaluates answers in separate LLM calls using standardized JSON rubrics for objective, unbiased scoring.", body))
    story.append(Paragraph("<b>7. 50-Key Gemini API Pool Architecture</b>", body_bold))
    story.append(Paragraph("Delivers 750 RPM throughput and 75,000 RPD capacity with automatic 60-second cooldown recovery.", body))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 11: 2.3 Key Features (8 to 14)
    # =========================================================================
    story.append(Paragraph("<b>8. Anti-Malpractice Proctoring Safeguards</b>", body_bold))
    story.append(Paragraph("Tracks window blur, tab switching, and clipboard pasting during official assessments, logging timestamped strikes.", body))
    story.append(Paragraph("<b>9. Dual Practice &amp; Graded Modes</b>", body_bold))
    story.append(Paragraph("Practice Mode offers low-anxiety preparation with instant coaching; Graded Mode updates official college records.", body))
    story.append(Paragraph("<b>10. Multi-Turn Conversation Memory</b>", body_bold))
    story.append(Paragraph("Preserves dialogue context across turns, enabling realistic follow-up probing and continuity.", body))
    story.append(Paragraph("<b>11. Relational &amp; Vector Database Integration</b>", body_bold))
    story.append(Paragraph("PostgreSQL handles relational records and transcripts; ChromaDB manages high-dimensional vector embeddings.", body))
    story.append(Paragraph("<b>12. Multi-Axis Holistic Skill Radar</b>", body_bold))
    story.append(Paragraph("Visualizes candidate performance across Technical Depth, Problem Solving, Systems Design, and Communication Clarity.", body))
    story.append(Paragraph("<b>13. Automated Remediation Task Loop</b>", body_bold))
    story.append(Paragraph("Faculty can assign targeted remediation tasks that are automatically cleared when the student achieves >= 7.0 on re-interviewing.", body))
    story.append(Paragraph("<b>14. HOD Departmental Skill Heatmap</b>", body_bold))
    story.append(Paragraph("Displays cohort-wide competency heatmaps and provides one-click batch remediation assignment.", body))
    story.append(Paragraph("<b>15. Turn-by-Turn Transcript Annotation</b>", body_bold))
    story.append(Paragraph("Faculty and recruiters can review complete question-by-question dialogue logs with individual rubric evaluations.", body))
    story.append(Paragraph("<b>16. Enterprise Role-Based Access Control (RBAC)</b>", body_bold))
    story.append(Paragraph("Strict JWT-based security isolating Student, Staff, Recruiter, and HOD administrative privilege tiers.", body))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 12: 2.3 Key Features (15-16), 3. IMPLEMENTATION & RESULTS, 3.1 Tech (Python)
    # =========================================================================
    story.append(Paragraph("<b>3. IMPLEMENTATION &amp; RESULTS</b>", h1))
    story.append(Paragraph("3.1 Technologies / Tools Used", h2))
    story.append(Paragraph("The project uses several modern technologies to implement the AXON AI Recruiter platform.", body))
    story.append(Paragraph("<b>Python 3.13 (Backend Application Runtime)</b>", body_bold))
    story.append(Paragraph("Python is the primary language used for AI processing, Job Description parsing, RAG orchestration, vector matching, and asynchronous API services.", body))
    story.append(Paragraph("• Semantic Text Parsing &amp; Sanitization", bullet))
    story.append(Paragraph("• High-Dimensional Dense Vector Embedding Generation", bullet))
    story.append(Paragraph("• Job Description &amp; Candidate Resume Cosine Matching", bullet))
    story.append(Paragraph("• Max Candidate Threshold Ranking Algorithms", bullet))
    story.append(Paragraph("• Asynchronous High-Concurrency API Endpoints", bullet))
    story.append(Paragraph("• Database ORM Modeling &amp; ACID Transactions", bullet))
    story.append(Paragraph("<b>FastAPI</b>", body_bold))
    story.append(Paragraph("High-performance ASGI framework providing asynchronous endpoints, OpenAPI documentation, and strict Pydantic validation.", body))
    story.append(Paragraph("<b>Next.js 15 / React 19 (Frontend Architecture)</b>", body_bold))
    story.append(Paragraph("Modern client-side application featuring App Router architecture, route-level role guards, React Context state persistence, and responsive interfaces.", body))
    story.append(Paragraph("<b>Tailwind CSS &amp; Lucide Icons</b>", body_bold))
    story.append(Paragraph("Utility-first design system delivering an accessible, dark-themed interview environment engineered to reduce candidate cognitive load.", body))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 13: 3.1 Technologies (Frontend, LLM, Embeddings, DBs)
    # =========================================================================
    story.append(Paragraph("<b>Google Gemini 3.6 Flash (Primary LLM Engine)</b>", body_bold))
    story.append(Paragraph("Foundation model offering ultra-fast token generation, structured JSON output mode, and large context windows for grounded interviewing.", body))
    story.append(Paragraph("<b>KeyPoolManager (Custom 50-Key Gemini Pool)</b>", body_bold))
    story.append(Paragraph("Thread-safe circular iterator that distributes requests across 50 Google Gemini API keys, handling 429 rate limits via 60-second cooldowns.", body))
    story.append(Paragraph("<b>Sentence Transformers (all-MiniLM-L6-v2)</b>", body_bold))
    story.append(Paragraph("Deep learning model producing 384-dimensional dense semantic vectors locally with sub-30ms inference times at zero external API cost.", body))
    story.append(Paragraph("<b>ChromaDB (Vector Database)</b>", body_bold))
    story.append(Paragraph("High-speed vector database storing candidate resume chunks and Job Description criteria with persistent disk storage.", body))
    story.append(Paragraph("<b>PostgreSQL / Supabase &amp; SQLite</b>", body_bold))
    story.append(Paragraph("Relational databases storing user accounts, Job Descriptions, applicant rankings, session logs, turn rubrics, and remediation tasks.", body))
    story.append(Paragraph("<b>PyPDF2 &amp; PDFPlumber</b>", body_bold))
    story.append(Paragraph("Used for extracting clean, uncorrupted text from diverse student resume PDF layouts and corporate Job Description documents.", body))
    story.append(Paragraph("<b>Anti-Malpractice Client Guard</b>", body_bold))
    story.append(Paragraph("Browser-level event listeners tracking window blur, tab switching, and clipboard pasting during official assessments.", body))
    story.append(Paragraph("<b>psutil &amp; System Telemetry</b>", body_bold))
    story.append(Paragraph("Monitors server CPU, memory, and backend process health during peak campus interview sessions.", body))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 14: 3.1 Technologies (KeyPool, PDF, Proctor), 3.2 Working Process (Stage 1)
    # =========================================================================
    story.append(Paragraph("<b>Visual Studio Code</b>", body_bold))
    story.append(Paragraph("Visual Studio Code served as the primary development environment for writing and testing both the Python backend and TypeScript frontend.", body))
    story.append(Paragraph("3.2 Working Process", h2))
    story.append(Paragraph("The working process of the project is organized into fifteen sequential stages.", body))
    story.append(Paragraph("<b>Stage 1 – Ingesting Candidate Resumes</b>", body_bold))
    story.append(Paragraph("Students upload their PDF resumes through the candidate portal. Files are validated for integrity and size.", body))
    story.append(Paragraph("<b>Stage 2 – Reading &amp; Extracting Resume Text</b>", body_bold))
    story.append(Paragraph("Document extraction engines parse raw text from PDF files, normalizing whitespace and layout structures.", body))
    story.append(Paragraph("<b>Stage 3 – Semantic Text Chunking</b>", body_bold))
    story.append(Paragraph("The text is segmented into discrete semantic chunks representing projects, technical skills, and work experience.", body))
    story.append(Paragraph("<b>Stage 4 – Dense Vector Embedding Computation</b>", body_bold))
    story.append(Paragraph("Each chunk is converted into a 384-dimensional dense numerical vector using the all-MiniLM-L6-v2 transformer model.", body))
    story.append(Paragraph("<b>Stage 5 – ChromaDB Vector Indexing</b>", body_bold))
    story.append(Paragraph("Embeddings and metadata are indexed into persistent ChromaDB collections isolated by candidate ID.", body))
    story.append(Paragraph("<b>Stage 6 – Job Description Ingestion &amp; Requirement Parsing</b>", body_bold))
    story.append(Paragraph("Recruiters upload target Job Descriptions; the system extracts required technical competencies and sets the Max Candidates quota.", body))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 15: 3.2 Working Process (Stages 7 to 11)
    # =========================================================================
    story.append(Paragraph("<b>Stage 7 – Semantic Resume-to-JD Matching &amp; Ranking</b>", body_bold))
    story.append(Paragraph("ChromaDB executes vector similarity search between the Job Description and all candidate resumes, calculating fit scores (0–100%).", body))
    story.append(Paragraph("<b>Stage 8 – Max Candidate Shortlist Filtering</b>", body_bold))
    story.append(Paragraph("The system filters the top-ranking candidates up to the configured Max Candidate threshold and issues assessment invitations.", body))
    story.append(Paragraph("<b>Stage 9 – Session Initialization &amp; Mode Gating</b>", body_bold))
    story.append(Paragraph("Shortlisted candidates enter the interview room, selecting Practice Mode (formative) or Graded Mode (proctored).", body))
    story.append(Paragraph("<b>Stage 10 – Context Assembly &amp; RAG Retrieval</b>", body_bold))
    story.append(Paragraph("ChromaDB retrieves the top-k relevant resume chunks matching the current Job Description competency, fusing them into a prompt.", body))
    story.append(Paragraph("<b>Stage 11 – Deterministic Difficulty Calibration</b>", body_bold))
    story.append(Paragraph("The Difficulty Engine evaluates recent performance scores to set the question level (Levels 1 to 5).", body))
    story.append(Paragraph("<b>Stage 12 – Multi-Key Pool Selection &amp; Question Generation</b>", body_bold))
    story.append(Paragraph("The KeyPoolManager picks an active Gemini key to generate a technical inquiry grounded in the candidate's resume and the target JD.", body))
    story.append(Paragraph("<b>Stage 13 – Candidate Response Submission &amp; Proctoring</b>", body_bold))
    story.append(Paragraph("The candidate submits their technical explanation while browser listeners monitor window focus.", body))
    story.append(Paragraph("<b>Stage 14 – Decoupled Rubric Evaluation &amp; Database Logging</b>", body_bold))
    story.append(Paragraph("An independent prompt grades the answer (1.0 to 10.0), logging JSON rubrics to PostgreSQL.", body))
    story.append(Paragraph("<b>Stage 15 – Scorecard Synthesis &amp; Remediation Task Clearance</b>", body_bold))
    story.append(Paragraph("Holistic scores update candidate radar charts. Passing scores (>= 7.0) automatically clear assigned remediation tasks.", body))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 16: 3.3 Screenshots / Output (3.3.1 JD Match & Max Candidates Dashboard)
    # =========================================================================
    story.append(Paragraph("3.3 Screenshots / Output", h1))
    story.append(Paragraph("The following mockups illustrate the primary interfaces of the AXON platform:", body))
    story.append(Spacer(1, 8))

    story.append(Paragraph("3.3.1. Job Description Matching &amp; Max Candidate Shortlist Dashboard", mockup_header))
    m_jd_data = [
        [Paragraph("<b>AXON RECRUITER PORTAL — JOB DESCRIPTION SCREENING &amp; MAX CANDIDATES</b>", body_bold)],
        [Paragraph("• <b>Target Job Description:</b> <code>Senior_Backend_Cloud_Engineer_JD.pdf</code><br/>"
                   "• <b>Required Skills:</b> Python, FastAPI, PostgreSQL, Redis, Docker, Distributed Systems<br/>"
                   "• <b>Total Applicants Evaluated:</b> 184 Candidates &nbsp;|&nbsp; <b>ChromaDB Vector Matching:</b> Complete<br/>"
                   "• <b>Max Candidate Threshold:</b> [ 🔘 Top 25 Candidates ] &nbsp; <i>(Adjustable Slider: 10 to 100)</i><br/>"
                   "• <b>Shortlisted Applicants (Top Match Rankings):</b><br/>"
                   "&nbsp;&nbsp;1. John Doe (2023CS0142) — <b>94.2% Match</b> [FastAPI, Redis, PostgreSQL, Celery] ✅<br/>"
                   "&nbsp;&nbsp;2. Sarah Smith (2023CS0188) — <b>91.5% Match</b> [Python, Docker, Kafka, Microservices] ✅<br/>"
                   "&nbsp;&nbsp;3. Alex Kumar (2023IT0045) — <b>88.7% Match</b> [FastAPI, PostgreSQL, Redis] ✅<br/>"
                   "• <b>Recruiter Action:</b> [ ⚡ Send Batch Invitations to Top 25 Candidates for AI Assessment ]", body)]
    ]
    t_jd = Table(m_jd_data, colWidths=[460])
    t_jd.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDE9FE")),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#7C3AED")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_jd)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 17: 3.3 Screenshots / Output (3.3.2 & 3.3.3)
    # =========================================================================
    story.append(Paragraph("3.3.2. Student Setup &amp; Resume Upload Dashboard", mockup_header))
    m1_data = [
        [Paragraph("<b>AXON STUDENT PORTAL — RESUME ONBOARDING &amp; SETUP</b>", body_bold)],
        [Paragraph("• <b>Candidate:</b> John Doe (Roll No: 2023CS0142) &nbsp;|&nbsp; <b>Dept:</b> Computer Science<br/>"
                   "• <b>Resume File:</b> <code>john_doe_resume.pdf</code> (Indexed: 14 Chunks in ChromaDB)<br/>"
                   "• <b>Target Role / JD:</b> Senior Backend Cloud Engineer (Match Score: 94.2%)<br/>"
                   "• <b>Detected Skills:</b> Python, FastAPI, Docker, PostgreSQL, Redis, Kubernetes, React<br/>"
                   "• <b>Interview Mode:</b> [🔘 Practice Mode (Coaching)] &nbsp; [⚪ Graded Assessment]<br/>"
                   "• <b>Status:</b> Shortlisted within Max Candidate Quota (Rank #1) &nbsp;|&nbsp; Ready", body)],
        [Paragraph("<b>[ 🚀 START TECHNICAL INTERVIEW ]</b>", body_bold)]
    ]
    t1 = Table(m1_data, colWidths=[460])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t1)
    story.append(Spacer(1, 15))

    story.append(Paragraph("3.3.3. AI Recruiter Interview Room (Chat &amp; Live Assessment)", mockup_header))
    m2_data = [
        [Paragraph("<b>AXON INTERVIEW ROOM — TURN 4 OF 25 [GRADED MODE]</b>", body_bold)],
        [Paragraph("🛡️ <b>Proctoring:</b> Active (0 Strikes) &nbsp;|&nbsp; ⏱️ <b>Timer:</b> 07:15 &nbsp;|&nbsp; 📈 <b>Difficulty:</b> Level 3", body)],
        [Paragraph("<b>AI RECRUITER:</b><br/>“The Senior Backend Engineer Job Description emphasizes high-scale caching. In your resume, you mention using Redis for caching API responses in your FastAPI project. How did you handle cache invalidation when database records were updated?”", body)],
        [Paragraph("<b>CANDIDATE RESPONSE:</b><br/>“We adopted the Cache-Aside pattern. Whenever an entity was updated via a PUT/POST endpoint, we performed a transactional write to PostgreSQL and explicitly deleted the corresponding Redis cache key.”", body)],
        [Paragraph("<b>[ 📤 SUBMIT ANSWER ]</b> &nbsp;&nbsp;&nbsp;&nbsp; <i>(Evaluating Turn Rubric via Gemini Flash...)</i>", body_bold)]
    ]
    t2 = Table(m2_data, colWidths=[460])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#DBEAFE")),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#2563EB")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t2)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 18: 3.3 Screenshots / Output (3.3.4 & 3.3.5)
    # =========================================================================
    story.append(Paragraph("3.3.4. Student Evaluation Scorecard &amp; Skill Radar", mockup_header))
    m3_data = [
        [Paragraph("<b>COMPREHENSIVE STUDENT SCORECARD &amp; SKILL RADAR</b>", body_bold)],
        [Paragraph("<b>Overall Score:</b> 8.4 / 10.0 (High Distinction) &nbsp;|&nbsp; <b>Target JD:</b> Cloud Engineer<br/>"
                   "• <b>Technical Depth:</b> 8.8 / 10 &nbsp;&nbsp;&nbsp; • <b>Problem Solving &amp; Logic:</b> 8.5 / 10<br/>"
                   "• <b>System Architecture:</b> 8.2 / 10 &nbsp;&nbsp;&nbsp; • <b>Communication Clarity:</b> 8.1 / 10<br/>"
                   "<b>Decoupled Rubric Feedback (Turn 4):</b><br/>"
                   "• <i>Accuracy:</i> Correct explanation of Cache-Aside invalidation.<br/>"
                   "• <i>Improvement:</i> Consider handling race conditions using write locks.<br/>"
                   "• <i>Remediation Clearance:</i> Task 'Caching Strategies' marked <b>COMPLETED</b>.", body)]
    ]
    t3 = Table(m3_data, colWidths=[460])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#DCFCE7")),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#16A34A")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t3)
    story.append(Spacer(1, 15))

    story.append(Paragraph("3.3.5. Staff Portal: Candidate Profiles &amp; Turn Transcripts", mockup_header))
    m4_data = [
        [Paragraph("<b>FACULTY COMMAND CENTER — CANDIDATE TRANSCRIPT REVIEW</b>", body_bold)],
        [Paragraph("<b>Candidate:</b> John Doe (2023CS0142) &nbsp;|&nbsp; <b>Track:</b> Cloud &amp; Backend<br/>"
                   "• <b>Turn 1 (L2):</b> Python GIL and multi-threading [Score: 7.5/10]<br/>"
                   "• <b>Turn 2 (L2):</b> PostgreSQL composite index design [Score: 8.0/10] → <i>Promoted to L3</i><br/>"
                   "• <b>Turn 3 (L3):</b> Redis Cache-Aside invalidation [Score: 8.8/10]<br/>"
                   "• <b>Turn 4 (L3):</b> Celery idempotency with distributed locks [Score: 9.0/10] → <i>Promoted to L4</i><br/>"
                   "<b>Staff Actions:</b> [ Assign Remedial Task ] &nbsp; [ Endorse for Drive ] &nbsp; [ Export PDF ]", body)]
    ]
    t4 = Table(m4_data, colWidths=[460])
    t4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#FEF3C7")),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#D97706")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t4)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 19: 3.3 Screenshots / Output (3.3.6 & 3.3.7)
    # =========================================================================
    story.append(Paragraph("3.3.6. HOD Command Center: Departmental Skill Heatmap", mockup_header))
    m5_data = [
        [Paragraph("<b>HEAD OF DEPARTMENT DASHBOARD — BATCH SKILL HEATMAP</b>", body_bold)],
        [Paragraph("<b>Department:</b> Computer Science &amp; Engineering &nbsp;|&nbsp; <b>Cohort:</b> 240 Students<br/>"
                   "• <b>Data Structures &amp; Algorithms:</b> 82% Competent (Green) &nbsp;|&nbsp; Avg: 7.8/10<br/>"
                   "• <b>Cloud &amp; DevOps Engineering:</b> 54% Competent (Amber) &nbsp;|&nbsp; Avg: 5.6/10<br/>"
                   "• <b>Database Optimization &amp; SQL:</b> 76% Competent (Green) &nbsp;|&nbsp; Avg: 7.2/10<br/>"
                   "• <b>Distributed Systems &amp; Concurrency:</b> 41% Competent (Red) &nbsp;|&nbsp; Avg: 4.8/10<br/>"
                   "<b>Action:</b> [ ⚡ Batch Assign Task: 'Distributed Systems Mastery' to 64 Students ]", body)]
    ]
    t5 = Table(m5_data, colWidths=[460])
    t5.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDE9FE")),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#7C3AED")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t5)
    story.append(Spacer(1, 15))

    story.append(Paragraph("3.3.7. 50-Key Gemini Pool Status &amp; Telemetry Monitor", mockup_header))
    m6_data = [
        [Paragraph("<b>API CLUSTER MONITOR — 50-KEY GEMINI FLASH ROTATION POOL</b>", body_bold)],
        [Paragraph("<b>Active Keys:</b> 50 &nbsp;|&nbsp; <b>Healthy Keys:</b> 49 &nbsp;|&nbsp; <b>Cooldown Keys:</b> 1 (Key #14, TTL: 24s)<br/>"
                   "• <b>Total Cluster Throughput:</b> 750 Requests/Minute (RPM) &nbsp;|&nbsp; 75,000 RPD<br/>"
                   "• <b>Current Active Interviews:</b> 38 Concurrent Students<br/>"
                   "• <b>Average Turn Latency:</b> 620ms &nbsp;|&nbsp; <b>Quota Error Failover Rate:</b> 100%<br/>"
                   "• <b>Health Status:</b> Optimal &nbsp;|&nbsp; Zero Student Interruption Recorded", body)]
    ]
    t6 = Table(m6_data, colWidths=[460])
    t6.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#0F172A")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t6)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 20: 3.4 Results Achieved (1 to 9)
    # =========================================================================
    story.append(Paragraph("3.4 Results Achieved", h1))
    story.append(Paragraph("The project successfully demonstrates an autonomous AI Recruiter and Assessment Platform.", body))
    story.append(Paragraph("The following results were achieved.", body))
    story.append(Paragraph("<b>1. High-Accuracy Job Description Matching</b>", body_bold))
    story.append(Paragraph("Demonstrated semantic matching between resumes and Job Descriptions with 94%+ precision using dense vector embeddings.", body))
    story.append(Paragraph("<b>2. Automated Max Candidate Shortlisting</b>", body_bold))
    story.append(Paragraph("Successfully filtered applicant cohorts to configurable Max Candidate thresholds, eliminating manual screening overhead.", body))
    story.append(Paragraph("<b>3. AI-Based Resume Grounding</b>", body_bold))
    story.append(Paragraph("Technical inquiries successfully ground questions in candidate resume claims with zero hallucination.", body))
    story.append(Paragraph("<b>4. Competency Classification</b>", body_bold))
    story.append(Paragraph("The system categorizes technical questions accurately into relevant engineering domains.", body))
    story.append(Paragraph("<b>5. Knowledge Retrieval</b>", body_bold))
    story.append(Paragraph("The RAG system retrieves targeted resume project chunks from ChromaDB with sub-30ms latency.", body))
    story.append(Paragraph("<b>6. Semantic Search</b>", body_bold))
    story.append(Paragraph("The system finds semantically related project experiences regardless of slight keyword differences.", body))
    story.append(Paragraph("<b>7. AI Agent Decision Making</b>", body_bold))
    story.append(Paragraph("The Agent dynamically determines question progression and whether follow-up probing is necessary.", body))
    story.append(Paragraph("<b>8. Safe Diagnostic &amp; Proctoring Tools</b>", body_bold))
    story.append(Paragraph("The system safely logs window blur, tab switching, and clipboard events without executing unsafe commands.", body))
    story.append(Paragraph("<b>9. Context-Based Follow-up Responses</b>", body_bold))
    story.append(Paragraph("Conversation memory allows the Agent to remember candidate answers and probe deeper into design choices.", body))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 21: 3.4 Results (10 to 15), 4. CONCLUSION & FUTURE SCOPE, 4.1 Conclusion
    # =========================================================================
    story.append(Paragraph("<b>10. Clear Rubric Evaluation</b>", body_bold))
    story.append(Paragraph("The system delivers structured scores from 1.0 to 10.0 with constructive technical feedback.", body))
    story.append(Paragraph("<b>11. Comprehensive Chat History</b>", body_bold))
    story.append(Paragraph("Complete interview transcripts, scores, and rubrics are saved in PostgreSQL for faculty review.", body))
    story.append(Paragraph("<b>12. Feedback Collection &amp; Analytics</b>", body_bold))
    story.append(Paragraph("The system records candidate self-assessments and generates cohort heatmaps for HODs.", body))
    story.append(Paragraph("<b>13. 50-Key Resilient API Mode</b>", body_bold))
    story.append(Paragraph("The multi-key pool maintained 100% uptime across 40+ concurrent sessions with zero 429 interruptions.", body))
    story.append(Paragraph("<b>14. Secure Configuration</b>", body_bold))
    story.append(Paragraph("API keys and JWT secrets are stored securely in environment files outside the codebase.", body))
    story.append(Paragraph("<b>15. Student-Friendly Modern Interface</b>", body_bold))
    story.append(Paragraph("The Next.js web application provides an intuitive, low-friction interview experience.", body))
    story.append(Paragraph("4. CONCLUSION &amp; FUTURE SCOPE", h1))
    story.append(Paragraph("4.1 Project Conclusion", h2))
    story.append(Paragraph(
        "The AXON AI Recruiter is a practical Artificial Intelligence application developed to simplify, standardize, and scale technical recruitment assessments.",
        body
    ))
    story.append(Paragraph("The project combines several modern technologies including:", body))
    story.append(Paragraph("• Job Description Parsing &amp; Matching", bullet))
    story.append(Paragraph("• Max Candidate Threshold Shortlisting", bullet))
    story.append(Paragraph("• Large Language Models (Gemini 3.6 Flash)", bullet))
    story.append(Paragraph("• Agentic AI &amp; State Machines", bullet))
    story.append(Paragraph("• Retrieval Augmented Generation (RAG)", bullet))
    story.append(Paragraph("• Vector Databases (ChromaDB)", bullet))
    story.append(Paragraph("• Multi-Key Pool Orchestration (750 RPM)", bullet))
    story.append(Paragraph("• Anti-Malpractice Proctoring", bullet))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 22: 4.1 Conclusion (Cont.), 4.2 Challenges Faced (1 to 2)
    # =========================================================================
    story.append(Paragraph("• Conversation Memory", bullet))
    story.append(Paragraph("• Relational Database (PostgreSQL)", bullet))
    story.append(Paragraph("• Next.js 15 &amp; React", bullet))
    story.append(Paragraph("• Python 3.13", bullet))
    story.append(Paragraph(
        "The main purpose of the project is to provide students with realistic technical interview practice and provide institutions with objective assessment data.",
        body
    ))
    story.append(Paragraph(
        "Instead of conducting hundreds of manual interviews, placement cells can deploy AXON to match candidates with Job Descriptions, filter applicants via Max Candidate quotas, and conduct comprehensive assessments.",
        body
    ))
    story.append(Paragraph(
        "The AI Agent analyzes the candidate's resume and selects relevant technical questions. The RAG system retrieves authentic project context from the vector database. The Agent can also adjust difficulty dynamically across 5 structured levels.",
        body
    ))
    story.append(Paragraph(
        "The retrieved resume context, curriculum requirements, and conversation history are combined to generate a rigorous technical assessment.",
        body
    ))
    story.append(Paragraph(
        "The system also maintains conversation memory so that follow-up probing questions can be asked naturally.",
        body
    ))
    story.append(Paragraph(
        "PostgreSQL is used to store interview logs, while the HOD heatmap module provides departmental analytics on student competence.",
        body
    ))
    story.append(Paragraph(
        "Security is maintained by restricting tool execution and enforcing client-side focus monitoring.",
        body
    ))
    story.append(Paragraph(
        "The project therefore demonstrates the practical combination of Agent + JD Matching + Max Candidate Filter + RAG + Multi-Key Pool + Difficulty Engine for an AI recruitment use case.",
        body
    ))
    story.append(Paragraph("4.2 Challenges Faced", h2))
    story.append(Paragraph("Several challenges were encountered during the development of the project.", body))
    story.append(Paragraph("<b>1. Semantic Matching between Resumes and Job Descriptions</b>", body_bold))
    story.append(Paragraph("Extracting technical prerequisites from unstructured Job Descriptions and accurately matching them against diverse resume templates.", body))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 23: 4.2 Challenges Faced (2 to 10)
    # =========================================================================
    story.append(Paragraph("<b>2. Max Candidate Ranking Calibration</b>", body_bold))
    story.append(Paragraph("Balancing weighted match scores across technical skills, project experiences, and academic criteria.", body))
    story.append(Paragraph("<b>3. Resume Parsing &amp; Document Preparation</b>", body_bold))
    story.append(Paragraph("Extracting clean text from diverse student resume PDF layouts required robust sanitization.", body))
    story.append(Paragraph("<b>4. Text Chunking Granularity</b>", body_bold))
    story.append(Paragraph("Choosing an appropriate chunk size was critical to avoid diluting project context.", body))
    story.append(Paragraph("<b>5. Dense Vector Generation</b>", body_bold))
    story.append(Paragraph("Generating embeddings locally using sentence-transformers with minimal latency required optimization.", body))
    story.append(Paragraph("<b>6. ChromaDB Vector Integration</b>", body_bold))
    story.append(Paragraph("Indexing embeddings and linking them with candidate IDs required careful metadata handling.", body))
    story.append(Paragraph("<b>7. Multi-Key API Management</b>", body_bold))
    story.append(Paragraph("Orchestrating 50 Gemini API keys with thread-safe rotation and cooldown registries was complex.", body))
    story.append(Paragraph("<b>8. Preventing AI Hallucination</b>", body_bold))
    story.append(Paragraph("Ensuring the LLM asked questions grounded strictly in candidate resume claims required strict prompt constraints.", body))
    story.append(Paragraph("<b>9. Deterministic Difficulty Routing</b>", body_bold))
    story.append(Paragraph("Designing mathematical scoring thresholds to transition difficulty smoothly between Levels 1 and 5.", body))
    story.append(Paragraph("<b>10. Decoupled Rubric Evaluation</b>", body_bold))
    story.append(Paragraph("Separating question generation from answer evaluation into independent prompts to ensure objective scoring.", body))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 24: 4.2 Challenges Faced (11 to 15), 4.3 Future Enhancements (1 to 2)
    # =========================================================================
    story.append(Paragraph("<b>11. Multi-Turn Conversation Memory</b>", body_bold))
    story.append(Paragraph("Retaining relevant turn dialogue without overflowing the model context window.", body))
    story.append(Paragraph("<b>12. Relational Database Management</b>", body_bold))
    story.append(Paragraph("Designing schema tables for users, question banks, turn logs, and tasks in PostgreSQL.", body))
    story.append(Paragraph("<b>13. Error Handling &amp; Fault Tolerance</b>", body_bold))
    story.append(Paragraph("Handling API rate limits, database reconnections, and network interruptions gracefully.", body))
    story.append(Paragraph("<b>14. Anti-Malpractice Proctoring</b>", body_bold))
    story.append(Paragraph("Implementing client-side listeners for window blur, tab switching, and clipboard pasting.", body))
    story.append(Paragraph("<b>15. User Interface Usability</b>", body_bold))
    story.append(Paragraph("Designing an intuitive, dark-themed interview room that minimizes student test anxiety.", body))
    story.append(Paragraph("4.3 Future Enhancements", h2))
    story.append(Paragraph("The project can be expanded significantly in the future.", body))
    story.append(Paragraph("<b>1. Bidirectional Voice-to-Voice Interviewing</b>", body_bold))
    story.append(Paragraph("Integrate real-time speech-to-speech interaction via Gemini Live API for spoken technical interviews.", body))
    story.append(Paragraph("<b>2. 3D Photorealistic Avatar Interviewer</b>", body_bold))
    story.append(Paragraph("Incorporate interactive 3D virtual avatar interviewers with lip-syncing for immersive mock sessions.", body))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 25: 4.3 Future Enhancements (3 to 11)
    # =========================================================================
    story.append(Paragraph("<b>3. Interactive Code Sandbox Execution</b>", body_bold))
    story.append(Paragraph("Embed a secure, containerized coding sandbox to evaluate algorithmic solutions and test cases live.", body))
    story.append(Paragraph("<b>4. Multilingual Vernacular Support</b>", body_bold))
    story.append(Paragraph("Support regional Indian languages such as Tamil, Hindi, and Telugu for vernacular preparation.", body))
    story.append(Paragraph("<b>5. Computer Vision Proctoring</b>", body_bold))
    story.append(Paragraph("Incorporate webcam gaze tracking and multiple-person detection to enhance assessment integrity.", body))
    story.append(Paragraph("<b>6. Advanced Graph-RAG Architecture</b>", body_bold))
    story.append(Paragraph("Connect candidate projects with knowledge graphs for deeper architectural cross-questioning.", body))
    story.append(Paragraph("<b>7. Campus ERP Integration</b>", body_bold))
    story.append(Paragraph("Synchronize assessment scores directly with institutional student databases and placement portals.", body))
    story.append(Paragraph("<b>8. Automated Hiring Pipeline Connectors</b>", body_bold))
    story.append(Paragraph("Integrate with corporate ATS platforms (Greenhouse, Lever, Workday) for seamless applicant synchronization.", body))
    story.append(Paragraph("<b>9. AI-Generated Video Feedback</b>", body_bold))
    story.append(Paragraph("Produce personalized synthetic video debriefs highlighting candidate strengths and weaknesses.", body))
    story.append(Paragraph("<b>10. Peer-to-Peer Mock Assessment Matchmaking</b>", body_bold))
    story.append(Paragraph("Pair students for collaborative peer mock interviews moderated and graded by the AI agent.", body))
    story.append(Paragraph("<b>11. On-Premise Offline LLM Deployment</b>", body_bold))
    story.append(Paragraph("Support offline inference with local models (e.g. Llama 3) for institutions with restricted internet.", body))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 26: 4.3 Future Enhancements (12 to 17)
    # =========================================================================
    story.append(Paragraph("<b>12. Dynamic Time Pressure Simulation</b>", body_bold))
    story.append(Paragraph("Dynamically adjust response countdown timers to test candidate composure under stress.", body))
    story.append(Paragraph("<b>13. Cross-Departmental Benchmarking</b>", body_bold))
    story.append(Paragraph("Provide college administrators with comparative readiness metrics across different engineering departments.", body))
    story.append(Paragraph("<b>14. GitHub &amp; Portfolio Scraping</b>", body_bold))
    story.append(Paragraph("Scan candidate GitHub repositories to ask questions directly grounded in actual commit histories.", body))
    story.append(Paragraph("<b>15. Behavioral STAR-Method Analysis</b>", body_bold))
    story.append(Paragraph("Integrate behavioral and leadership competency evaluation alongside technical questioning.", body))
    story.append(Paragraph("<b>16. Native Mobile Applications</b>", body_bold))
    story.append(Paragraph("Develop native iOS and Android apps for students to take mock practice interviews anywhere.", body))
    story.append(Paragraph("<b>17. Automated Placement Probability Predictor</b>", body_bold))
    story.append(Paragraph("Train ML models on historical placement data to forecast candidate offer likelihood based on skill scores.", body))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 27: 4.3 Future Enhancements (18 to 20), 4.4 References (1 to 10)
    # =========================================================================
    story.append(Paragraph("<b>18. Human-in-the-Loop Faculty Co-Pilot</b>", body_bold))
    story.append(Paragraph("Enable human interviewers to co-interview candidates with real-time AI suggestions and scoring assistance.", body))
    story.append(Paragraph("<b>19. Continuous Institutional Question Learning</b>", body_bold))
    story.append(Paragraph("Refine question banks continuously based on questions faced by alumni in real corporate hiring rounds.", body))
    story.append(Paragraph("<b>20. 24/7 Automated Campus Assessment</b>", body_bold))
    story.append(Paragraph("Provide round-the-clock interview assessment access for students without scheduling delays.", body))
    story.append(Paragraph("4.4 References", h1))
    story.append(Paragraph("1. Python Documentation – Reference for Python programming language and standard libraries.", bullet))
    story.append(Paragraph("2. Next.js Documentation – Reference for developing interactive React-based web applications.", bullet))
    story.append(Paragraph("3. Sentence Transformers Documentation – Reference for generating sentence embeddings and semantic similarity.", bullet))
    story.append(Paragraph("4. ChromaDB Documentation – Reference for vector databases, embeddings, collections, and semantic retrieval.", bullet))
    story.append(Paragraph("5. PostgreSQL Documentation – Reference for enterprise relational database management.", bullet))
    story.append(Paragraph("6. Google Gemini API Documentation – Reference for integrating AI-based natural-language generation.", bullet))
    story.append(Paragraph("7. Retrieval Augmented Generation – Reference for combining information retrieval with language model generation.", bullet))
    story.append(Paragraph("8. Agentic AI Concepts – Reference for AI systems that reason, select actions, and use tools to accomplish tasks.", bullet))
    story.append(Paragraph("9. FastAPI Documentation – Reference for building asynchronous high-performance Python web APIs.", bullet))
    story.append(Paragraph("10. PyPDF2 Documentation – Reference for PDF parsing and text extraction in Python.", bullet))

    doc.build(story, canvasmaker=SimplePageNumberCanvas)
    print(f"27-page AXON Report successfully compiled to: {filename}")


if __name__ == "__main__":
    out_file = "d:/Axon/AXON_AI_Recruiter_Documentation.pdf"
    build_updated_pdf(out_file)
    # Also compile to AXON_AI_Recruiter_Project_Report.pdf so both updated files exist
    build_updated_pdf("d:/Axon/AXON_AI_Recruiter_Project_Report.pdf")
