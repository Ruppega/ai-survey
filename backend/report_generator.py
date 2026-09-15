import io
import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)


# =========================================================
# FILE LOCATION
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_FILE = os.path.join(BASE_DIR, "memory.json")


# =========================================================
# TEXT HELPERS
# =========================================================

def safe_text(value, default="Not available"):
    if value is None:
        return default

    text = str(value).strip()

    return text if text else default


def escape_html(value):
    text = safe_text(value)
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace('"', "&quot;")
    return text


def clean_filename(value):
    value = safe_text(value, "research")
    value = re.sub(r"[^A-Za-z0-9_-]+", "_", value)
    return value.strip("_") or "research"


# =========================================================
# ADOPTION SCORE
# =========================================================

def calculate_adoption_score(persona):
    try:
        rating = float(persona.get("rating", 0))
    except (ValueError, TypeError):
        rating = 0

    rating = max(0, min(rating, 5))

    decision = str(
        persona.get("buyDecision", "")
    ).strip().lower()

    score = (rating / 5) * 60

    if decision == "yes":
        score += 40

    return round(score, 1)


def adoption_category(score):
    if score >= 70:
        return "High Adoption"
    if score >= 40:
        return "Moderate Adoption"
    return "Low Adoption"


# =========================================================
# MEMORY
# =========================================================

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}

    try:
        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        return data if isinstance(data, dict) else {}

    except (OSError, json.JSONDecodeError):
        return {}


def get_interview_data():
    memory = load_memory()

    individual = []
    all_persona = []

    personas_memory = memory.get("personas", {})

    if isinstance(personas_memory, dict):

        for persona_id, record in personas_memory.items():

            if not isinstance(record, dict):
                continue

            conversation = record.get(
                "conversation",
                []
            )

            if not isinstance(conversation, list):
                continue

            for item in conversation:

                if not isinstance(item, dict):
                    continue

                mode = str(
                    item.get("mode", "individual")
                ).lower()

                if mode != "all":
                    question = safe_text(
                        item.get("question"),
                        ""
                    )

                    response = safe_text(
                        item.get("response"),
                        ""
                    )

                    if question and response:
                        individual.append({
                            "personaId": str(persona_id),
                            "question": question,
                            "response": response,
                            "timestamp": item.get(
                                "timestamp",
                                ""
                            )
                        })

    global_interviews = memory.get(
        "allPersonaInterviews",
        []
    )

    if isinstance(global_interviews, list):

        for item in global_interviews:

            if not isinstance(item, dict):
                continue

            question = safe_text(
                item.get("question"),
                ""
            )

            responses = item.get(
                "responses",
                []
            )

            if question:
                all_persona.append({
                    "question": question,
                    "responses": responses
                    if isinstance(responses, list)
                    else [],
                    "timestamp": item.get(
                        "timestamp",
                        ""
                    )
                })

    return individual, all_persona


# =========================================================
# THEME EXTRACTION
# =========================================================

THEME_KEYWORDS = {
    "Price & Value": [
        "price",
        "cost",
        "cheap",
        "expensive",
        "affordable",
        "value",
        "money",
        "budget"
    ],
    "Design": [
        "design",
        "look",
        "style",
        "appearance",
        "color",
        "colour",
        "size",
        "shape"
    ],
    "Quality": [
        "quality",
        "durable",
        "durability",
        "strong",
        "material",
        "reliable",
        "performance"
    ],
    "Convenience": [
        "easy",
        "convenient",
        "portable",
        "comfortable",
        "simple",
        "clean",
        "cleaning",
        "carry",
        "use"
    ],
    "Features": [
        "feature",
        "features",
        "function",
        "option",
        "battery",
        "storage",
        "capacity",
        "compartment",
        "technology"
    ],
    "Problems & Concerns": [
        "problem",
        "issue",
        "concern",
        "difficult",
        "hard",
        "dislike",
        "negative",
        "improve",
        "improvement"
    ]
}


def find_themes(texts):
    if not texts:
        return []

    combined = " ".join(
        str(text).lower()
        for text in texts
        if text
    )

    theme_counts = Counter()

    for theme, keywords in THEME_KEYWORDS.items():

        count = 0

        for keyword in keywords:
            count += len(
                re.findall(
                    rf"\b{re.escape(keyword)}\b",
                    combined
                )
            )

        if count > 0:
            theme_counts[theme] = count

    return [
        theme
        for theme, _ in theme_counts.most_common()
    ]


# =========================================================
# RESPONSE SUMMARY
# =========================================================

def summarize_responses(personas):
    reasons = []

    for persona in personas:

        if not isinstance(persona, dict):
            continue

        reason = str(
            persona.get("reason", "")
        ).strip()

        if reason:
            reasons.append(reason)

    if not reasons:
        return {
            "direction": "No persona opinions were provided.",
            "themes": [],
            "concerns": [],
        }

    positive_words = [
        "good",
        "great",
        "useful",
        "helpful",
        "convenient",
        "like",
        "love",
        "easy",
        "affordable",
        "quality",
        "recommend"
    ]

    negative_words = [
        "expensive",
        "bad",
        "difficult",
        "hard",
        "problem",
        "issue",
        "concern",
        "dislike",
        "poor",
        "improve"
    ]

    positive_score = 0
    negative_score = 0

    for reason in reasons:

        text = reason.lower()

        positive_score += sum(
            text.count(word)
            for word in positive_words
        )

        negative_score += sum(
            text.count(word)
            for word in negative_words
        )

    if positive_score > negative_score:
        direction = "Overall responses lean positive."
    elif negative_score > positive_score:
        direction = "Overall responses contain more negative concerns."
    else:
        direction = "Overall responses are mixed or balanced."

    themes = find_themes(reasons)

    concern_keywords = [
        "expensive",
        "problem",
        "issue",
        "concern",
        "difficult",
        "hard",
        "improve",
        "dislike"
    ]

    concern_reasons = [
        reason
        for reason in reasons
        if any(
            keyword in reason.lower()
            for keyword in concern_keywords
        )
    ]

    return {
        "direction": direction,
        "themes": themes[:6],
        "concerns": concern_reasons[:5]
    }


# =========================================================
# PDF STYLES
# =========================================================

def build_styles():
    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontSize=24,
            leading=29,
            alignment=TA_CENTER,
            spaceAfter=14
        )
    )

    styles.add(
        ParagraphStyle(
            name="ReportSubtitle",
            parent=styles["Normal"],
            fontSize=11,
            leading=16,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#555555"),
            spaceAfter=8
        )
    )

    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            parent=styles["Heading2"],
            fontSize=16,
            leading=20,
            spaceBefore=8,
            spaceAfter=10
        )
    )

    styles.add(
        ParagraphStyle(
            name="Small",
            parent=styles["Normal"],
            fontSize=8.5,
            leading=11
        )
    )

    styles.add(
        ParagraphStyle(
            name="BodyReport",
            parent=styles["BodyText"],
            fontSize=9.5,
            leading=14,
            spaceAfter=6
        )
    )

    styles.add(
        ParagraphStyle(
            name="MetricValue",
            parent=styles["Normal"],
            fontSize=17,
            leading=20,
            alignment=TA_CENTER
        )
    )

    styles.add(
        ParagraphStyle(
            name="MetricLabel",
            parent=styles["Normal"],
            fontSize=8.5,
            leading=11,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#555555")
        )
    )

    return styles


# =========================================================
# TABLE HELPERS
# =========================================================

def make_table(data, widths=None, header=True):
    table = Table(
        data,
        colWidths=widths,
        repeatRows=1 if header else 0,
        hAlign="LEFT"
    )

    style = [
        (
            "GRID",
            (0, 0),
            (-1, -1),
            0.5,
            colors.HexColor("#D1D5DB")
        ),
        (
            "VALIGN",
            (0, 0),
            (-1, -1),
            "TOP"
        ),
        (
            "LEFTPADDING",
            (0, 0),
            (-1, -1),
            6
        ),
        (
            "RIGHTPADDING",
            (0, 0),
            (-1, -1),
            6
        ),
        (
            "TOPPADDING",
            (0, 0),
            (-1, -1),
            5
        ),
        (
            "BOTTOMPADDING",
            (0, 0),
            (-1, -1),
            5
        ),
    ]

    if header:
        style.extend([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#F3F4F6")
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
        ])

    table.setStyle(TableStyle(style))

    return table


def metric_card(label, value, styles):
    return Table(
        [[
            Paragraph(
                escape_html(value),
                styles["MetricValue"]
            )
        ], [
            Paragraph(
                escape_html(label),
                styles["MetricLabel"]
            )
        ]],
        colWidths=[39 * mm],
        rowHeights=[12 * mm, 8 * mm],
        style=TableStyle([
            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.7,
                colors.HexColor("#D1D5DB")
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                4
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                4
            )
        ])
    )


# =========================================================
# MAIN REPORT
# =========================================================

def generate_research_report(
    product="",
    description="",
    gender="Both",
    age="",
    objective="",
    personas=None,
    insights=None
):
    personas = personas or []
    insights = insights if isinstance(insights, dict) else {}

    styles = build_styles()

    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title=f"{safe_text(product, 'Research')} Research Report",
        author="Persona Research System"
    )

    story = []

    # -----------------------------------------------------
    # CALCULATIONS
    # -----------------------------------------------------

    total = len(personas)

    preferred = 0
    not_preferred = 0
    ratings = []
    adoption_scores = []

    for persona in personas:

        if not isinstance(persona, dict):
            continue

        decision = str(
            persona.get("buyDecision", "")
        ).strip().lower()

        if decision == "yes":
            preferred += 1
        elif decision == "no":
            not_preferred += 1

        try:
            rating = float(
                persona.get("rating", 0)
            )

            if 1 <= rating <= 5:
                ratings.append(rating)

        except (ValueError, TypeError):
            pass

        score = calculate_adoption_score(persona)

        adoption_scores.append(score)

    # Treat missing decision values as not preferred
    if preferred + not_preferred < total:
        not_preferred = total - preferred

    would_use_percentage = (
        round((preferred / total) * 100, 1)
        if total
        else 0
    )

    average_rating = (
        round(sum(ratings) / len(ratings), 1)
        if ratings
        else 0
    )

    overall_adoption = (
        round(sum(adoption_scores) / len(adoption_scores), 1)
        if adoption_scores
        else 0
    )

    if overall_adoption >= 75:
        validation = "Strong Validation"
    elif overall_adoption >= 50:
        validation = "Moderate Validation"
    else:
        validation = "Needs Improvement"

    response_summary = summarize_responses(
        personas
    )

    individual_interviews, all_persona_interviews = (
        get_interview_data()
    )

    # -----------------------------------------------------
    # TITLE
    # -----------------------------------------------------

    story.append(
        Spacer(1, 25 * mm)
    )

    story.append(
        Paragraph(
            escape_html(
                product or "Persona Research Report"
            ),
            styles["ReportTitle"]
        )
    )

    story.append(
        Paragraph(
            "Synthetic Persona Research Report",
            styles["ReportSubtitle"]
        )
    )

    story.append(
        Paragraph(
            f"Generated on {datetime.now().strftime('%d %B %Y, %I:%M %p')}",
            styles["ReportSubtitle"]
        )
    )

    story.append(
        Spacer(1, 20 * mm)
    )

    story.append(
        Paragraph(
            "This report summarizes survey responses, persona opinions, "
            "adoption results and interview-response findings. "
            "Full interview transcripts are intentionally excluded.",
            styles["BodyReport"]
        )
    )

    story.append(PageBreak())

    # -----------------------------------------------------
    # 1. RESEARCH OVERVIEW
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "1. Research Overview",
            styles["SectionHeading"]
        )
    )

    overview_data = [
        [
            Paragraph("<b>Research Field</b>", styles["Small"]),
            Paragraph("<b>Details</b>", styles["Small"])
        ],
        [
            Paragraph("Product", styles["Small"]),
            Paragraph(
                escape_html(product),
                styles["Small"]
            )
        ],
        [
            Paragraph("Description", styles["Small"]),
            Paragraph(
                escape_html(description),
                styles["Small"]
            )
        ],
        [
            Paragraph("Research Objective", styles["Small"]),
            Paragraph(
                escape_html(objective),
                styles["Small"]
            )
        ],
        [
            Paragraph("Target Age", styles["Small"]),
            Paragraph(
                escape_html(age),
                styles["Small"]
            )
        ],
        [
            Paragraph("Gender", styles["Small"]),
            Paragraph(
                escape_html(gender),
                styles["Small"]
            )
        ],
        [
            Paragraph("Number of Personas", styles["Small"]),
            Paragraph(
                str(total),
                styles["Small"]
            )
        ]
    ]

    story.append(
        make_table(
            overview_data,
            widths=[48 * mm, 132 * mm]
        )
    )

    story.append(Spacer(1, 8 * mm))

    # -----------------------------------------------------
    # 2. OVERALL RESULTS
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "2. Overall Results",
            styles["SectionHeading"]
        )
    )

    metric_data = [[
        metric_card(
            "Total Personas",
            str(total),
            styles
        ),
        metric_card(
            "Would Use / Buy",
            f"{would_use_percentage}%",
            styles
        ),
        metric_card(
            "Average Rating",
            f"{average_rating}/5",
            styles
        ),
        metric_card(
            "Adoption Score",
            f"{overall_adoption}/100",
            styles
        )
    ]]

    metric_table = Table(
        metric_data,
        colWidths=[
            44 * mm,
            44 * mm,
            44 * mm,
            44 * mm
        ]
    )

    metric_table.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 2),
            ("RIGHTPADDING", (0, 0), (-1, -1), 2)
        ])
    )

    story.append(metric_table)
    story.append(Spacer(1, 7 * mm))

    results_data = [
        [
            Paragraph("<b>Result</b>", styles["Small"]),
            Paragraph("<b>Value</b>", styles["Small"])
        ],
        [
            Paragraph("Would use / purchase", styles["Small"]),
            Paragraph(
                f"{preferred} personas",
                styles["Small"]
            )
        ],
        [
            Paragraph("Would not use / purchase", styles["Small"]),
            Paragraph(
                f"{not_preferred} personas",
                styles["Small"]
            )
        ],
        [
            Paragraph("Validation Status", styles["Small"]),
            Paragraph(
                f"<b>{escape_html(validation)}</b>",
                styles["Small"]
            )
        ]
    ]

    story.append(
        make_table(
            results_data,
            widths=[80 * mm, 100 * mm]
        )
    )

    story.append(Spacer(1, 5 * mm))

    story.append(
        Paragraph(
            "The adoption score combines product rating and purchase/use "
            "decision. It is calculated as: "
            "(Rating / 5 × 60) + 40 points when the persona selects Yes.",
            styles["BodyReport"]
        )
    )

    # -----------------------------------------------------
    # 3. PERSONA SUMMARY & OPINIONS
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "3. Persona Summary & Opinions",
            styles["SectionHeading"]
        )
    )

    persona_rows = [[
        Paragraph("<b>Name</b>", styles["Small"]),
        Paragraph("<b>Age</b>", styles["Small"]),
        Paragraph("<b>Gender</b>", styles["Small"]),
        Paragraph("<b>Occupation</b>", styles["Small"]),
        Paragraph("<b>Rating</b>", styles["Small"]),
        Paragraph("<b>Decision</b>", styles["Small"]),
        Paragraph("<b>Adoption</b>", styles["Small"]),
        Paragraph("<b>Opinion / Reason</b>", styles["Small"])
    ]]

    for persona in personas:

        if not isinstance(persona, dict):
            continue

        score = calculate_adoption_score(persona)

        decision = safe_text(
            persona.get("buyDecision"),
            "No"
        )

        persona_rows.append([
            Paragraph(
                escape_html(
                    persona.get("name")
                ),
                styles["Small"]
            ),
            Paragraph(
                escape_html(
                    persona.get("age")
                ),
                styles["Small"]
            ),
            Paragraph(
                escape_html(
                    persona.get("gender")
                ),
                styles["Small"]
            ),
            Paragraph(
                escape_html(
                    persona.get("occupation")
                ),
                styles["Small"]
            ),
            Paragraph(
                f"{safe_text(persona.get('rating'), '0')}/5",
                styles["Small"]
            ),
            Paragraph(
                escape_html(decision),
                styles["Small"]
            ),
            Paragraph(
                f"{score}/100<br/>"
                f"{escape_html(adoption_category(score))}",
                styles["Small"]
            ),
            Paragraph(
                escape_html(
                    persona.get("reason")
                ),
                styles["Small"]
            )
        ])

    story.append(
        make_table(
            persona_rows,
            widths=[
                22 * mm,
                11 * mm,
                15 * mm,
                27 * mm,
                14 * mm,
                17 * mm,
                23 * mm,
                51 * mm
            ]
        )
    )

    # -----------------------------------------------------
    # 4. ADOPTION DISTRIBUTION
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "4. Adoption Score Distribution",
            styles["SectionHeading"]
        )
    )

    high = sum(
        1
        for score in adoption_scores
        if score >= 70
    )

    moderate = sum(
        1
        for score in adoption_scores
        if 40 <= score < 70
    )

    low = sum(
        1
        for score in adoption_scores
        if score < 40
    )

    distribution_data = [
        [
            Paragraph("<b>Category</b>", styles["Small"]),
            Paragraph("<b>Personas</b>", styles["Small"]),
            Paragraph("<b>Meaning</b>", styles["Small"])
        ],
        [
            Paragraph("High Adoption", styles["Small"]),
            Paragraph(str(high), styles["Small"]),
            Paragraph(
                "Strong interest and positive product response.",
                styles["Small"]
            )
        ],
        [
            Paragraph("Moderate Adoption", styles["Small"]),
            Paragraph(str(moderate), styles["Small"]),
            Paragraph(
                "Potential interest with some conditions or concerns.",
                styles["Small"]
            )
        ],
        [
            Paragraph("Low Adoption", styles["Small"]),
            Paragraph(str(low), styles["Small"]),
            Paragraph(
                "Low purchase/use intention or weak rating.",
                styles["Small"]
            )
        ]
    ]

    story.append(
        make_table(
            distribution_data,
            widths=[45 * mm, 30 * mm, 105 * mm]
        )
    )

    # -----------------------------------------------------
    # 5. RESPONSE & OPINION SUMMARY
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "5. Response & Opinion Summary",
            styles["SectionHeading"]
        )
    )

    story.append(
        Paragraph(
            escape_html(
                response_summary["direction"]
            ),
            styles["BodyReport"]
        )
    )

    themes = response_summary["themes"]

    if themes:
        story.append(
            Paragraph(
                "<b>Common themes:</b> "
                + escape_html(", ".join(themes)),
                styles["BodyReport"]
            )
        )
    else:
        story.append(
            Paragraph(
                "<b>Common themes:</b> No recurring themes detected.",
                styles["BodyReport"]
            )
        )

    if response_summary["concerns"]:

        story.append(
            Paragraph(
                "<b>Important concerns:</b>",
                styles["BodyReport"]
            )
        )

        for concern in response_summary["concerns"]:
            story.append(
                Paragraph(
                    "• " + escape_html(concern),
                    styles["BodyReport"]
                )
            )

    # -----------------------------------------------------
    # 6. AI INSIGHTS SUMMARY
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "6. AI Research Insights",
            styles["SectionHeading"]
        )
    )

    ai_summary = str(insights.get("summary", "")).strip()
    ai_main_finding = str(insights.get("mainFinding", "")).strip()

    if ai_summary:
        story.append(
            Paragraph(
                "<b>Overall AI summary:</b> " + escape_html(ai_summary),
                styles["BodyReport"]
            )
        )

    if ai_main_finding and ai_main_finding != ai_summary:
        story.append(
            Paragraph(
                "<b>Main finding:</b> " + escape_html(ai_main_finding),
                styles["BodyReport"]
            )
        )

    for label, key in [
        ("Positive signals", "positiveSignals"),
        ("Concerns", "concerns"),
        ("Interview discoveries", "interviewDiscoveries"),
        ("Behavioral trends", "behavioralTrends")
    ]:
        items = insights.get(key, [])
        if isinstance(items, list) and items:
            story.append(
                Paragraph(
                    "<b>" + escape_html(label) + ":</b>",
                    styles["BodyReport"]
                )
            )
            for item in items[:8]:
                if isinstance(item, dict):
                    text = (
                        item.get("description")
                        or item.get("reasoning")
                        or item.get("interpretation")
                        or item.get("title")
                        or item.get("topic")
                        or item.get("theme")
                        or item.get("evidence")
                        or str(item)
                    )
                else:
                    text = str(item)
                story.append(
                    Paragraph(
                        "• " + escape_html(text),
                        styles["BodyReport"]
                    )
                )

    ai_themes = insights.get("themes", [])
    if isinstance(ai_themes, list) and ai_themes:
        story.append(
            Paragraph(
                "<b>Key themes:</b>",
                styles["BodyReport"]
            )
        )
        for theme in ai_themes[:6]:
            if isinstance(theme, dict):
                name = theme.get("theme", "Theme")
                desc = theme.get("description", "")
                agreement = theme.get("agreement")
                suffix = f" ({agreement}% agreement)" if agreement is not None else ""
                text = f"{name}{suffix}: {desc}"
            else:
                text = str(theme)
            story.append(
                Paragraph(
                    "• " + escape_html(text),
                    styles["BodyReport"]
                )
            )

    comparison = insights.get("surveyVsInterview", [])
    if isinstance(comparison, list) and comparison:
        story.append(
            Paragraph(
                "<b>Survey vs interview:</b>",
                styles["BodyReport"]
            )
        )
        for item in comparison[:6]:
            if isinstance(item, dict):
                text = (
                    f"{item.get('topic', 'Topic')}: "
                    f"Survey — {item.get('surveySignal', '—')}; "
                    f"Interview — {item.get('interviewSignal', '—')}; "
                    f"{item.get('interpretation', '')}"
                )
            else:
                text = str(item)
            story.append(
                Paragraph(
                    "• " + escape_html(text),
                    styles["BodyReport"]
                )
            )

    # -----------------------------------------------------
    # 7. INTERVIEW RESPONSE SUMMARY
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "6. Interview Response Summary",
            styles["SectionHeading"]
        )
    )

    total_individual = len(
        individual_interviews
    )

    total_all_questions = len(
        all_persona_interviews
    )

    total_all_responses = sum(
        len(item.get("responses", []))
        for item in all_persona_interviews
    )

    if (
        total_individual == 0
        and total_all_questions == 0
    ):

        story.append(
            Paragraph(
                "No interview responses were recorded for this research run.",
                styles["BodyReport"]
            )
        )

    else:

        story.append(
            Paragraph(
                f"Interview activity included "
                f"{total_individual} individual response(s) "
                f"and {total_all_responses} all-persona response(s) "
                f"across {total_all_questions} all-persona question(s).",
                styles["BodyReport"]
            )
        )

        # Summarize individual interview themes/questions
        question_groups = defaultdict(list)

        for item in individual_interviews:
            question_groups[
                item["question"]
            ].append(item["response"])

        if question_groups:

            story.append(
                Paragraph(
                    "<b>Individual interview findings:</b>",
                    styles["BodyReport"]
                )
            )

            for question, responses in question_groups.items():

                combined = " ".join(responses)
                themes_for_question = find_themes(
                    [combined]
                )

                summary_text = (
                    f"<b>Question:</b> "
                    f"{escape_html(question)}<br/>"
                    f"<b>Responses analyzed:</b> "
                    f"{len(responses)}"
                )

                if themes_for_question:
                    summary_text += (
                        "<br/><b>Recurring areas:</b> "
                        + escape_html(
                            ", ".join(
                                themes_for_question[:4]
                            )
                        )
                    )

                story.append(
                    Paragraph(
                        summary_text,
                        styles["BodyReport"]
                    )
                )

        # Summarize all-persona interview findings
        if all_persona_interviews:

            story.append(
                Paragraph(
                    "<b>All-persona interview findings:</b>",
                    styles["BodyReport"]
                )
            )

            for item in all_persona_interviews:

                question = item.get(
                    "question",
                    ""
                )

                responses = item.get(
                    "responses",
                    []
                )

                response_texts = []

                for response in responses:

                    if isinstance(response, dict):

                        answer = (
                            response.get("response")
                            or response.get("answer")
                            or response.get("message")
                            or ""
                        )

                        if answer:
                            response_texts.append(
                                str(answer)
                            )

                    elif response:
                        response_texts.append(
                            str(response)
                        )

                themes_for_question = find_themes(
                    response_texts
                )

                summary = (
                    f"<b>Question:</b> "
                    f"{escape_html(question)}<br/>"
                    f"<b>Persona responses analyzed:</b> "
                    f"{len(response_texts)}"
                )

                if themes_for_question:
                    summary += (
                        "<br/><b>Recurring areas:</b> "
                        + escape_html(
                            ", ".join(
                                themes_for_question[:4]
                            )
                        )
                    )

                story.append(
                    Paragraph(
                        summary,
                        styles["BodyReport"]
                    )
                )

        story.append(
            Paragraph(
                "The interview section summarizes response patterns and "
                "recurring topics rather than reproducing the complete "
                "conversation transcript.",
                styles["BodyReport"]
            )
        )

    # -----------------------------------------------------
    # 8. FINAL CONCLUSION
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "8. Final Research Conclusion",
            styles["SectionHeading"]
        )
    )

    conclusion = (
        f"The research included {total} personas. "
        f"{preferred} personas ({would_use_percentage}%) indicated "
        f"that they would use or purchase the product, while "
        f"{not_preferred} did not. The average rating was "
        f"{average_rating}/5 and the overall adoption score was "
        f"{overall_adoption}/100. Based on the defined scoring model, "
        f"the research result is classified as {validation}."
    )

    story.append(
        Paragraph(
            escape_html(conclusion),
            styles["BodyReport"]
        )
    )

    if themes:

        story.append(
            Paragraph(
                "The main response areas identified were: "
                + escape_html(
                    ", ".join(themes)
                )
                + ".",
                styles["BodyReport"]
            )
        )

    story.append(
        Paragraph(
            "This report is intended to support product-research "
            "decision making by combining persona survey results "
            "with a concise summary of recorded interview responses.",
            styles["BodyReport"]
        )
    )

    # -----------------------------------------------------
    # BUILD PDF
    # -----------------------------------------------------

    document.build(story)

    buffer.seek(0)

    return buffer
