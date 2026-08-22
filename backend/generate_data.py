"""backend/generate_data.py — deterministic, seeded, fully fictional dataset.

Produces the synthetic ATHA network per CONTEXT.md "Dataset spec (synthetic v1)":
48 students, 12 alumni, 12 enterprises, 20 topics, 8 events (3 past with
highlights, 5 upcoming incl. the single real entity ATHA 001), 2 schools.

Topic clusters are shaped so the four acceptance fixtures retrieve distinct,
plausible matches:
  A: cybersecurity / data science / talent acquisition      (enterprise recruiter)
  B: networking / entrepreneurship / events                 (society president)
  C: mentoring / wellbeing / community                      (wellbeing advisor)
  D: data quality / research methodology / network analysis (data lead)

Run: python generate_data.py   -> writes data/*.json next to the repo backend/.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

SEED = 20260824
DATA_DIR = Path(__file__).resolve().parents[1] / "data"

SCHOOLS = ["University of Warwick", "Warwick Business School"]

# --- Topic vocabulary: 4 fixture clusters x 3 + 8 filler = 20 ---------------
CLUSTERS = {
    "A": ["cybersecurity", "data science", "talent acquisition"],
    "B": ["networking", "entrepreneurship", "events"],
    "C": ["mentoring", "wellbeing", "community"],
    "D": ["data quality", "research methodology", "network analysis"],
}
FILLER_TOPICS = [
    "artificial intelligence", "fintech", "sustainability", "consulting",
    "leadership", "marketing analytics", "product management", "career development",
]
ALL_TOPICS = [t for topics in CLUSTERS.values() for t in topics] + FILLER_TOPICS
assert len(ALL_TOPICS) == 20

# --- Fictional name pools ----------------------------------------------------
FIRST_NAMES = [
    "Amelia", "Oliver", "Priya", "Noah", "Zara", "Ethan", "Ingrid", "Lucas",
    "Mei", "Tomas", "Aisha", "Felix", "Grace", "Hassan", "Isla", "Jakub",
    "Keira", "Leo", "Marta", "Nathan", "Olive", "Patrick", "Quinn", "Rosa",
    "Sam", "Tara", "Umar", "Vera", "William", "Yasmin", "Adrian", "Bianca",
    "Callum", "Dana", "Emil", "Farah", "Gareth", "Hana", "Ivan", "Julia",
    "Kian", "Lena", "Marcus", "Nadia", "Oscar", "Piper", "Ravi", "Sofia",
    "Theo", "Una", "Victor", "Wren", "Yusuf", "Elena", "Ben", "Chloe",
    "Dev", "Esme", "Finn", "Georgia",
]
LAST_NAMES = [
    "Ackroyd", "Barnes", "Calloway", "Drewitt", "Ellison", "Fairbank",
    "Gosling", "Hartley", "Iverson", "Jepson", "Kirkland", "Lomax",
    "Mercer", "Naylor", "Ormond", "Pemberton", "Quigley", "Rowan",
    "Sedgwick", "Thornhill", "Underwood", "Vance", "Whitfield", "Yardley",
    "Ashcroft", "Bellweather", "Cresswell", "Dunmore", "Everly", "Foss",
]

UW_PROGRAMS = [
    "BSc Computer Science", "BSc Data Analytics", "BSc Business Management",
    "BA Economics", "BSc Psychology", "BSc Mathematics", "BA Sociology",
]
WBS_PROGRAMS = [
    "MSc Management", "MSc Business Analytics", "MSc Marketing & Strategy",
    "MSc Finance", "MBA",
]

SKILLS = {
    "A": ["Python", "SQL", "threat modelling", "penetration testing",
          "people analytics", "machine learning", "security operations"],
    "B": ["event planning", "community building", "pitching", "social media",
          "fundraising", "public speaking"],
    "C": ["active listening", "peer coaching", "programme coordination",
          "facilitation", "signposting", "storytelling"],
    "D": ["data auditing", "survey design", "graph modelling", "statistics",
          "documentation", "ETL"],
    "F": ["research", "communication", "analysis", "project work"],
}

BIOS = {
    "A": [
        "Focused on cybersecurity and applied data science, {first} wants to help "
        "organisations close the security skills gap through smarter talent acquisition.",
        "{first} studies how data science strengthens cybersecurity defences and how "
        "employers can use it for better talent acquisition.",
        "From threat modelling to people analytics, {first} connects cybersecurity, "
        "data science and talent acquisition.",
    ],
    "B": [
        "{first} thrives on networking, loves the energy of live events, and is "
        "building practical entrepreneurship skills.",
        "An aspiring founder, {first} organises networking events and learns "
        "entrepreneurship by doing.",
        "{first} believes great ventures start with great events and even better "
        "networking, and wants to grow the entrepreneurship scene on campus.",
    ],
    "C": [
        "{first} cares deeply about student wellbeing, peer mentoring, and building "
        "inclusive community spaces.",
        "A trained peer mentor, {first} champions wellbeing and keeps community at "
        "the heart of everything they do.",
        "{first} is exploring how mentoring relationships strengthen community and "
        "wellbeing on campus.",
    ],
    "D": [
        "{first} obsesses over data quality, rigorous research methodology, and "
        "network analysis of complex systems.",
        "{first} applies research methodology and network analysis to measure and "
        "improve data quality.",
        "Curious about how networks behave, {first} pairs research methodology with "
        "network analysis and careful data quality work.",
    ],
    "F": [
        "{first} is exploring {t1} and {t2} and looking for where they connect.",
        "Keen to turn curiosity about {t1} into real projects, {first} also enjoys {t2}.",
    ],
}

ALUMNI_ROLES = {
    "A": ["Security Consultant", "Data Scientist", "Talent Acquisition Lead"],
    "B": ["Founder", "Community Manager", "Events Producer"],
    "C": ["Wellbeing Programme Manager", "Mentoring Coordinator", "Community Lead"],
    "D": ["Data Governance Analyst", "Research Lead", "Network Analyst"],
}

ENTERPRISES = [
    # Cluster A — cybersecurity / data science / talent acquisition
    {"id": "ent-01", "name": "Northbridge Cybernetics", "sector": "Cybersecurity",
     "size": "201-1000", "hq": "Manchester", "cluster": "A",
     "description": "Managed security services and threat intelligence for UK "
                    "finance and retail, with a growing graduate academy.",
     "contact": {"name": "Priya Shah", "role": "Head of Talent",
                 "email": "priya.shah@northbridge.example.com"}},
    {"id": "ent-02", "name": "Quantia Analytics", "sector": "Data & Analytics",
     "size": "51-200", "hq": "Leeds", "cluster": "A",
     "description": "Decision intelligence consultancy pairing data science with "
                    "security-aware engineering for regulated industries.",
     "contact": {"name": "Daniel Okafor", "role": "Early Careers Manager",
                 "email": "daniel.okafor@quantia.example.com"}},
    {"id": "ent-03", "name": "TalentArc Partners", "sector": "HR Technology",
     "size": "11-50", "hq": "Birmingham", "cluster": "A",
     "description": "Talent acquisition platform using data science to match "
                    "technical candidates — including cybersecurity specialists — to employers.",
     "contact": {"name": "Ruth Ellison", "role": "Partnerships Director",
                 "email": "ruth.ellison@talentarc.example.com"}},
    # Cluster B — networking / entrepreneurship / events
    {"id": "ent-04", "name": "Harbourlight Ventures", "sector": "Venture Capital",
     "size": "11-50", "hq": "London", "cluster": "B",
     "description": "Pre-seed fund backing student and alumni founders, known for "
                    "its networking salons and demo events.",
     "contact": {"name": "Marcus Cole", "role": "Platform Lead",
                 "email": "marcus.cole@harbourlight.example.com"}},
    {"id": "ent-05", "name": "Mosaic Events Collective", "sector": "Events",
     "size": "11-50", "hq": "Coventry", "cluster": "B",
     "description": "Event production collective designing networking formats that "
                    "help founders and students actually meet.",
     "contact": {"name": "Sofia Reyes", "role": "Managing Producer",
                 "email": "sofia.reyes@mosaic.example.com"}},
    {"id": "ent-06", "name": "Foundry Lane Studio", "sector": "Startup Studio",
     "size": "51-200", "hq": "Sheffield", "cluster": "B",
     "description": "Venture studio running entrepreneurship programmes and "
                    "community networking for early-stage teams in the Midlands.",
     "contact": {"name": "Tom Greaves", "role": "Programme Director",
                 "email": "tom.greaves@foundrylane.example.com"}},
    # Cluster C — mentoring / wellbeing / community
    {"id": "ent-07", "name": "Brightwell Trust", "sector": "Wellbeing Charity",
     "size": "51-200", "hq": "Bristol", "cluster": "C",
     "description": "Charity delivering wellbeing programmes and peer-support "
                    "training across UK universities.",
     "contact": {"name": "Hannah Dove", "role": "University Partnerships Lead",
                 "email": "hannah.dove@brightwell.example.org"}},
    {"id": "ent-08", "name": "Kindred Community CIC", "sector": "Community Interest Company",
     "size": "11-50", "hq": "Nottingham", "cluster": "C",
     "description": "Community interest company building intergenerational mentoring "
                    "and community wellbeing projects with student volunteers.",
     "contact": {"name": "Levi Osei", "role": "Community Director",
                 "email": "levi.osei@kindred.example.org"}},
    {"id": "ent-09", "name": "Anchor Mentoring Network", "sector": "Education & Mentoring",
     "size": "11-50", "hq": "Cardiff", "cluster": "C",
     "description": "Alumni mentoring network pairing students with professional "
                    "mentors, with a strong focus on wellbeing and community.",
     "contact": {"name": "Carys Morgan", "role": "Head of Mentoring",
                 "email": "carys.morgan@anchor.example.org"}},
    # Cluster D — data quality / research methodology / network analysis
    {"id": "ent-10", "name": "Clearmetrics Data Group", "sector": "Data Governance",
     "size": "201-1000", "hq": "London", "cluster": "D",
     "description": "Data governance consultancy helping enterprises measure data "
                    "quality, define methodology standards and audit data pipelines.",
     "contact": {"name": "Ingrid Bergstrom", "role": "Head of Data Practice",
                 "email": "ingrid.bergstrom@clearmetrics.example.com"}},
    {"id": "ent-11", "name": "Methodica Research Labs", "sector": "Research Services",
     "size": "51-200", "hq": "Edinburgh", "cluster": "D",
     "description": "Applied research lab offering research methodology review, "
                    "survey design and data quality assurance for public-sector studies.",
     "contact": {"name": "Alan Whitaker", "role": "Research Director",
                 "email": "alan.whitaker@methodica.example.com"}},
    {"id": "ent-12", "name": "Netform Analytics", "sector": "Network Analytics",
     "size": "11-50", "hq": "Manchester", "cluster": "D",
     "description": "Boutique analytics firm specialising in network analysis of "
                    "organisational data, with strict data quality controls.",
     "contact": {"name": "Maya Lindqvist", "role": "Chief Analyst",
                 "email": "maya.lindqvist@netform.example.com"}},
]

EVENTS = [
    # Past events (with highlights)
    {"id": "evt-01", "name": "Midlands Cyber Careers Evening", "date": "2026-03-12",
     "kind": "past", "location": "University of Warwick",
     "highlights": [
         "Panel: breaking into security without a traditional degree",
         "Live capture-the-flag demo with Northbridge engineers",
         "Over forty one-to-one CV reviews booked on the night",
     ]},
    {"id": "evt-02", "name": "Spring Startup Pitch Night", "date": "2026-04-02",
     "kind": "past", "location": "Warwick Business School",
     "highlights": [
         "Nine student ventures pitched to a live audience",
         "Audience choice award won by a campus resale platform",
         "Three founders secured follow-up investor meetings",
     ]},
    {"id": "evt-03", "name": "Peer Mentoring Kickoff Day", "date": "2026-02-19",
     "kind": "past", "location": "University of Warwick",
     "highlights": [
         "Sixty new mentor-mentee pairs matched in one afternoon",
         "Workshop: listening skills for first-time mentors",
         "Alumni fireside chat on staying well in demanding careers",
     ]},
    # Upcoming events — evt-04 is the SINGLE REAL entity in the dataset
    {"id": "evt-04", "name": "ATHA 001", "date": "2026-Q4",
     "kind": "upcoming", "location": "Warwick Business School", "highlights": []},
    {"id": "evt-05", "name": "Autumn Founders Roundtable", "date": "2026-09-24",
     "kind": "upcoming", "location": "Warwick Business School", "highlights": []},
    {"id": "evt-06", "name": "Wellbeing & Community Fair", "date": "2026-10-08",
     "kind": "upcoming", "location": "University of Warwick", "highlights": []},
    {"id": "evt-07", "name": "Data Quality in Practice", "date": "2026-11-05",
     "kind": "upcoming", "location": "University of Warwick", "highlights": []},
    {"id": "evt-08", "name": "Tech Talent Networking Mixer", "date": "2026-09-30",
     "kind": "upcoming", "location": "University of Warwick", "highlights": []},
]

# Enterprise -> events sponsored (deterministic)
SPONSORS = {
    "ent-01": ["evt-01", "evt-08", "evt-04"],
    "ent-02": ["evt-01"],
    "ent-03": ["evt-08"],
    "ent-04": ["evt-02", "evt-05", "evt-04"],
    "ent-05": ["evt-02"],
    "ent-06": ["evt-05"],
    "ent-07": ["evt-03", "evt-06"],
    "ent-08": ["evt-06"],
    "ent-09": ["evt-03"],
    "ent-10": ["evt-07", "evt-04"],
    "ent-11": ["evt-07"],
    "ent-12": ["evt-07"],
}


def unique_names(rng: random.Random, count: int) -> list[str]:
    names: set[str] = set()
    while len(names) < count:
        names.add(f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}")
    return sorted(names)


def make_students(rng: random.Random) -> list[dict]:
    """48 students: 12xA, 12xB, 12xC, 8xD, 4x filler."""
    plan = (["A"] * 12) + (["B"] * 12) + (["C"] * 12) + (["D"] * 8) + (["F"] * 4)
    assert len(plan) == 48
    names = unique_names(rng, 48)
    mentors = [f"alu-{i:02d}" for i in range(1, 5)]  # cluster-C alumni
    students = []
    for i, (name, cluster) in enumerate(zip(names, plan), start=1):
        first = name.split()[0]
        if cluster == "F":
            t1, t2 = rng.sample(FILLER_TOPICS, 2)
            interests = [t1, t2]
            bio = rng.choice(BIOS["F"]).format(first=first, t1=t1, t2=t2)
        else:
            interests = list(CLUSTERS[cluster])
            if rng.random() < 0.4:
                interests.append(rng.choice(FILLER_TOPICS))
            bio = rng.choice(BIOS[cluster]).format(first=first)
        wbs = rng.random() < 0.3
        school = SCHOOLS[1] if wbs else SCHOOLS[0]
        program = rng.choice(WBS_PROGRAMS if wbs else UW_PROGRAMS)
        year = rng.choice(["2025 cohort", "2026 cohort"]) if wbs else rng.choice(
            ["Year 1", "Year 2", "Year 3"])
        student = {
            "id": f"stu-{i:02d}",
            "name": name,
            "role": "student",
            "year_or_cohort": year,
            "program_or_role": program,
            "school": school,
            "skills": rng.sample(SKILLS[cluster], k=3),
            "interests": interests,
            "bio": bio,
            "contact_email": f"{first.lower()}.{name.split()[1].lower()}"
                             f"{i:02d}@warwick.example.ac.uk",
        }
        if cluster == "C":
            student["mentor_id"] = mentors[(i - 1) % len(mentors)]
        students.append(student)
    # Two filler students also join the mentoring scheme (story texture)
    for extra in (46, 47):
        students[extra]["mentor_id"] = mentors[(extra - 1) % len(mentors)]
    return students


ATTENDED_PLAN = {
    "evt-01": ("A", ["alu-05", "alu-06"]),
    "evt-02": ("B", ["alu-08", "alu-09"]),
    "evt-03": ("C", ["alu-01", "alu-02"]),
}


def assign_attended(students: list[dict], alumni: list[dict]) -> None:
    by_cluster: dict[str, list[str]] = {"A": [], "B": [], "C": [], "D": [], "F": []}
    for s in students:
        c = next((k for k, v in CLUSTERS.items() if set(v) <= set(s["interests"])), "F")
        by_cluster[c].append(s["id"])
    for evt_id, (cluster, alumni_ids) in ATTENDED_PLAN.items():
        for pid in by_cluster[cluster] + by_cluster["F"]:
            stu = next(s for s in students if s["id"] == pid)
            stu.setdefault("attended", []).append(evt_id)
        for aid in alumni_ids:
            alu = next(a for a in alumni if a["id"] == aid)
            alu.setdefault("attended", []).append(evt_id)


def make_alumni(rng: random.Random) -> list[dict]:
    """12 alumni: 4xC mentors, 3xA, 3xB, 2xD."""
    plan = (["C"] * 4) + (["A"] * 3) + (["B"] * 3) + (["D"] * 2)
    assert len(plan) == 12
    names = unique_names(rng, 12)
    alumni = []
    role_counters: dict[str, int] = {}
    for i, (name, cluster) in enumerate(zip(names, plan), start=1):
        first = name.split()[0]
        idx = role_counters.get(cluster, 0)
        role_counters[cluster] = idx + 1
        job = ALUMNI_ROLES[cluster][idx % len(ALUMNI_ROLES[cluster])]
        wbs = rng.random() < 0.4
        alumni.append({
            "id": f"alu-{i:02d}",
            "name": name,
            "role": "alumnus",
            "year_or_cohort": f"Class of {2015 + ((i * 7) % 10)}",
            "program_or_role": job,
            "school": SCHOOLS[1] if wbs else SCHOOLS[0],
            "skills": rng.sample(SKILLS[cluster], k=3),
            "interests": list(CLUSTERS[cluster]),
            "bio": rng.choice(BIOS[cluster]).format(first=first),
            "contact_email": f"{first.lower()}.{name.split()[1].lower()}"
                             f"@example.com",
        })
    return alumni


def main() -> None:
    rng = random.Random(SEED)
    students = make_students(rng)
    alumni = make_alumni(rng)
    assign_attended(students, alumni)

    enterprises = []
    for e in ENTERPRISES:
        enterprises.append({
            "id": e["id"], "name": e["name"], "sector": e["sector"],
            "size": e["size"], "hq": e["hq"], "description": e["description"],
            "contact": e["contact"],
            "seeks": list(CLUSTERS[e["cluster"]]),
            "sponsors": SPONSORS[e["id"]],
        })

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    files = {
        "students.json": {"students": students},
        "alumni.json": {"alumni": alumni},
        "enterprises.json": {"enterprises": enterprises},
        "topics.json": {"topics": [{"name": t} for t in ALL_TOPICS]},
        "events.json": {"events": EVENTS},
        "schools.json": {"schools": [{"name": s} for s in SCHOOLS]},
    }
    for filename, payload in files.items():
        path = DATA_DIR / filename
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                        encoding="utf-8")
        print(f"wrote {path}")
    print(f"counts: students={len(students)} alumni={len(alumni)} "
          f"enterprises={len(enterprises)} topics={len(ALL_TOPICS)} "
          f"events={len(EVENTS)} schools={len(SCHOOLS)}")
    print(f"mentored_by pairs={sum(1 for s in students if 'mentor_id' in s)}, "
          f"attended pairs={sum(len(s.get('attended', [])) for s in students)}, "
          f"sponsors pairs={sum(len(e['sponsors']) for e in enterprises)}")


if __name__ == "__main__":
    main()
