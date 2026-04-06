# Group Report: Lab 3 - Production-Grade Agentic System

- **Team Name**: BanGanCua
- **Team Members**: Hồ Bảo Thư, Lê Thanh Thưởng, Nguyễn Đình Hiếu, Trần Văn Tuấn, Lê Đình Việt, Lê Văn Tùng
- **Deployment Date**: 2026-04-06
---

## 1. Executive Summary

*Brief overview of the agent's goal and success rate compared to the baseline chatbot.*

- **Success Rate**: [e.g., 85% on 20 test cases]
- **Key Outcome**: [e.g., "Our agent solved 40% more multi-step queries than the chatbot baseline by correctly utilizing the Search tool."]

---

## 2. System Architecture & Tooling

### 2.1 ReAct Loop Implementation

Our agent employs a production-grade ReAct (Reasoning and Acting) loop to handle multi-step banking queries. Instead of providing generic advice, the agent iteratively calls specialized financial tools:

1.  **Thought**: The LLM analyzes the user's intent (e.g., comparing banks or calculating returns).
2.  **Action**: It invokes `fetch_interest_rates` to retrieve live data or `calculate_savings_interest` for precise math.
3.  **Observation**: The system feeds the tool's output back into the prompt, allowing the agent to refine its recommendation.

This cycle continues for up to **10 steps** until a comprehensive **Final Answer** is generated, ensuring that financial data is never hallucinated.

```mermaid
graph TD
    Start(["Input: Banking Query"]) --> Init["Init Context (Prompt + Question)"]
    Init --> Loop{"Loop: steps < 10?"}
    
    Loop -- Yes --> LLM["LLM: Generate Thought + Action"]
    LLM --> Parse["Parse: Tool Name & JSON Args"]
    
    Parse --> Exec["Execute: fetch_rate or calculate_interest"]
    Exec --> Obs["Observation: Live Bank Data/Calculated Result"]
    Obs --> Context["Update Context with Observation"]
    Context --> Increment["Steps++"]
    Increment --> Loop
    
    Parse -- Final Answer Found --> Success(["Output: Accurate Financial Advice"])
    Loop -- No --> Timeout(["Max Steps Reached: Timeout Error"])



### 2.2 Tool Definitions (Inventory)
| Tool Name | Input Format | Use Case |
| :--- | :--- | :--- |
| `calculate_saving_interest` | `principal` ,`rate_percent`,  `months`| Calculate interest over given duration  |
| `bank_tools` |  | Search all banks’ interest rates at the present. |

### 2.3 LLM Providers Used
- **Primary**: GPT-4o-mini (Azure Inference API)
- **Secondary (Backup)**: Gemini 1.5 Flash & Phi-3 Mini (Local GGUF via llama-cpp)

---

## 3. Telemetry & Performance Dashboard

*Analyze the industry metrics collected during the final test run.*

- **Average Latency (P50)**: [e.g., 1200ms]
- **Max Latency (P99)**: [e.g., 4500ms]
- **Average Tokens per Task**: [e.g., 350 tokens]
- **Total Cost of Test Suite**: [e.g., $0.05]

---

## 4. Root Cause Analysis (RCA) - Failure Traces

*Deep dive into why the agent failed.*

### Case Study: [e.g., Hallucinated Argument]
- **Input**: "How much is the tax for 500 in Vietnam?"
- **Observation**: Agent called `calc_tax(amount=500, region="Asia")` while the tool only accepts 2-letter country codes.
- **Root Cause**: The system prompt lacked enough `Few-Shot` examples for the tool's strict argument format.

---

## 5. Ablation Studies & Experiments

### Experiment 1: Prompt v1 vs Prompt v2
- **Diff**: [e.g., Adding "Always double check the tool arguments before calling".]
- **Result**: Reduced invalid tool call errors by [e.g., 30%].

### Experiment 2 (Bonus): Chatbot vs Agent
| Case | Chatbot Result | Agent Result | Winner |
| :--- | :--- | :--- | :--- |
| Simple Q | Correct | Correct | Draw |
| Multi-step | Hallucinated | Correct | **Agent** |

---

## 6. Production Readiness Review

*Considerations for taking this system to a real-world environment.*

- **Security**: [e.g., Input sanitization for tool arguments.]
- **Guardrails**: [e.g., Max 5 loops to prevent infinite billing cost.]
- **Scaling**: [e.g., Transition to LangGraph for more complex branching.]

---

> [!NOTE]
> Submit this report by renaming it to `GROUP_REPORT_[TEAM_NAME].md` and placing it in this folder.
