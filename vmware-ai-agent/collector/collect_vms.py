import subprocess
import json
import os
from tqdm import tqdm

os.environ["GOVC_INSECURE"] = "1"

def run_govc_command(args):
    cmd = ["govc"] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError:
        return None  # Silently skip errors

def get_vm_metrics(vm_path):
    metrics = ["cpu.usage.average", "mem.usage.average"]
    run_govc_command(["metric.enable", vm_path] + metrics)
    output = run_govc_command(["metric.sample", "-instance=-", vm_path] + metrics)

    if not output:
        return {}

    usage = {}
    for line in output.strip().splitlines():
        parts = line.split()
        if len(parts) >= 5:
            metric_name = parts[2]
            values = parts[3]
            usage[metric_name] = f"{values.split(',')[-1]} %"
    return usage

def get_vm_info():
    vm_list_output = run_govc_command(["find", ".", "-type", "VirtualMachine"])
    if not vm_list_output:
        return []

    vm_paths = vm_list_output.strip().splitlines()
    vm_data = []

    for path in tqdm(vm_paths, desc="🔍 Collecting VM data", unit="VM", ncols=100):
        if "(" in path or ")" in path:
            continue

        metrics = get_vm_metrics(path)
        name = run_govc_command(["object.collect", path, "config.name"])
        power = run_govc_command(["object.collect", path, "runtime.powerState"])
        guest = run_govc_command(["object.collect", path, "config.guestFullName"])

        if name and power and guest:
            vm_data.append({
                "path": path,
                "name": name.strip().split("\t")[-1],
                "power_state": power.strip().split("\t")[-1],
                "guest_os": guest.strip().split("\t")[-1],
                "metrics": metrics
            })
        else:
            info_json = run_govc_command(["vm.info", "-json", path])
            if info_json:
                try:
                    info = json.loads(info_json)
                    vm = info.get("VirtualMachines", [{}])[0]
                    vm_data.append({
                        "path": path,
                        "name": vm.get("Name", "Unknown"),
                        "power_state": vm.get("Runtime", {}).get("PowerState", "Unknown"),
                        "guest_os": vm.get("Config", {}).get("GuestFullName", "Unknown"),
                        "metrics": metrics
                    })
                except json.JSONDecodeError:
                    pass

    return vm_data

if __name__ == "__main__":
    vms = get_vm_info()
    with open("vm_data.json", "w") as f:
        json.dump(vms, f, indent=2)
    print(f"\n✅ Collected info and metrics for {len(vms)} VMs.")

