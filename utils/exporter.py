
import csv
import io
from datetime import datetime
from config.settings import EXPORT_COLUMNS


def generate_csv(log: list) -> bytes:
    """
    Convert the moderation log list into a downloadable CSV bytes object.
    """
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=EXPORT_COLUMNS, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(log)
    return output.getvalue().encode("utf-8")


def get_export_filename() -> str:
    """Generate a timestamped filename for the CSV export."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"moderation_report_{ts}.csv"
