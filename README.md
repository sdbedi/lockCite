# Negative Case Treatment Analyzer

This script analyzes legal court opinions to identify and extract instances of negative case treatments, where one case overrules, criticizes, or otherwise undermines the holding of another case.

## Description

The Negative Case Treatment Analyzer uses OpenAI's GPT-4o model via API to analyze court opinions and identify any cases that receive negative treatment within the text. For each identified negative treatment, the script returns:

- The name or citation of the case being treated
- The type of treatment (e.g., "Overruled", "Limited", "Distinguished")
- An excerpt from the opinion showing the treatment
- An explanation of why this constitutes negative treatment

If no negative treatments are found, the script will print "No negative treatments found."

## Installation

1. Clone this repository to your local machine
2. Install the required dependencies:

```bash
pip install beautifulsoup4 openai
```

3. Set up your OpenAI API key as an environment variable:

```bash
# For Linux/macOS
export OPENAI_API_KEY="your-api-key-here"

# For Windows (Command Prompt)
set OPENAI_API_KEY=your-api-key-here

# For Windows (PowerShell)
$env:OPENAI_API_KEY="your-api-key-here"
```

## Usage

The script expects an HTML file of a court opinion with the same name as the slug you provide:

```bash
python main.py <slug>
```

For example, if you run:

```bash
python main.py little
```

The script will look for a file named `little.html` in the same directory and analyze it for negative treatments.

## Output

The script will output the negative treatments found, including:
- The total count of negative treatments
- For each treatment:
  - The case being treated
  - The type of treatment
  - An excerpt showing the treatment
  - An explanation of the negative treatment

## TODOs

1. Implement regex patterns to reliably extract citations (see reference to [citation-regexes](https://github.com/freelawproject/citation-regexes) in the code)
2. Optimize API usage by iterating over individual citations once regex extraction is implemented
3. Add support for different file formats beyond HTML
4. Implement error handling for API rate limits and token limitations
5. Add functionality to save results to a file
6. Add tests to verify accuracy of treatment identification
7. Explore different LLM models

## Requirements

- Python 3.6+
- BeautifulSoup4
- OpenAI Python client
- OpenAI API key

