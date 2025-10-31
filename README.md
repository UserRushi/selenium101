# Selenium Assignment: LambdaTest Playground Automation

This repo contains Selenium tests for 3 scenarios on LambdaTest's Selenium Playground.

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Run tests: `pytest test_scenarios.py -v` (or `pytest test_scenarios.py::test_selenium_playground[1] -v` for specific scenario)
3. Outputs:
   - Screenshots: In `screenshots/` folder.
   - Logs: Console and file (via logging).
   - Videos: In `videos/` (screen recordings; enable pyautogui in conftest.py).
   - Network/Console logs: Printed in test output.

## Locators Used (At Least 3 Per Test)
- Scenario 1: ID (message box), XPath (button), CSS (validation).
- Scenario 2: CSS (slider container), XPath (input), ID (value output).
- Scenario 3: Name (submit), XPath (error/select), ID/CSS/Class (fields/validation).

## Capabilities
- Network/Console logs enabled via Chrome prefs.
- Screenshots on steps/failures.
- Video via PyAutoGUI (local screen record).

For LambdaTest cloud runs, update driver with their capabilities (e.g., via `lt://` hub).

## Repo Structure