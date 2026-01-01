import os
import json
from src.core.workflow_state import WorkflowState

class ArtifactSaver:
    @staticmethod
    def save_artifacts(state: WorkflowState, output_dir="output"):
        """Saves final JSON pages to the output directory."""
        
        # 1. Ensure directory exists
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                print(f"📂 Created output directory: {output_dir}")
            except OSError as e:
                print(f"❌ Error creating output directory: {e}")
                return

        # 2. Map filenames to state data
        artifacts = {
            "product_page.json": state.product_page,
            "faq_page.json": state.faq_page,
            "comparison_page.json": state.comparison_page
        }

        # 3. Save files
        saved_count = 0
        for filename, content in artifacts.items():
            if content:
                filepath = os.path.join(output_dir, filename)
                try:
                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump(content, f, indent=2)
                    saved_count += 1
                except IOError as e:
                    print(f"❌ Failed to save {filename}: {e}")

        if saved_count > 0:
            print(f"💾 Successfully saved {saved_count} JSON files to '{output_dir}/'")
        else:
            print("⚠️ No artifacts were generated to save.")