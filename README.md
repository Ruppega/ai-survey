# Persona AI – Synthetic User Research Platform

## 1. Project Overview

Persona AI is an AI-powered synthetic user research platform designed to help researchers simulate product research using AI-generated user personas.

The system generates realistic synthetic personas based on:

- Product name
- Product description
- Target audience age
- Target gender
- Research objective

Researchers can then interact with these personas, analyze their opinions, calculate product adoption scores, extract research insights, ask questions about the research data, and generate a downloadable research report.

The platform is designed to support large-scale synthetic research with **up to 100 personas**.

---

## 2. Project Objectives

The main objectives of the project are:

1. Generate realistic AI-powered synthetic users.
2. Support generation of up to 100 personas.
3. Provide individual persona interviews.
4. Maintain conversation memory and persona context.
5. Allow researchers to ask the same question to all personas.
6. Calculate product adoption scores.
7. Extract recurring themes and sentiment from research responses.
8. Provide an interactive research results dashboard.
9. Allow researchers to ask natural-language questions about the generated research.
10. Generate a downloadable PDF research report.
11. Validate the system through large-scale testing with 100 personas.

---

## 3. Key Features

### 3.1 AI Persona Generation

Users provide research information through the Research Setup form.

The system generates synthetic personas containing information such as:

- Name
- Gender
- Age
- Occupation
- Personality
- Product purchase decision
- Product rating
- Reason for the decision

The system supports between **1 and 100 personas**.

For large requests, persona generation is performed in batches to reduce the load on a single AI generation request.

Example:

```text
100 personas requested
        ↓
Batch 1 → 20 personas
Batch 2 → 20 personas
Batch 3 → 20 personas
Batch 4 → 20 personas
Batch 5 → 20 personas
        ↓
100 personas
