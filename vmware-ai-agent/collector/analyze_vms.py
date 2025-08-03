import json
import os

INPUT_FILE = "vm_data.json"
OUTPUT_FILE = "analysis_report.json"

def assess_vm(vm):
    metrics = vm.get("metrics", {})
    cpu = metrics.get("cpu.usage.average", "0 %").replace("%", "").strip()
    mem = metrics.get("mem.usage.average", "0 %").replace("%", "").strip()

    try:
        cpu_val = float(cpu)
        mem_val = float(mem)
    except ValueError:
        cpu_val = mem_val = 0.0

    risk = "✅ Healthy VM"
    recommendation = "No action needed."

    if cpu_val < 5 and mem_val > 70:
        risk = "⚠️ Low CPU usage but high memory usage"
        recommendation = "Consider checking for memory leaks or idle services"
    elif cpu_val > 85:
        risk = "🔥 High CPU usage"
        recommendation = "Check running processes or scale up resources"
    elif mem_val > 90:
        risk = "🔥 High memory usage"
        recommendation = "Consider adding more memory or optimizing usage"

    return {
        "name": vm.get("config.name", vm.get("name", "Unknown")).split()[-1],
        "power_state": vm.get("runtime.powerState", vm.get("power_state", "Unknown")).split()[-1],
        "cpu.usage.average": f"{cpu_val:.2f} %",
        "mem.usage.average": f"{mem_val:.2f} %",
        "risk": risk,
        "recommendation": recommendation
    }

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Missing input file: {INPUT_FILE}")
        return

    with open(INPUT_FILE, "r") as f:
        vm_data = json.load(f)

    report = [assess_vm(vm) for vm in vm_data]

    with open(OUTPUT_FILE, "w") as f:
        json.dump(report, f, indent=2)

    print(f"✅ Risk analysis complete. Report saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

