import subprocess
import time
import os

# Configuration
ANALYSIS_SCRIPT_PATH = os.path.abspath("insights_engine.py")
INTERVAL_SECONDS = 120  # Run every 2 minutes

def run_analysis():
    print("📊 Running VM analysis...")
    try:
        result = subprocess.run(["python3", ANALYSIS_SCRIPT_PATH], check=True)
        print("✅ Analysis completed.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during analysis: {e}")

def main():
    while True:
        run_analysis()
        print(f"⏳ Waiting {INTERVAL_SECONDS} seconds until next run...")
        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    print("🧠 Background collector started.")
    main()

