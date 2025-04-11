import os
import sys
import re
from bs4 import BeautifulSoup
from collections import namedtuple
from openai import OpenAI
import json
client = OpenAI()


NegativeTreatment = namedtuple('NegativeTreatment', ['treated_case', 'treatment_type', 'context', 'explanation'])

def extract_negative_treatments(slug):
    filename = f"{slug}.html"
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"HTML file for slug '{slug}' not found.")

    with open(filename, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    text = soup.get_text()
    print(text[:1000])  # Print the first 1000 characters for debugging

    # Regex pattern to match legal citations
    citation_pattern = r'\b\d{1,3}\s+[A-Z][a-zA-Z\.]*\s+\d{1,4}\b'
    citations = set(re.findall(citation_pattern, text))
    print(f"Found {len(citations)} citations.")
    print (f"Citations: {citations}")

    prompt = f"""
You are a legal analyst. Given the following excerpt from a court opinion, determine whether the cited case "{citation}" is treated negatively (e.g., overruled, limited, criticized, distinguished).

Context:
\"\"\"
{context}
\"\"\"

Respond in JSON with keys: 
- "is_negative" (true/false), 
- "treatment_type" (e.g., Overruled, Distinguished, etc.), 
- "explanation" (a brief explanation).

If the treatment is not negative, use:
- "is_negative": false
- "treatment_type": null
- "explanation": "No negative treatment detected."
"""

    response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a legal assistant."},
        {"role": "user", "content": prompt}
        ],
                    temperature=0
                )
    answer = response['choices'][0]['message']['content']
    result = json.loads(answer)


    # negative_treatments = []

    # for citation in citations:
    #     start = 0
    #     while start < len(text):
    #         start = text.find(citation, start)
    #         if start == -1:
    #             break

    #         window_start = max(0, start - 500)
    #         window_end = min(len(text), start + len(citation) + 500)
    #         context = text[window_start:window_end].strip()

#             # GPT-4 prompt to analyze context
#             prompt = f"""
# You are a legal analyst. Given the following excerpt from a court opinion, determine whether the cited case "{citation}" is treated negatively (e.g., overruled, limited, criticized, distinguished).

# Context:
# \"\"\"
# {context}
# \"\"\"

# Respond in JSON with keys: 
# - "is_negative" (true/false), 
# - "treatment_type" (e.g., Overruled, Distinguished, etc.), 
# - "explanation" (a brief explanation).

# If the treatment is not negative, use:
# - "is_negative": false
# - "treatment_type": null
# - "explanation": "No negative treatment detected."
# """

#             try:
#                 response = openai.ChatCompletion.create(
#                     model="gpt-4",
#                     messages=[
#                         {"role": "system", "content": "You are a legal assistant."},
#                         {"role": "user", "content": prompt}
#                     ],
#                     temperature=0
#                 )
#                 answer = response['choices'][0]['message']['content']
#                 import json
#                 result = json.loads(answer)

#                 if result.get("is_negative"):
#                     negative_treatments.append(NegativeTreatment(
#                         treated_case=citation,
#                         treatment_type=result.get("treatment_type"),
#                         context=context,
#                         explanation=result.get("explanation")
#                     ))
#             except Exception as e:
#                 print(f"Error analyzing {citation}: {e}")

#             start += len(citation)

#     return negative_treatments

  
    response = client.responses.create(
        model="gpt-4o",
        input="Write a one-sentence bedtime story about a unicorn."
    )

    print(response.output_text)
    return response.output_text



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <slug>")
        sys.exit(1)

    slug = sys.argv[1]
    results = extract_negative_treatments(slug)

    if not results:
        print("No negative treatments found.")
    else:
        for r in results:
            print(f"Treated Case: {r.treated_case}")
            print(f"Treatment Type: {r.treatment_type}")
            print(f"Context: {r.context}")
            print(f"Explanation: {r.explanation}")
            print("-" * 80)