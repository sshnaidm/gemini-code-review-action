#!/usr/bin/env python3
import argparse
import os
import sys

from google import genai
from google.genai import types


def read_prompt_from_file(prompt_file_path):
    """Reads the prompt from the specified file."""
    try:
        with open(prompt_file_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Prompt file not found at {prompt_file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading prompt file: {e}")
        sys.exit(1)


GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY is None or GEMINI_API_KEY == "":
    print("GEMINI_API_KEY environment variable is not set")
    sys.exit(1)

MODEL = os.environ.get("MODEL")
MAX_OUTPUT = int(os.environ.get("MAX_OUTPUT", "0") or "0")
COMMIT_TITLE = os.environ.get("COMMIT_TITLE", "")
COMMIT_BODY = os.environ.get("COMMIT_BODY", "")
THINKING = os.environ.get("THINKING")
TEMPERATURE = os.environ.get("TEMPERATURE")
TOP_P = os.environ.get("TOP_P")


def call_api(prompt_str):
    """Calls the Gemini Code Assistant API with the provided prompt."""
    params = {}
    persona = """
You are a code review assistant. You are helping to review code changes in a pull request."""
    params["system_instruction"] = persona

    if THINKING:
        if THINKING.isdigit():
            params["thinking_config"] = types.ThinkingConfig(thinking_budget=int(THINKING))
        elif THINKING.lower() == "off":
            params["thinking_config"] = types.ThinkingConfig(thinking_budget=0)
        elif THINKING.lower() == "dynamic":
            params["thinking_config"] = types.ThinkingConfig(thinking_budget=-1)
        else:
            print(f"Invalid thinking mode: {THINKING}. Must be 'off', 'dynamic', or a number.")
            sys.exit(1)
    if TEMPERATURE is not None and TEMPERATURE != "":
        try:
            params["temperature"] = float(TEMPERATURE)
        except ValueError:
            print(f"Invalid temperature value: {TEMPERATURE}. Must be a float number.")
            sys.exit(1)
    if TOP_P is not None and TOP_P != "":
        try:
            params["top_p"] = float(TOP_P)
        except ValueError:
            print(f"Invalid top_p value: {TOP_P}. Must be a float number.")
            sys.exit(1)
    if MAX_OUTPUT:
        try:
            params["max_output_tokens"] = int(MAX_OUTPUT)
        except ValueError:
            print(f"Invalid max length value: {MAX_OUTPUT}. Must be an integer.")
            sys.exit(1)
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt_str,
            config=types.GenerateContentConfig(**params)
        )
        review = response.text
        return review
    except Exception as e:
        print(f"An unexpected error occurred in Client call: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Call Gemini Code Assistant API")
    parser.add_argument("--diff-file", type=str, help="Path to the diff file", required=True)
    parser.add_argument("--prompt", type=str, help="The prompt for code review")
    parser.add_argument("--prompt-file", type=str, help="Path to a file containing the prompt")
    parser.add_argument(
        "--context-files",
        type=str,
        help="Comma-separated list of paths to context files",
    )
    args = parser.parse_args()
    default_prompt = """
Instructions:
##
Review the attached code and find bugs and issues in the code. Attached diff for review and original files.
Added lines are marked with "+" and removed lines are marked with "-". Lines that are not changed are not marked.
Suggest improvements for the change in the file.
Write exact lines of files that need to be changed. Don't explain the purpose of the original file.
Do not suggest descriptive variable name.
Write output in markdown format.
##
"""
    if args.prompt_file:
        prompt = read_prompt_from_file(args.prompt_file)
    elif args.prompt:
        prompt = args.prompt
    else:
        prompt = default_prompt

    diff_file = args.diff_file
    # Add content of diff file to prompt
    with open(diff_file, "r") as f:
        diff_content = f.read()
    prompt = f"## These are changes diff for the code:\n```{diff_content}\n```\n{prompt}"

    if args.context_files:
        context_files_text = ""
        context_files_list = args.context_files.split(",")
        for context_file in context_files_list:
            try:
                with open(context_file, "r") as f:
                    context_files_text += f"# This is original file {context_file} before changes:\n```{f.read()}\n```"
            except FileNotFoundError:
                # print it to stderr
                sys.stderr.write(f"Warning: Context file {context_file} not found. Skipping.\n")
        prompt = f"## These are origin files before changes:\n{context_files_text}\n{prompt}"
    prompt = f"## This is commit title:\n{COMMIT_TITLE}\n## This is commit body:\n{COMMIT_BODY}\n{prompt}"
    with open("/tmp/prompt.txt", "w") as f:
        f.write(prompt)

    review = call_api(prompt)
    print(review)


if __name__ == "__main__":
    main()
