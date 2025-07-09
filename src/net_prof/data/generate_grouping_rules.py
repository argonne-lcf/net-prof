import csv
import re

def convert_counter_name_to_regex(name: str) -> str:
    """
    Converts counter names with wildcards like <n>, <min>, <max> into regex.
    Example: HNI_PKTS_SENT_BY_TC_<n> → ^HNI_PKTS_SENT_BY_TC_\\d+$
    """
    # Replace any placeholder like <...> with \d+
    regex_name = re.sub(r"<[^>]+>", r"\\d+", name)
    return f"^{regex_name}$"

def generate_grouping_rules(input_path: str = "groupings3.csv",
                            output_path: str = "grouping_rules.csv"):
    # Read tab-delimited input and write comma-delimited output including Unit.
    with open(input_path, "r", newline="") as infile:
        reader = csv.DictReader(infile, delimiter="\t")
        print("Detected headers:", reader.fieldnames)  # Debugging aid

        with open(output_path, "w", newline="") as outfile:
            fieldnames = ["Counter_Group", "Regex", "Counter_Description", "Unit"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                regex_name = convert_counter_name_to_regex(row["Counter_Name"])
                writer.writerow({
                    "Counter_Group": row.get("Counter_Group", ""),
                    "Regex": regex_name,
                    "Counter_Description": row.get("Counter_Description", ""),
                    "Unit": row.get("Unit", "")
                })

if __name__ == "__main__":
    generate_grouping_rules()

