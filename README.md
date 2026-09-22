# Persona AI — Synthetic User Research Platform

## Project Overview

**Persona AI** is an AI-powered synthetic user research platform designed to simulate user research using realistic AI-generated personas.

The platform takes **product information, target audience details, and research objectives** as inputs and generates a diverse set of synthetic users. Researchers can then interact with these personas, collect responses, analyze behavioral patterns, and generate research reports without conducting every research activity manually.

The system supports **up to 100 synthetic personas** and provides an end-to-end workflow from persona generation to research reporting.

---

## Key Features

### 1. AI Persona Generation

Persona AI generates synthetic users based on the research requirements provided by the researcher.

Each persona can include:

* Name
* Age
* Gender
* Occupation
* Personality
* Product rating
* Purchase decision
* Purchase reasoning
* Behavioral characteristics

The platform supports generation of **up to 100 personas**. Large requests can be processed using batch generation to improve reliability and scalability.

---

### 2. Individual Persona Interviews

Researchers can interact with individual synthetic personas through a conversational interface.

The system maintains:

* Conversation history
* Persona information
* Previous questions and responses
* Context across multiple turns

This allows a persona to provide more consistent responses throughout an interview rather than treating every question independently.

---

### 3. Ask All Personas

Researchers can ask the same question to multiple generated personas simultaneously.

This makes it easier to:

* Compare different user perspectives
* Identify common responses
* Discover differences between personas
* Understand overall user reactions

---

### 4. Research Analysis

Persona AI analyzes collected responses to identify meaningful research patterns, including:

* Recurring themes
* Sentiment
* Agreement patterns
* Behavioral trends
* Segment-level insights
* Common user preferences

The goal is to transform large volumes of synthetic responses into structured research findings.

---

### 5. Adoption Score

Each persona receives an **adoption score** based on their product rating and purchase decision.

The score provides a simple way to summarize product acceptance and compare how different personas respond to the product.

---

### 6. Results Dashboard

The Results Dashboard provides a centralized view of the generated research.

It can display:

* Total personas
* Purchase decisions
* Average product ratings
* Adoption scores
* Sentiment
* Common themes
* Persona opinions
* Research insights

This allows researchers to understand the overall research outcome without manually reviewing every response.

---

### 7. Ask Research

**Ask Research** enables researchers to ask natural-language questions about the generated research data.

Instead of manually analyzing individual responses, researchers can ask research-oriented questions and obtain answers based on the available persona and interview information.

Example questions include:

* What are the main reasons users would purchase the product?
* What concerns do users have about the product?
* Which features are commonly appreciated?
* What patterns appear across the personas?

---

### 8. Research Report Generation

The platform can generate a downloadable **PDF research report** containing:

* Research overview
* Persona findings
* Purchase decisions
* Adoption results
* Interview summaries
* Ask Research results
* Key insights
* Final conclusions

This provides a structured output that can be used for further analysis or presentation.

---

## 100-Persona Validation

A major objective of the project is validating the platform with **100 synthetic personas**.

Testing covers the complete research workflow, including:

* Persona generation
* Batch processing
* Persona data consistency
* Unique persona identification
* Individual interviews
* Multi-persona questioning
* Adoption score calculation
* Dashboard results
* Research insights
* Ask Research
* PDF report generation
* End-to-end workflow validation

This ensures that the platform can handle a larger synthetic research dataset while maintaining consistent functionality across its major components.

---

## System Workflow

```text
Research Setup
      ↓
Generate Personas
      ↓
View Personas
      ↓
Interview Individual Personas
      ↓
Ask All Personas
      ↓
Analyze Responses
      ↓
Extract Insights
      ↓
Ask Research
      ↓
Generate Research Report
```

---

## System Architecture

```text
                ┌──────────────────────┐
                │     Researcher       │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │   React + Vite UI    │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │    Flask Backend     │
                └──────────┬───────────┘
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
      Persona Engine   Interview     Research
             │          Engine        Analysis
             │             │             │
             └─────────────┼─────────────┘
                           ▼
                ┌──────────────────────┐
                │   Generative AI      │
                │   Google Gemini      │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ JSON Memory Storage  │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ Results / Insights   │
                │ Dashboard + Reports  │
                └──────────────────────┘
```

---

## Technology Stack

| Layer             | Technology         |
| ----------------- | ------------------ |
| Frontend          | React              |
| Build Tool        | Vite               |
| Backend           | Python             |
| API Framework     | Flask              |
| Generative AI     | Google Gemini      |
| Data Storage      | JSON-based memory  |
| Report Generation | ReportLab          |
| Communication     | REST API           |
| Development       | JavaScript, Python |

---

## Core Modules

### Research Setup

Collects product details, target audience information, and research objectives.

### Persona Generator

Creates synthetic users with demographic and behavioral characteristics.

### Interview Engine

Maintains persona context and conversation history during interviews.

### Ask All Personas

Allows the researcher to submit a question across multiple personas.

### Analysis Engine

Extracts themes, sentiment, behavioral trends, and agreement patterns.

### Adoption Analysis

Calculates and displays persona-level adoption scores.

### Results Dashboard

Presents aggregated research findings through an interactive interface.

### Ask Research

Provides natural-language access to the generated research data.

### Report Generator

Converts research findings into a structured PDF report.

---

## Data Flow

```text
Product Information
        │
        ▼
Research Configuration
        │
        ▼
AI Persona Generation
        │
        ▼
100 Synthetic Personas
        │
        ├──────────────► Individual Interviews
        │
        └──────────────► Ask All Personas
                              │
                              ▼
                       Response Collection
                              │
                              ▼
                       Research Analysis
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
          Insights       Ask Research      Adoption Score
             │                │                │
             └────────────────┼────────────────┘
                              ▼
                       Results Dashboard
                              │
                              ▼
                       PDF Research Report
```

---

## Project Objectives

The project aims to:

* Reduce the time required for early-stage user research.
* Simulate diverse user perspectives using AI-generated personas.
* Enable conversational exploration of synthetic users.
* Identify patterns across large sets of responses.
* Provide structured research insights.
* Support research with up to 100 synthetic personas.
* Generate a consolidated research report.

---

## Advantages

* **Scalable:** Supports up to 100 synthetic personas.
* **Interactive:** Enables conversational persona interviews.
* **Context-Aware:** Maintains persona and conversation context.
* **Data-Driven:** Extracts patterns from collected responses.
* **Research-Oriented:** Supports natural-language research queries.
* **Automated:** Reduces manual analysis of large response sets.
* **Reportable:** Generates downloadable research reports.
* **End-to-End:** Covers persona generation, interaction, analysis, and reporting in one platform.

---

## Validation

The completed system was validated using a 100-persona research workflow.

Validation included:

**Generation → Interaction → Analysis → Dashboard → Reporting**

The final validation verified persona generation, response consistency, interview functionality, analytical calculations, insights, Ask Research, and end-to-end system behavior.

---

## Conclusion

Persona AI provides an end-to-end environment for conducting **synthetic user research using generative AI**.

By combining AI-generated personas, conversational interviews, multi-persona questioning, automated analysis, adoption scoring, interactive results, and PDF reporting, the platform provides a structured approach to exploring user perspectives and product decisions.

The project demonstrates how generative AI can be integrated with a web-based research platform to create an interactive and scalable synthetic user research workflow.
