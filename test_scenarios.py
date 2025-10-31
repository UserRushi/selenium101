# python
import pytest
import logging
import os
from datetime import datetime
import time

from pages import SeleniumPlaygroundPage

logger = logging.getLogger(__name__)

# --- Scenario Functions ---
def scenario_1_simple_form_demo(page: SeleniumPlaygroundPage):
    message_to_enter = "Welcome to LambdaTest"
    logger.info(f"Executing Scenario 1: Simple Form Demo with message '{message_to_enter}'")
    try:
        page.go_to_simple_form_demo()
        page.enter_message(message_to_enter)
        page.click_get_checked_value()
        page.validate_message_displayed(message_to_enter)
        logger.info("Scenario 1 completed successfully.")
    except Exception as e:
        logger.error(f"Scenario 1 failed: {e}")
        raise

def scenario_2_two_input_fields(page: SeleniumPlaygroundPage):
    value_a = "10"
    value_b = "5"
    expected_sum = str(int(value_a) + int(value_b))
    logger.info(f"Executing Scenario 2: Two Input Fields with A='{value_a}' B='{value_b}'")
    page.go_to_simple_form_demo()
    page.enter_values_for_sum(value_a, value_b)
    page.click_get_values_button()
    page.validate_sum_displayed(expected_sum)
    logger.info("Scenario 2 completed successfully.")

def scenario_3_input_form_submit(page: SeleniumPlaygroundPage):
    """
    Test Scenario 3: Input Form Submit, validate error and success messages.
    """
    logger.info("Executing Scenario 3: Input Form Submit")
    
    # Test 1: Validate HTML5 validation message on empty form submit
    try:
        page.go_to_input_form_submit()
        page.click_submit_button()
        
        expected_error_message = "Please fill out this field."
        actual_error_message = page.get_html5_validation_message(page.NAME_FIELD)
        assert expected_error_message == actual_error_message, f"Empty form error message validation failed. Expected: '{expected_error_message}', Found: '{actual_error_message}'"
        logger.info("Empty form submission error message validated successfully.")
    
    except Exception as e:
        logger.error(f"Scenario 3 (Error Validation) failed: {e}")
        raise
    
    # Test 2: Fill form and validate success message
    try:
        form_data = {
            "name": "John Doe",
            "email": "john.doe@test.com",
            "password": "Password123",
            "company": "LambdaTest",
            "website": "https://www.lambdatest.com",
            "country": "United States",
            "city": "San Francisco",
            "address1": "123 Main St",
            "address2": "Apt 4B",
            "state": "California",
            "zipcode": "94107"
        }
        page.fill_form(form_data)
        page.click_submit_button()
        
        expected_success_message = "Thanks for contacting us, we will get back to you shortly."
        page.validate_submission_success(expected_success_message)
        logger.info("Successful form submission message validated.")
        logger.info("Scenario 3 completed successfully.")
    
    except Exception as e:
        logger.error(f"Scenario 3 (Success Validation) failed: {e}")
        raise


# --- Pytest Test Function ---
@pytest.mark.parametrize("scenario_number", [1, 2, 3], ids=[
    "Scenario_1_SimpleForm",
    "Scenario_2_TwoInputs",
    "Scenario_3_InputFormSubmit"
])
def test_selenium_playground_scenarios(scenario_number, driver):
    page = SeleniumPlaygroundPage(driver)
    
    driver.get("https://www.lambdatest.com/selenium-playground")
    logger.info(f"Starting Test Scenario {scenario_number} from Selenium Playground.")
    
    test_name = f"scenario_{scenario_number}"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    driver.save_screenshot(f'screenshots/start_{test_name}_{timestamp}.png')

    if scenario_number == 1:
        scenario_1_simple_form_demo(page)
    elif scenario_number == 2:
        scenario_2_two_input_fields(page)
    elif scenario_number == 3:
        scenario_3_input_form_submit(page)
    else:
        pytest.fail(f"Invalid scenario number: {scenario_number}")

    driver.save_screenshot(f'screenshots/end_{test_name}_{timestamp}.png')
    logger.info(f"Finished Test Scenario {scenario_number} successfully.")
