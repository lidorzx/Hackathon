import json
import requests
import os
import re

VLLM_API_URL = "http://localhost:8000/v1/chat/completions"
VLLM_MODEL_NAME = "llama-3.3-70B-Instruct"
VM_DATA_FILE = "vm_data.json"
OUTPUT_REPORT_FILE = "analysis_report.json"

def ask_llm(prompt):
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": VLLM_MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }

    try:
        response = requests.post(VLLM_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        print(f"❌ Failed to reach vLLM API: {e}")
        return None

def generate_prompt(vm):
    return (
        f"Analyze the following virtual machine and detect any risks or inefficiencies:\n"
        f"- Name: {vm.get('config.name', vm.get('name', 'Unknown'))}\n"
        f"- Power State: {vm.get('runtime.powerState', vm.get('power_state', 'Unknown'))}\n"
        f"- Guest OS: {vm.get('config.guestFullName', vm.get('guest_os', 'Unknown'))}\n"
        f"- CPU Usage: {vm.get('metrics', {}).get('cpu.usage.average', 'N/A')}\n"
        f"- Memory Usage: {vm.get('metrics', {}).get('mem.usage.average', 'N/A')}\n"
        f"Respond in the following format:\n"
        f"**Risk Label:** <short risk label>\n"
        f"**Recommendation:** <short, actionable recommendation>"
    )

def analyze_vms():
    if not os.path.exists(VM_DATA_FILE):
        print(f"❌ VM data file '{VM_DATA_FILE}' not found.")
        return

    with open(VM_DATA_FILE, "r") as f:
        vm_data = json.load(f)

    report = []
    for vm in vm_data:
        vm_name = vm.get('config.name', vm.get('name', 'Unknown'))
        print(f"🧠 Analyzing: {vm_name}")
        prompt = generate_prompt(vm)
        insight = ask_llm(prompt)

        # Build the report entry with base fields
        report_entry = {
            "name": vm_name,
            "power_state": vm.get("runtime.powerState", vm.get("power_state", "Unknown")),
            "cpu.usage.average": vm.get("metrics", {}).get("cpu.usage.average"),
            "mem.usage.average": vm.get("metrics", {}).get("mem.usage.average"),
        }

        # Extract Risk and Recommendation from markdown-style AI response
        if insight:
            risk_match = re.search(r"\*\*Risk Label:\*\*\s*(.+)", insight)
            rec_match = re.search(r"\*\*Recommendation:\*\*\s*(.+)", insight, re.DOTALL)

            if risk_match and rec_match:
                report_entry["risk"] = risk_match.group(1).strip()
                report_entry["recommendation"] = rec_match.group(1).strip()
            else:
                # Fallback: split by first newline
                parts = insight.strip().split("\n", 1)
                report_entry["risk"] = parts[0].strip()
                report_entry["recommendation"] = parts[1].strip() if len(parts) > 1 else "⚠️ Could not parse recommendation."
        else:
            report_entry["risk"] = "⚠️ No response from model"
            report_entry["recommendation"] = "Ensure model is available or retry."

        report.append(report_entry)

    # Write the analysis report
    with open(OUTPUT_REPORT_FILE, "w") as f:
        json.dump(report, f, indent=2)

    print("\n✅ Risk analysis complete. Report saved to:", OUTPUT_REPORT_FILE)

if __name__ == "__main__":
    analyze_vms()
