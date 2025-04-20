import os
import sys
from bs4 import BeautifulSoup
from openai import OpenAI
import json
client = OpenAI()

# Set your OpenAI API key from environment variable
# openai.api_key = os.getenv("OPENAI_API_KEY")


def extract_negative_treatments(slug):
    filename = f"{slug}.html"

    # Check whether we have the file - currently, we expect there to be an html file corresponding to the case in the same directory. 
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"HTML file {filename} not found. Please verify the filename, and ensure that the relevant file is stored ")

    # Parse the HTML to extract everything in the body of the documents
    # TODO - figure out regex to reliably extract citations - see this for inspiration - https://github.com/freelawproject/citation-regexes
    with open(filename, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    text = soup.get_text().strip()

    # Prompt for GPT to analyze entire case
    # TODO - once regex is figured out, iterate over citations separately to conserve api usage
    prompt = f"""
You are the Chief Justice of the United States Supreme Court. Given the full text of a court opinion, identify any cases that are negatively treated within the text.

A negative treatment occurs when one case overrules, distinguishes, declines to apply, limits, criticizes, or otherwise undermines the holding of another case.

From the text below, return a JSON array where each object includes:
- treated_case (the name or citation of the case being treated),
- treatment_type (e.g. "Overruled", "Limited", etc.),
- excerpt (text from the opinion showing the treatment),
- explanation (your reasoning why this is negative treatment).


---TEXT START---
{text} \n
---TEXT END---
"""

    try:
        response = client.responses.create(
            model="gpt-4o",
            input=[
                {
                "role": "system",
                "content": [
                    {
                    "type": "input_text",
                    "text": "You are the Chief Justice of the United States Supreme Court"
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
                    "type": "json_schema",
                    "name": "negative_treatments",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "citations": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "treated_case": {
                                            "type": "string"
                                        },
                                        "treatment_type": {
                                            "type": "string"
                                        },
                                        "excerpt": {
                                            "type": "string"
                                        },
                                        "explanation": {
                                            "type": "string"
                                        }
                                    },
                                    "additionalProperties": False,
                                    "required": ["treated_case", "treatment_type", "excerpt", "explanation"]
                                }
                            }
                            
                        },
                        "additionalProperties": False,
                        "required": ["citations"]
                    },
                    "strict": True
                }
            },
            reasoning={},
            tools=[],
            temperature=1,
            max_output_tokens=2048,
            top_p=1,
            store=True
        )
 

         # Try to parse the JSON list from the model   
        try:
            treatments = json.loads(response.output_text)
        except json.JSONDecodeError:
            print("⚠️ GPT response was not valid JSON. Raw response:")
            print(response)
            sys.exit(1)
        
        negative_treatments_found = treatments['citations'] # list of the negative treatments identified by OpenAI API, in the json schema we supplied

            
        return negative_treatments_found
    except Exception as e:
        print(f"⚠️ Error calling OpenAI API: {e}")
        sys.exit(1)
    


if len(sys.argv) != 2:
    print("⚠️ Please provide the slug of the case as an argument.")
    print("Usage: main.py <slug>")
    sys.exit(1)

slug = sys.argv[1]
results = extract_negative_treatments(slug)
negative_treatments_count = len(results) # Count of the negative treatments
if not results:
    print(f"No negative treatments found for {slug}.")
else:
    print(f"{negative_treatments_count} Negative treatment(s) found:")
    print("-" * 80)
    for r in results:
        print(f"Treated Case: {r.get('treated_case')}")
        print(f"Treatment Type: {r.get('treatment_type')}")
        print(f"Excerpt: {r.get('excerpt')}")
        print(f"Explanation: {r.get('explanation')}")
        print("-" * 80)
