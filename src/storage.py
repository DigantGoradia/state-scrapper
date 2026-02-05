import json
import logging
import os


class JobHistory:
    """Manages persistence of processed job symbols."""

    def __init__(self, data_file: str = "data/history.json"):
        """Initializes the history manager."""
        self.data_file = data_file
        self.logger = logging.getLogger(__name__)

    def load_history(self) -> set[str]:
        """Loads the set of processed job symbols from the JSON file."""
        if not os.path.exists(self.data_file):
            return set()

        try:
            with open(self.data_file) as f:
                data = json.load(f)
                return set(data.get("processed_jobs", []))
        except (OSError, json.JSONDecodeError) as e:
            self.logger.error(f"Error loading history: {e}")
            return set()

    def update_history(self, new_symbols: list[str]):
        """Adds new symbols to the history and saves the file."""
        current_history = self.load_history()
        updated_history = current_history.union(set(new_symbols))

        # Ensure directory exists
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)

        try:
            with open(self.data_file, "w") as f:
                json.dump({"processed_jobs": list(updated_history)}, f, indent=2)
            self.logger.info(f"Updated history with {len(new_symbols)} new jobs.")
        except OSError as e:
            self.logger.error(f"Error saving history: {e}")
