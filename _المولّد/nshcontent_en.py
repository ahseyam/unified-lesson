# -*- coding: utf-8 -*-
"""English user guides for the Unified Lesson Platform — Ibn Khaldun Schools.

Five guides, one per role, illustrated with live screenshots of the platform's
**English** interface.

⛔ The wording here follows `i18n.EN` exactly. Where this file says "run sheet"
   and the platform button says "Print the run sheet", the two must agree — a
   guide that names a screen differently from the screen is worse than none.

⚠️ And the store is shared and Arabic: a teacher working in English writes into
   the same records their Arabic-speaking colleagues read. So the guide never
   promises a separate English platform — it is one platform, two interfaces.
"""
SITE = "https://ahseyam.github.io/unified-lesson/"

# ═════════ Shared with every role ═════════
COMMON_OPEN = [
    ("Open the link", SITE,
     "It runs on phone, laptop and tablet with nothing to install. Bookmark it — "
     "it is your single reference; do not rely on a copy someone sends you, or you "
     "will be working from yesterday's data."),
    ("Switch to English", "the EN button, top right",
     "Press it once and the choice is remembered on your device. Arabic is the "
     "default for everyone, so nothing changes for your Arabic-speaking colleagues. "
     "You may enter your own text in English or Arabic — both are kept as typed."),
    ("Choose your role", "one card per role",
     "Each role sees only what concerns it: its own buttons, screens and reports. "
     "You will not see what is not yours, and you cannot press a button that "
     "destroys someone else's work."),
    ("Enter your staff number", "you are identified by it, not by your name",
     "Names repeat and are spelled in different ways, so the same person appears "
     "twice in the reports. If your number is on the roster, your name and subject "
     "are filled in for you."),
]

CLOSE_HELP = ("Who to contact", [
    "If what concerns you does not appear, or something that is not yours does — "
    "contact the Planning and School Accreditation Department.",
    "If the page does not open at all — check the link above and your connection.",
])

SHEETS = {}


def sheet(key, role, title, who, why, steps, traps, faq):
    SHEETS[key] = dict(role=role, title=title, who=who, why=why,
                       steps=steps, traps=traps, faq=faq)


# ── 1) The teaching teacher ──
sheet(
    "teacher", "teacher",
    "Platform User Guide — Teaching Teacher",
    "For: every teacher with a lesson in the unified lesson schedule",
    "Your lesson in the external review starts from your cell in the schedule and "
    "ends with a documented score and one action you carry into your bridge card. "
    "This guide walks the whole way with you.",
    [
        ("Sign in with your role", "login_teacher",
         ["Choose the “Teaching teacher” card, then enter your staff number "
          "and your name appears.",
          "You are asked for your subject — it is the subject you teach, and your row "
          "in the schedule is found by it."], None),
        ("Find your cell in the schedule", "t_grid",
         ["The schedule is a matrix: rows are the week, the day and the visiting peer's "
          "subject; columns are the periods with their start times.",
          "Find your subject's row on the day your lesson runs, then go down to your "
          "period's column.",
          "Enter in the cell: your name, the strategy from the bank, the teaching "
          "approach, the class and the start time."],
         "Do not write in a cell that is not your subject or your period — whatever is "
         "entered there becomes its owner's lesson."),
        ("Start the lesson from its cell", "t_prep",
         ["Press “Start lesson” in the cell — the planning screen opens with "
          "its data already filled in.",
          "Complete the time map: warm-up, delivery, assessment and closure — their "
          "total is the lesson time.",
          "The priority-care time and the gifted time sit **inside** the delivery time; "
          "they are not added to it."],
         "Do not issue the plan before it is complete: once issued, peers and observers "
         "read it."),
        ("Read the run sheet", "t_run",
         ["A short sheet to read before you walk in: what you will deliver and what "
          "will be recorded on you.",
          "Print it or open it on your phone — your whole plan on one page."], None),
        ("Read your result and carry your action", "t_report",
         ["After the visit your score and its level appear, together with what each "
          "observer wrote about you.",
          "The “bridge action” is what you commit to in your next lesson — "
          "carry it into your card."],
         "The score locks on approval: after that the schedule, the plan and the "
         "observations cannot be changed."),
    ],
    [("My lesson does not appear under “My schedule”",
      "Your lesson is matched by your staff number. Check you signed in with your own "
      "number; if the cell was filled by someone else with your name spelled "
      "differently, ask them to use the “Register me here” button instead."),
     ("I cannot type in a particular cell",
      "Either it belongs to a subject that is not yours, or its lesson has been "
      "approved and locked.")],
    [("Can anyone see my plan before I issue it?",
      "No. Before you issue it, it is your draft alone."),
     ("My colleagues work in Arabic — do we see the same data?",
      "Yes. There is one shared store and one schedule; only the interface language "
      "differs. What you type stays exactly as you typed it.")],
)

# ── 2) The peer teacher ──
sheet(
    "peer", "peer",
    "Platform User Guide — Peer Teacher",
    "For: the teacher assigned to visit a colleague's unified lesson",
    "Your visit is neither an inspection nor a grade: you read your colleague's plan, "
    "attend the lesson, and leave with one action **you take for yourself**. Your "
    "sidebar is four steps in the order of your visit.",
    [
        ("Sign in with your role", "login",
         ["Choose the “Peer teacher” card and enter your staff number.",
          "Do not choose the “Teaching teacher” card — each role has its own "
          "screens."], None),
        ("Start from “My assigned visits”", "p_visits",
         ["The first thing you open: what has been assigned to you, with its time, its "
          "school, your colleague's name and the state of their plan.",
          "A counter in the sidebar tells you how many visits await your card."],
         "No visit appears until the school's academic deputy assigns it — ask them if "
         "it is late."),
        ("Read your colleague's plan before you go in", "p_read",
         ["The second stage is “Your colleague's plan”: a sheet with what will "
          "be delivered in the lesson.",
          "The time map, its stages and the strategy card — read before entering.",
          "Print it or open it on your phone so it is at hand during the lesson."], None),
        ("Fill the visit card", "p_card",
         ["The third stage is “Visit card”, and it is short: what happened, "
          "what helped you, and what you will apply.",
          "Fill it during the lesson or straight afterwards — most of what is written "
          "days later is lost.",
          "No observer rubric falls to you and no indicators are rated — that is not "
          "your part."], None),
        ("Carry your action", "p_result",
         ["The last stage is “Your own action”: a commitment to yourself, not "
          "a judgement on your colleague.",
          "One specific action that can be seen in your next lesson — that is what is "
          "followed up with you.",
          "The lesson result appears if the observers recorded it — to read, not to "
          "edit."], None),
    ],
    [("No visits are assigned to me",
      "Assignment is by the academic deputy, using staff numbers. Check you signed in "
      "with your own number."),
     ("I cannot find the entry grid",
      "Because you do not schedule anything. Your sidebar is four steps only, and that "
      "is deliberate.")],
    [("How many visits do I owe?",
      "Two per term — the counter in the sidebar says what is left."),
     ("Do I give my colleague a grade?",
      "No. Grading is for the observers; your card is description and benefit.")],
)

# ── 3) The school principal ──
sheet(
    "principal", "principal",
    "Platform User Guide — School Principal",
    "For: the school principal — whose scope is their own school alone",
    "The platform learns your school the first time you sign in and fixes it: you do "
    "not choose a complex or a stage on every screen, and you never see another "
    "school's schedule.",
    [
        ("Sign in and choose your school once", "login_prin",
         ["Choose the “School principal” card; you are asked for the sector, "
          "the complex and the school.",
          "It is then fixed for you — to change it, sign out and sign in again."], None),
        ("My school's schedule", "m_school",
         ["You see your school's lessons alone: who has a lesson scheduled, whose plan "
          "is complete and whose is not.",
          "You may type in any cell of your school — completeness is your "
          "responsibility.",
          "Above the schedule, a line says how many names on the roster still have no "
          "lesson recorded, and opens their list."], None),
        ("Observe the lesson", "m_obs",
         ["Your capacity on the card is filled from your role — you are not asked for "
          "it and it is not changed here.",
          "Complete the rubric during the lesson: the indicators with their scores, and "
          "the evidence with what you saw."],
         "What you write is attributed to you by name in the reports — write it "
         "precisely."),
        ("Approve the result and lock the lesson", "m_approve",
         ["Once the observations are complete, the score, its level and the bridge "
          "action appear.",
          "Approval locks the lesson: after it, the schedule, the plan and the "
          "observations cannot be changed."],
         "Do not approve a lesson no one has observed — unlocking requires a "
         "confirmation and is recorded in your name."),
        ("School dashboard and reports", "m_reports",
         ["Activation reports: who planned and who did not, who has been observed and "
          "who is waiting.",
          "Results reports by indicator, by teacher and by stage — exported as CSV for "
          "analysis."], None),
    ],
    [("I do not see “Where I visit — supervisor rota”",
      "Because you do not rotate between complexes. That is for the subject supervisor "
      "alone."),
     ("I do not see “Assign peers”",
      "Assignment belongs to the academic deputy — they are the one who sees it.")],
    [("Do I see the complex's other schools?",
      "No. Your scope is your school, and that is deliberate, to protect others' data."),
     ("I run two schools — how?",
      "Sign out and sign in with the other school; what you entered in the first is "
      "kept as it was.")],
)

# ── 4) The academic deputy ──
sheet(
    "deputy", "deputy",
    "Platform User Guide — Academic Deputy",
    "For: the academic deputy — who alone assigns peer teachers",
    "You have everything the principal has, and one thing more: **assigning peers**. "
    "Until you assign a visit, it does not appear in the peer teacher's account, and "
    "the peer card is never filled at all.",
    [
        ("Sign in and choose your school", "login_prin",
         ["Choose the “Academic deputy” card, then the sector, the complex and "
          "the school.",
          "It is fixed for you, exactly as it is for the principal."], None),
        ("Check the schedule is complete", "w_school",
         ["Before assigning: make sure the lessons carry their teachers' names in the "
          "cells.",
          "No assignment can be made on a cell with no teacher."], None),
        ("See who has not entered before you assign", "w_pending",
         ["Above the schedule a line reads: “N of the roster with no lesson "
          "yet” — with an “Open the roster” button.",
          "The list names them by name, staff number and subject, and prints or exports "
          "as CSV.",
          "Follow them up first: the schedule is not complete without them."],
         "The report measures the schedule against the teacher roster, not against "
         "itself — so whoever has not entered is named."),
        ("Assign peers by staff number", "w_assign",
         ["Open “Assign peers”: the list of your school's lessons, each with "
          "two peer slots.",
          "Type the staff number and the name appears from the roster to confirm — then "
          "it saves itself.",
          "The “Not yet assigned” filter shows you what is still without a "
          "peer."],
         "By number, not by name: names repeat, and a teacher would see someone else's "
         "visit."),
        ("Observe what concerns you", "w_obs",
         ["Your capacity on the card, “Academic deputy”, is filled from your "
          "role automatically.",
          "Observing and approving work exactly as they do for the principal."], None),
    ],
    [("I assigned it and it did not appear for the teacher",
      "Check they signed in with their own staff number — matching is on the number, "
      "not the name."),
     ("The number is not on the roster",
      "The number is accepted and saved, but with no name to confirm it. Ask the "
      "Planning and Accreditation Department to update the roster.")],
    [("How many peers per lesson?",
      "Two — two slots per lesson."),
     ("Does the principal assign as well?",
      "No. Assignment was given to you alone so a teacher is not assigned twice from "
      "two directions.")],
)

# ── 5) The subject supervisor ──
sheet(
    "supervisor", "supervisor",
    "Platform User Guide — Subject Supervisor",
    "For: the subject supervisor in educational supervision",
    "Your scope is a subject, not a school: you see your subject's lessons in the "
    "complex you visit each day, you observe them and approve their result. The "
    "subject and day filters narrow the schedule in a second.",
    [
        ("Sign in and choose your subject", "login_sup",
         ["Choose the “Subject supervisor” card, then your subject — your "
          "scope is known from it.",
          "If your number is on the roster, your subject is filled in for you."],
         "The subject is a taught subject, not a university qualification: someone "
         "qualified in chemistry appears under “Science”."),
        ("Narrow the schedule by subject and day", "s_grid",
         ["The “Subject you visit” and “Day” filters sit above the "
          "schedule.",
          "The “My visit today” button sets the week, the day and the complex "
          "from today's date in one press.",
          "Together they bring the rows down from hundreds to your lessons alone."], None),
        ("Review your week's plan", "s_plan",
         ["“My visit plan”: the days of the week and your subject's lessons in "
          "each one.",
          "The state of each plan comes with it — so you know before you set out."], None),
        ("Where I visit — supervisor rota", "s_rot",
         ["Which complex your subject team goes to on each day of each week.",
          "The order is your actual day: primary first, then intermediate, then "
          "secondary, by period times."], None),
        ("Observe and approve", "s_obs",
         ["Your capacity, “Subject supervisor”, is filled from your role "
          "automatically.",
          "Complete the rubric and the strategy card, then approve the result once the "
          "observations are complete."], None),
    ],
    [("I see many rows that do not concern me",
      "Set the “Subject” filter to your subject and “Day” to your "
      "visit day — or press “My visit today”."),
     ("I do not see “Assign peers”",
      "Assignment belongs to the academic deputy — it is not in your scope.")],
    [("I cover more than one subject — what do I do?",
      "The subject filter can be changed at any time from the same screen, without "
      "signing out."),
     ("Whose lessons do I approve?",
      "Those you observed yourself. Approval of a school's lessons is shared with its "
      "leadership.")],
)

# ── 6) Complex manager ──
# ⛔ الدَّوران الجديدان بقيا بلا دليلٍ عربيٍّ ولا إنجليزيّ. (١ أكتوبر ٢٠٢٦)
sheet(
    "cxmgr", "cxmgr",
    "Platform User Guide — Complex Manager",
    "For: the complex manager, who follows every school in their complex",
    "Your scope is a **whole complex**, not a single school, and you observe **any lesson "
    "in it**: you have your own independent form with its own score and your name, which no "
    "other evaluator overwrites. The adopted score for a lesson is the average of those who scored it.",
    [
        ("Sign in and choose your complex", "login_cx",
         ["Choose the “Complex manager” card, then the sector and the complex you manage.",
          "Your scope is then fixed to it: you neither see another complex nor edit in it."],
         "The scope is fixed at sign-in and cannot be switched from the screen — "
         "whoever switched it saw the whole system."),
        ("Read your complex's schedule", "c_grid",
         ["The schedule shows every lesson in your complex's schools: week, day, subject and teacher.",
          "You do not edit a cell in it — scheduling belongs to the teacher and their deputy."], None),
        ("Know what needs you first", "c_gap",
         ["The “Lessons with no subject supervisor” report lists what has no supervisor in your complex.",
          "Start with these — no one but you and those with you observes them."],
         "And you observe the rest as well: the form opens for you on any lesson in your complex."),
        ("Observe the lesson", "c_obs",
         ["Open the lesson; your capacity “Complex manager” is filled in from your role.",
          "Fill the form and the strategy card, then approve the result."],
         "Your form carries your name alone — and anyone who scored it with you appears beside you."),
        ("Follow your complex through the reports", "c_reports",
         ["Your complex's reports: teachers and their results · subjects · the weakest "
          "indicators · and missing entries.",
          "All of them are confined to your complex — so what you see concerns you."], None),
    ],
    [("A lesson I can see will not open its form",
      "It is outside your complex — observing belongs to whoever has the lesson in scope. "
      "Anything inside your complex does open for you."),
     ("I cannot edit a cell in the schedule",
      "Scheduling belongs to the teacher giving the lesson and their deputy; you follow and observe.")],
    [("My complex has both boys' and girls' schools?",
      "Each sector has its own platform and its own store — you sign in to each separately."),
     ("Who approves a result I recorded?",
      "You do — whoever observes approves. If someone scored it with you, the adopted score "
      "is the average of both.")],
)

# ── 7) Internal evaluation follow-up team ──
sheet(
    "intqa", "intqa",
    "Platform User Guide — Internal Evaluation Follow-up Team",
    "For: two members of the central administration — their scope is the whole system",
    "Your scope is the **whole system**: both sectors, the complexes and the schools. You make "
    "sure no lesson is left without an observer, **and you observe too**: each of you has an "
    "independent form with its own score and name. The adopted score for a lesson is the "
    "average of those who scored it.",
    [
        ("Sign in with your role", "login_iq",
         ["Choose the “Internal evaluation follow-up team” card — it is the last of them.",
          "You are asked for neither a subject nor a complex: your scope is the whole system."], None),
        ("Read the schedule", "q_grid",
         ["You see every lesson in the system: both sectors, the complexes and the schools.",
          "No cell is edited — following up is reading, not writing."], None),
        ("Follow what has no supervisor", "q_gap",
         ["The “Lessons with no subject supervisor” report is your first task: who observes "
          "them, and whether they have been observed.",
          "If one remains with no observer, you alert the deputy or the complex manager."], None),
        ("Observe the lesson", "q_note",
         ["Open the lesson under “Lesson observation”; your capacity is filled in from your role.",
          "Fill the form and the strategy card — each of you has their own form."],
         "Your form carries your name, and no other observer overwrites it — "
         "their score appears beside yours."),
    ],
    [("Where is the form?",
      "Under “Lesson observation” once the lesson is open — and a bar at its head moves you "
      "between the teacher's prep, the form and the strategy card."),
     ("I see every lesson in the system — is that right?",
      "Yes: your scope is the whole system, unlike the complex manager who is confined to theirs.")],
    [("Does our score count towards the lesson average?",
      "Yes — the adopted score is the average of everyone who scored, so yours is part of it."),
     ("How do we know what is late?",
      "The “Missing entries” report measures the schedule against the teacher roster and "
      "names whoever has not registered yet.")],
)

ORDER = ["teacher", "peer", "principal", "deputy", "supervisor", "cxmgr", "intqa"]
