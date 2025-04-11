import base64
from openai import OpenAI
import sys
import os
client = OpenAI()

if len(sys.argv) != 2:
    print("Usage: python case_analysis.py <slug>")
    sys.exit(1)

slug = sys.argv[1]

with open("little.html", "rb") as f:
    data = f.read()

base64_string = base64.b64encode(data).decode("utf-8")

response = client.responses.create(
    model="gpt-4o",
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_file",
                    "filename": "little.html",
                    "file_data": f"data:application/pdf;base64,{base64_string}",
                },
                {
                    "type": "input_text",
                    "text": "What is the first dragon in the book?",
                },
            ],
        },
    ]
)

print(response.output_text)