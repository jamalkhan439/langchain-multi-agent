from src.pipelines.pipeline import run_research_pipeline

topic = "Impact of AI on the job market 2026"

result = run_research_pipeline(topic)

print("\n========== RESEARCH REPORT ==========\n")
print(result["report"])

print("\n========== CRITIC FEEDBACK ==========\n")
print(result["feedback"])