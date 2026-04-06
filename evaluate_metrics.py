import os
import json
import glob
from statistics import mean

LOG_DIR = "logs"

def evaluate_metrics():
    """
    Parse JSON log files and calculate metrics based on EVALUATION.md.
    """
    if not os.path.exists(LOG_DIR):
        print(f"Directory {LOG_DIR} does not exist. Please run the agent first to generate logs.")
        return

    log_files = glob.glob(os.path.join(LOG_DIR, "*.log"))
    if not log_files:
        print("No log files found in the logs directory.")
        return

    prompt_tokens = []
    completion_tokens = []
    total_tokens = []
    latencies = []
    costs = []
    
    agent_steps = []
    total_runs = 0
    errors = 0
    
    # Error classification for Failure Analysis
    json_parser_errors = 0
    hallucination_errors = 0
    timeout_errors = 0

    for log_file in log_files:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    event = data.get("event")
                    payload = data.get("data", {})
                    
                    if event == "LLM_METRIC":
                        prompt_tokens.append(payload.get("prompt_tokens", 0))
                        completion_tokens.append(payload.get("completion_tokens", 0))
                        total_tokens.append(payload.get("total_tokens", 0))
                        latencies.append(payload.get("latency_ms", 0))
                        costs.append(payload.get("cost_estimate", 0))
                        
                    elif event == "AGENT_START":
                        total_runs += 1
                        
                    elif event == "AGENT_END":
                        agent_steps.append(payload.get("steps", 0))
                        
                    elif event == "ERROR" or "error" in str(event).lower():
                        errors += 1
                        error_type = payload.get("error_type", "")
                        if "json" in error_type.lower() or "parse" in error_type.lower():
                            json_parser_errors += 1
                        elif "tool" in error_type.lower() or "hallucination" in error_type.lower():
                            hallucination_errors += 1
                        elif "timeout" in error_type.lower() or "max_steps" in error_type.lower():
                            timeout_errors += 1
                            
                    # Additional tracking if loop maxed out based on step count
                    if event == "AGENT_END" and payload.get("steps", 0) >= payload.get("max_steps", 5):
                        # Assuming it was a max steps timeout issue
                        timeout_errors += 1
                        
                except json.JSONDecodeError:
                    # Ignore lines that are not valid JSON
                    continue

    print("Evaluation Metrics Report")
    
    # 1. Token Efficiency
    print("\n1. Token Efficiency (Average per Request):")
    if total_tokens:
        print(f"   - Prompt Tokens: {mean(prompt_tokens):.2f}")
        print(f"   - Completion Tokens: {mean(completion_tokens):.2f}")
        print(f"   - Total Tokens: {mean(total_tokens):.2f}")
        print(f"   - Total Cost Estimate: ${sum(costs):.6f}")
    else:
        print("   - No token data found.")
        
    # 2. Latency
    print("\n2. Latency (Average):")
    if latencies:
        print(f"   - Latency (ms): {mean(latencies):.2f}")
    else:
        print("   - No latency data found.")
        
    # 3. Loop Count (Steps)
    print("\n3. Loop Count (Steps):")
    if agent_steps:
        print(f"   - Average Steps per Run: {mean(agent_steps):.2f}")
        print(f"   - Total Successful Completions: {len(agent_steps)}")
    else:
        print("   - No step data found.")
        
    # 4. Failure Analysis
    print("\n4. Failure Analysis:")
    print(f"   - Total Runs Initiated: {total_runs}")
    print(f"   - General Errors: {errors}")
    print(f"   - JSON Parser Errors: {json_parser_errors}")
    print(f"   - Hallucination Errors: {hallucination_errors}")
    print(f"   - Timeout/Max Steps Errors: {timeout_errors}")
    
    total_failures = errors + json_parser_errors + hallucination_errors + timeout_errors
    
    # Calculate Aggregate Reliability
    print("\n=> Aggregate Reliability:")
    if total_runs > 0:
        # We consider a run successful if it didn't encounter failures that stopped execution
        # As an approximation, we calculate success rate
        reliability = max(0, ((total_runs - total_failures) / total_runs) * 100)
        print(f"   {reliability:.2f}% (Success Rate based on {total_runs} total runs)")
    else:
        print("   N/A (No runs detected. Start the agent to generate logs.)")

if __name__ == "__main__":
    evaluate_metrics()
