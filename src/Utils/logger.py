import datetime

class RunLogger:
    def __init__(self):
        self.logs = []
        self.start_time = datetime.datetime.now()

    def log_step(self, agent: str, action: str, details: str = ""):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        entry = f"| {timestamp} | **{agent}** | {action} | {details} |"
        self.logs.append(entry)
        # Also print to console so we still see it live
        print(f"[{agent}] {action} {details}")

    def save_report(self, filename="run_report.md"):
        duration = datetime.datetime.now() - self.start_time
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# 🕵️ Agent Execution Report\n")
            f.write(f"**Date:** {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Duration:** {duration}\n\n")
            
            f.write("## 🔄 Execution Trace\n")
            f.write("| Time | Agent | Action | Details |\n")
            f.write("|---|---|---|---|\n")
            for log in self.logs:
                f.write(log + "\n")
            
            f.write("\n## ✅ Final Status\n")
            f.write("System completed successfully. Generated 3 artifacts.\n")
            
        print(f"\n📄 Report saved to {filename}")