import json

INPUT_FILE = "data/assessments.json"
OUTPUT_FILE = "data/processed_assessments.json"


def preprocess_catalog():

    with open(INPUT_FILE, "r") as f:
        data = json.load(f)

    processed = []

    for item in data:

        processed_item = {
            "name": item.get("name", ""),
            "url": item.get("link", ""),
            "description": item.get("description", ""),
            "test_type": ", ".join(item.get("test_types", [])),
            "job_levels": ", ".join(item.get("job_levels", [])),
            "languages": ", ".join(item.get("languages", [])),
            "duration": item.get("duration", ""),
            "remote_testing": item.get("remote_testing", ""),
            "adaptive": item.get("adaptive", ""),
            "skills": ", ".join(item.get("keys", [])),
        }

        # TEXT USED FOR EMBEDDINGS
        processed_item["search_text"] = f"""
        Assessment Name: {processed_item['name']}
        Description: {processed_item['description']}
        Skills: {processed_item['skills']}
        Job Levels: {processed_item['job_levels']}
        Test Type: {processed_item['test_type']}
        Languages: {processed_item['languages']}
        Duration: {processed_item['duration']}
        Remote Testing: {processed_item['remote_testing']}
        Adaptive Support: {processed_item['adaptive']}
        """

        processed.append(processed_item)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(processed, f, indent=2)

    print(f"Processed {len(processed)} assessments")


if __name__ == "__main__":
    preprocess_catalog()