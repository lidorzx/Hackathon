import subprocess
import json
import os

# Allow self-signed certs
os.environ["GOVC_INSECURE"] = "1"

def run_govc_command(args):
    cmd = ["govc"] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print("Command failed:", e.stderr)
        return None

def get_vm_metrics(vm_path, vm_name):
    # Enable metrics first
    metrics = ["cpu.usage.average", "mem.usage.average"]
    run_govc_command(["metric.enable", vm_path] + metrics)

    # Sample metrics
    sample_output = run_govc_command([
        "metric.sample", "-instance=-", "-n=1", vm_path
    ] + metrics)

    if not sample_output:
        return {}

    usage = {}
    for line in sample_output.strip().splitlines():
        parts = line.split()
        if len(parts) >= 4:
            metric_key = parts[2]  # e.g. cpu.usage.average
            metric_value = parts[3].split(",")[-1]  # Last sample
            usage[metric_key] = f"{metric_value.strip()} %"
    return usage

def get_vm_info():
    vm_list_output = run_govc_command(["find", ".", "-type", "VirtualMachine"])
    if not vm_list_output:
        return []

    vm_paths = vm_list_output.strip().splitlines()
    vm_data = []

    for path in vm_paths:
        if "(" in path or ")" in path:
            print(f"⚠️ Skipping problematic VM path: {path}")
            continue

        print(f"🔍 Querying VM: {path}")

        # Get name, power, guest
        name = run_govc_command(["object.collect", path, "config.name"])
        power = run_govc_command(["object.collect", path, "runtime.powerState"])
        guest = run_govc_command(["object.collect", path, "config.guestFullName"])

        if name and power and guest:
            name_clean = name.strip().split()[-1]
            power_clean = power.strip().split()[-1]
            guest_clean = guest.strip().split("string")[-1].strip()

            # Get metrics
            metrics = get_vm_metrics(path, name_clean)

            vm_data.append({
                "path": path,
                "name": name_clean,
                "power_state": power_clean,
                "guest_os": guest_clean,
                "metrics": metrics
            })
        else:
            print(f"⚠️ Fallback to vm.info for: {path}")
            info_json = run_govc_command(["vm.info", "-json", path])
            if info_json:
                try:
                    info = json.loads(info_json)
                    vm = info.get("VirtualMachines", [{}])[0]
                    metrics = get_vm_metrics(path, vm.get("Name", "Unknown"))
                    vm_data.append({
                        "path": path,
                        "name": vm.get("Name", "Unknown"),
                        "power_state": vm.get("Runtime", {}).get("PowerState", "Unknown"),
                        "guest_os": vm.get("Config", {}).get("GuestFullName", "Unknown"),
                        "metrics": metrics
                    })
                except json.JSONDecodeError:
                    print(f"❌ JSON decode error for: {path}")
            else:
                print(f"❌ Failed to collect any data for: {path}")

    return vm_data

if __name__ == "__main__":
    vms = get_vm_info()
    with open("vm_data.json", "w") as f:
        json.dump(vms, f, indent=2)
<<<<<<< HEAD
    print(f"\n✅ Collected info for {len(vms)} VMs.")
=======
    print(f"\n✅ Collected info and metrics for {len(vms)} VMs.")

>>>>>>> 4406cbd (WIP: local changes before rebase)
