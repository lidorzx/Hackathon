import json
import requests
import os

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
        f"Give a short risk label and a recommendation."
    )

def analyze_vms():
    if not os.path.exists(VM_DATA_FILE):
        print(f"❌ VM data file '{VM_DATA_FILE}' not found.")
        return

    with open(VM_DATA_FILE, "r") as f:
        vm_data = json.load(f)

    report = []
    for vm in vm_data:
        print(f"🧠 Analyzing: {vm.get('config.name', vm.get('name', 'Unknown'))}")
        prompt = generate_prompt(vm)
        insight = ask_llm(prompt)

        # Build the report entry with basic metrics
        report_entry = {
            "name": vm.get("config.name", vm.get("name", "Unknown")),
            "power_state": vm.get("runtime.powerState", vm.get("power_state", "Unknown")),
            "cpu.usage.average": vm.get("metrics", {}).get("cpu.usage.average"),
            "mem.usage.average": vm.get("metrics", {}).get("mem.usage.average"),
        }

        # Process LLM response
        if insight:
            if "recommendation" in insight.lower():
                try:
                    parts = insight.split("recommendation", 1)
                    report_entry["risk"] = parts[0].strip().rstrip(":")
                    report_entry["recommendation"] = parts[1].strip()
                except Exception:
                    report_entry["risk"] = insight.strip()
                    report_entry["recommendation"] = "⚠️ Could not parse recommendation."
            else:
                report_entry["risk"] = insight.strip()
                report_entry["recommendation"] = "✅ No issues detected."
        else:
            report_entry["risk"] = "⚠️ No response from model"
            report_entry["recommendation"] = "Ensure model is available or retry."

        report.append(report_entry)

    # Write final report
    with open(OUTPUT_REPORT_FILE, "w") as f:
        json.dump(report, f, indent=2)

    print("\n✅ Risk analysis complete. Report saved to:", OUTPUT_REPORT_FILE)

if __name__ == "__main__":
    analyze_vms()

