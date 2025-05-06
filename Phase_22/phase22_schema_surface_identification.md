# Phase 22: Schema Surface Identification & Loop Archetype Definitions

This document outlines key schema surfaces for Phase 22 and defines the initial set of loop archetypes and their classification criteria.

## Loop Archetypes

Loop archetypes categorize the primary intent or nature of an agent's operational cycle. Understanding these archetypes helps in resource allocation (like complexity budgets), agent selection, and overall system behavior analysis.

### 1. Explore

*   **Description:** The primary goal is to gather new information, understand a new domain, or broadly search for solutions without a highly specific target. This often involves significant interaction with external knowledge sources or novel data generation.
*   **Classification Criteria:**
    *   High use of information gathering tools (web search, browser navigation to new sites).
    *   Intent involves open-ended questions or tasks like "research X", "find information about Y".
    *   May involve generating diverse outputs or hypotheses.
    *   Low reliance on existing, detailed internal models for the specific task domain.
*   **Associated Complexity:** Typically moderate to high, due to the unpredictable nature of information encountered and the potential breadth of investigation.

### 2. Optimize

*   **Description:** The focus is on refining an existing solution, process, or piece of knowledge. This involves iterative improvements, parameter tuning, or making an existing artifact more efficient or effective.
*   **Classification Criteria:**
    *   Intent involves improving a known entity, e.g., "refine algorithm X", "improve performance of Y", "reduce cost of Z".
    *   Often involves analysis of existing data or artifacts.
    *   May use simulation or testing tools to measure improvement.
    *   Relies on a reasonably well-defined problem space.
*   **Associated Complexity:** Moderate. While the scope is defined, optimization can involve complex analysis and subtle adjustments.

### 3. Refactor

*   **Description:** The primary aim is to improve the internal structure, maintainability, or clarity of an existing system, code, or knowledge representation without changing its external behavior or core functionality. This is about improving the *how*, not the *what*.
*   **Classification Criteria:**
    *   Intent involves restructuring, e.g., "refactor module X", "improve code readability of Y", "consolidate schemas for Z".
    *   Focus on internal quality attributes.
    *   Should result in functionally equivalent outputs for the same inputs.
    *   Often involves code analysis or schema manipulation tools.
*   **Associated Complexity:** Moderate to high, as it can involve deep understanding of existing structures and careful, error-prone modifications.

### 4. Implement

*   **Description:** The goal is to create or build a new component, feature, or artifact based on a relatively well-defined specification or plan. This is less about discovery and more about construction.
*   **Classification Criteria:**
    *   Intent involves creation, e.g., "implement feature X", "build module Y", "create schema Z".
    *   Follows a known plan or detailed requirements.
    *   Involves writing code, creating data structures, or populating knowledge bases according to a blueprint.
*   **Associated Complexity:** Variable, from low (for simple, well-specified components) to high (for complex systems), but generally more predictable than Explore.

### 5. Validate / Verify

*   **Description:** The primary purpose is to check if a system, component, piece of data, or belief conforms to specifications, requirements, or known truths. This involves testing, checking consistency, or confirming accuracy.
*   **Classification Criteria:**
    *   Intent involves checking, e.g., "validate X against schema Y", "test functionality Z", "verify accuracy of data A".
    *   Often involves comparison against a baseline or a set of rules.
    *   May use testing frameworks, assertion tools, or logical inference.
*   **Associated Complexity:** Low to moderate. The process is usually well-defined, but the analysis of results can sometimes be complex.

### 6. Debug / Remediate

*   **Description:** The focus is on identifying and fixing errors, inconsistencies, or failures in an existing system, component, or dataset. This is a reactive process to a known or suspected problem.
*   **Classification Criteria:**
    *   Triggered by an error, bug report, or identified anomaly.
    *   Intent involves fixing, e.g., "debug error X", "remediate inconsistency Y".
    *   Involves diagnostic tools, log analysis, and targeted modifications.
*   **Associated Complexity:** Moderate to high, as debugging can be a complex and time-consuming process of elimination and hypothesis testing.

This list is not exhaustive and can be expanded as the system evolves. The archetype classifier will use these definitions and criteria to categorize loop intents.

