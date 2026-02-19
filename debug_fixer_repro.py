from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
import os

# Mock LLM (we just want to test template formatting)
# But we need the real class structure
# We can't easily mock the API call without creds, but we can test the PROMPT formatting part
# which happens locally before the API call.

try:
    system_msg_template = (
        "You are an expert autonomous software engineer. "
    )
    
    user_msg_template = (
        "FilePath: {file_path}\n"
        "Error Type: {error_type}\n"
        "Error Message: {error_message}\n"
        "Line Number: {line_number}\n\n"
        "Current File Content:\n"
        "```python\n{content}\n```\n\n"
        "Please provide the corrected file content."
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_msg_template),
        ("human", user_msg_template)
    ])
    
    # Problematic content containing braces
    content = 'assert validate({"key": "value"}) is True'
    error_message = "Input to ChatPromptTemplate is missing variables {'\"key\"'}"
    
    print("Attempting to format prompt...")
    messages = prompt.format_messages(
        file_path="test_validator.py",
        error_type="LINTING",
        error_message=error_message,
        line_number=1,
        content=content
    )
    
    print("Prompt formatted successfully!")
    print(messages[1].content)

except Exception as e:
    print(f"FAILED with error: {e}")
