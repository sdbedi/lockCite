import os
import sys
from bs4 import BeautifulSoup
from openai import OpenAI
client = OpenAI()

# Set your OpenAI API key from environment variable
# openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_negative_treatments(slug):
    filename = f"{slug}.html"
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"HTML file '{filename}' not found.")

    with open(filename, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    text = soup.get_text().strip()

    # Prompt for GPT to analyze entire case
    prompt = f"""
You are a legal analyst. Given the full text of a court opinion, identify any cases that are negatively treated within the text.

A negative treatment occurs when one case overrules, limits, criticizes, or otherwise undermines the holding of another case.

From the text below, return a JSON array where each object includes:
- treated_case (the name or citation of the case being treated),
- treatment_type (e.g. "Overruled", "Limited", etc.),
- excerpt (text from the opinion showing the treatment),
- explanation (your reasoning why this is negative treatment).

If no negative treatment is present, return an empty array: []
---TEXT START---
{text} \n
---TEXT END---
"""

    try:
        print("prompt:")
        print(prompt)
        # response = openai.responses.create(
        #     # model="gpt-4o",
        #     # input=[
        #     #     {"role": "system", "content": "You are a legal research assistant."},
        #     #     {"role": "user", "content": prompt}
        #     # ],
        #     # temperature=0,
        #     # max_output_tokens=2048
        # )
        response = client.responses.create(
            model="gpt-4o",
            input=[
                {
                "role": "system",
                "content": [
                    {
                    "type": "input_text",
                    "text": "You are a legal research assistant"
                    }
                ]
                },
                {
                "role": "user",
                "content": [
                    {
                    "type": "input_text",
                    "text": prompt
                    }
                ]
                }
            ],
            text={
                "format": {
                "type": "text"
                }
            },
            reasoning={},
            tools=[],
            temperature=1,
            max_output_tokens=2048,
            top_p=1,
            store=True
        )
        print("GPT-4 response:")
        print(response)

        print(response.output_text)
        treatments = response.output_text
        raw_output = response["choices"][0]["message"]["content"]

        # Try to parse the JSON list from the model
        import json
        try:
            treatments = json.loads(raw_output)
        except json.JSONDecodeError:
            print("⚠️ GPT response was not valid JSON. Raw response:")
            print(raw_output)
        #     return []
        print(f"Parsed treatments: {treatments}")
        return treatments
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return []


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python case_analysis.py <slug>")
        sys.exit(1)

    slug = sys.argv[1]
    results = extract_negative_treatments(slug)

    if not results:
        print("No negative treatments found.")
    else:
        print(results)
        # for r in results:
        #     print(f"Treated Case: {r.get('treated_case')}")
        #     print(f"Treatment Type: {r.get('treatment_type')}")
        #     print(f"Excerpt: {r.get('excerpt')}")
        #     print(f"Explanation: {r.get('explanation')}")
        #     print("-" * 80)