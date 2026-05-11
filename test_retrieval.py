from rag.retriever import retrieve_assessments

query = """
Hiring senior backend Java engineer
with Spring Boot, SQL, AWS and Docker
"""

results = retrieve_assessments(query)

for idx, item in enumerate(results, start=1):

    print("\n" + "=" * 50)

    print(f"RESULT {idx}")
    print("NAME:", item["name"])
    print("TYPE:", item["test_type"])
    print("URL:", item["url"])