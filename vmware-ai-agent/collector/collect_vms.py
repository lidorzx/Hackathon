import subprocess
import json
import os

os.environ["GOVC_INSECURE"] = "1"

def run_govc_command(args):
    cmd = ["govc"] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print("Command failed:", e.stderr)
        return None

def get_vm_info():
    vm_list_output = run_govc_command(["find", ".", "-type", "VirtualMachine"])
    if not vm_list_output:
        return []

    vm_paths = vm_list_output.strip().splitlines()
    vm_data = []

    for path in vm_paths:
        if "(" in path or ")" in path:
            print(f"Skipping problematic VM path: {path}")
            continue

        print(f"Querying VM: {path}")
        name = run_govc_command(["object.collect", path, "config.name"])
        power = run_govc_command(["object.collect", path, "runtime.powerState"])
        guest = run_govc_command(["object.collect", path, "config.guestFullName"])

        if name and power and guest:
            vm_data.append({
                "path": path,
                "name": name.strip().split("\t")[-1],
                "power_state": power.strip().split("\t")[-1],
                "guest_os": guest.strip().split("\t")[-1]
            })
        else:
            print(f"⚠️ Fallback to vm.info for: {path}")
            info_json = run_govc_command(["vm.info", "-json", path])
            if info_json:
                try:
                    info = json.loads(info_json)
                    vm = info.get("VirtualMachines", [{}])[0]
                    vm_data.append({
                        "path": path,
                        "name": vm.get("Name", "Unknown"),
                        "power_state": vm.get("Runtime", {}).get("PowerState", "Unknown"),
                        "guest_os": vm.get("Config", {}).get("GuestFullName", "Unknown")
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
    print(f"\n✅ Collected info for {len(vms)} VMs.")
