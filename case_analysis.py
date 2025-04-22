import os
import sys
import json
import logging
from pathlib import Path
from bs4 import BeautifulSoup
from openai import OpenAI
from typing import List, Dict

client = OpenAI()
MODEL_NAME = "gpt-4o"
MAX_TOKENS = 2048

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

def load_case_text(slug: str) -> str:
    filename = Path(f"{slug}.html")
    if not filename.is_file():
        raise FileNotFoundError(f"HTML file '{filename}' not found.")
    with open(filename, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    return soup.get_text().strip()


def build_prompt(case_text: str) -> str:
    return f"""
You are the Chief Justice of the United States Supreme Court. Given the full text of a court opinion, identify any cases that are negatively treated within the text.

A negative treatment occurs when one case overrules, distinguishes, declines to apply, limits, criticizes, or otherwise undermines the holding of another case.

From the text below, return a JSON array where each object includes:
- treated_case (the name or citation of the case being treated),
- treatment_type (e.g. "Overruled", "Limited", etc.),
- excerpt (text from the opinion showing the treatment),
- explanation (your reasoning why this is negative treatment).

---TEXT START---
{case_text}
---TEXT END---
""".strip()


def call_openai_for_analysis(prompt: str) -> List[Dict]:
    logging.info("Calling OpenAI API...")
    try:
        response = client.responses.create(
            model=MODEL_NAME,
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
        raise RuntimeError(f"OpenAI API call failed: {e}")


def save_results(slug: str, results: List[Dict]) -> Path:
    output_path = Path(f"{slug}_negative_treatments.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    logging.info(f"Results saved to {output_path}")
    return output_path


def extract_negative_treatments(slug: str) -> List[Dict]:
    logging.info(f"Processing case: {slug}")
    case_text = load_case_text(slug)
    prompt = build_prompt(case_text)
    results = call_openai_for_analysis(prompt)
    save_results(slug, results)
    return results


def main():
    if len(sys.argv) != 2:
        print("⚠️ Please provide the slug of the case as an argument.")
        print("Usage: python case_analysis.py <slug>")
        sys.exit(1)

    slug = sys.argv[1]
    try:
        results = extract_negative_treatments(slug)
        if not results:
            print(f"No negative treatments found for '{slug}'.")
        else:
            print(f"{len(results)} Negative treatment(s) found:")
            print("-" * 80)
            for r in results:
                print(f"Treated Case   : {r.get('treated_case')}")
                print(f"Treatment Type : {r.get('treatment_type')}")
                print(f"Excerpt        : {r.get('excerpt')}")
                print(f"Explanation    : {r.get('explanation')}")
                print("-" * 80)
    except Exception as e:
        logging.error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()