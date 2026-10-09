# AXON Portal

AI Recruiter & Adaptive Technical Assessment Platform.

## Features
- **Proctored MCQ Assessment Mode**: Replaces conversational Graded Mode. Delivers 20 randomized, option-shuffled technical questions with real-time focus & cursor anti-cheat strike enforcement (disqualification upon 3 strikes) and instantaneous scorecards.
- **Bulk Upload**:
  - Bulk Student Roster upload via PDF or Excel (`.xlsx`, `.xls`) with strict 50 MiB limit and 300 student cap.
  - Bulk MCQ Question Bank upload via PDF or Excel with automated fallback to external answer lookups (`https://api.greeksforgeeks.com/answers`).
- **Institutional Oversight & Cleanup**:
  - Dedicated **MCQ Results** tab in Directory Oversight with pass/fail ratios, average percentages, and candidate strike tracking.
  - HOD single-click purge inactive students retaining exclusively canonical student `11234003` (`student@123`).
- **Complete Offline Engine**: 100% free of external API key dependencies.

For detailed documentation on the MCQ architecture, file layouts, and API contract, see [docs/mcq.md](docs/mcq.md).