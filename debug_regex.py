import re
import xml.etree.ElementTree as ET

xml_content = """<?xml version="1.0" encoding="utf-8"?><testsuites name="pytest tests"><testsuite name="pytest" errors="1" failures="0" skipped="0" tests="1" time="0.276" timestamp="2026-02-19T09:01:18.501019+00:00" hostname="bbca980fcaed"><testcase classname="" name="tests.test_validator" time="0.000"><error message="collection failure">/usr/local/lib/python3.11/site-packages/_pytest/python.py:507: in importtestmodule
    mod = import_path(
/usr/local/lib/python3.11/site-packages/_pytest/pathlib.py:587: in import_path
    importlib.import_module(module_name)
/usr/local/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
&lt;frozen importlib._bootstrap&gt;:1204: in _gcd_import
    ???
&lt;frozen importlib._bootstrap&gt;:1176: in _find_and_load
    ???
&lt;frozen importlib._bootstrap&gt;:1147: in _find_and_load_unlocked
    ???
&lt;frozen importlib._bootstrap&gt;:690: in _load_unlocked
    ???
/usr/local/lib/python3.11/site-packages/_pytest/assertion/rewrite.py:197: in exec_module
    exec(co, module.__dict__)
tests/test_validator.py:1: in &lt;module&gt;
    from src.validator import validate
E     File "/app/src/validator.py", line 1
E       def validate(data)
E                         ^
E   SyntaxError: expected ':'</error></testcase></testsuite></testsuites>"""

root = ET.fromstring(xml_content)
suites = root.findall("testsuite") if root.tag == "testsuites" else [root]

for suite in suites:
    for testcase in suite.iter("testcase"):
        failure = testcase.find("failure")
        error = testcase.find("error")
        
        if failure is not None or error is not None:
            elem = failure if failure is not None else error
            msg = elem.attrib.get("message", "")
            file_path = testcase.attrib.get("file", "unknown")
            line = testcase.attrib.get("line", "0")
            
            print(f"Original file_path: {file_path}")
            print(f"Message: {msg}")
            print(f"Text content: {elem.text}")
            
            search_text = f"{msg}\n{elem.text or ''}"
            
            if file_path == "unknown" and search_text:
                # Look for File "/app/src/validator.py", line 1
                match = re.search(r'File "([^"]+)", line (\d+)', search_text)
                if match:
                    file_path = match.group(1)
                    line = match.group(2)
                    print(f"Matched file: {file_path}")
                    print(f"Matched line: {line}")
                else:
                    print("No regex match found.")
