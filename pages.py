# python
import logging
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

logger = logging.getLogger(__name__)

class SeleniumPlaygroundPage:
    # --- Locators ---
    # Top-level links
    INPUT_FORM_SUBMIT_LINK = (By.LINK_TEXT, "Input Form Submit")
    SIMPLE_FORM_DEMO_LINK = (By.LINK_TEXT, "Simple Form Demo")

    # Form fields
    NAME_FIELD = (By.ID, "name")
    EMAIL_FIELD = (By.ID, "inputEmail4")
    PASSWORD_FIELD = (By.ID, "inputPassword4")
    COMPANY_FIELD = (By.ID, "company")
    WEBSITE_FIELD = (By.ID, "websitename")
    COUNTRY_DROPDOWN = (By.NAME, "country")
    CITY_FIELD = (By.ID, "inputCity")
    ADDRESS_1_FIELD = (By.ID, "inputAddress1")
    ADDRESS_2_FIELD = (By.ID, "inputAddress2")
    STATE_FIELD = (By.ID, "inputState")
    ZIPCODE_FIELD = (By.ID, "inputZip")

    # Simple Form Demo Elements
    SINGLE_INPUT_FIELD = (By.ID, "user-message")
    GET_CHECKED_VALUE_BUTTON = (By.ID, "showInput")
    MESSAGE_DISPLAYED_LOCATOR = (By.ID, "message-one")

    # Two Input Fields
    FIRST_INPUT_FIELD = (By.ID, "sum1")
    SECOND_INPUT_FIELD = (By.ID, "sum2")
    GET_VALUES_BUTTON = (By.XPATH, "//button[contains(text(),'Get Sum') or contains(text(),'Get Total') or contains(@onclick,'total')]")
    SUM_DISPLAYED_LOCATOR = (By.ID, "addmessage")

    # Checkbox Demo
    CHECKBOX_DEMO_LINK = (By.LINK_TEXT, "Checkbox Demo")
    SINGLE_CHECKBOX = (By.ID, "isAgeSelected")
    SINGLE_CHECKBOX_SUCCESS_MESSAGE = (By.ID, "txtAge")

    # Buttons
    SUBMIT_BUTTON = (By.XPATH, '//*[@id="seleniumform"]/div[6]/button')

    # Messages
    SUCCESS_MESSAGE = (By.CSS_SELECTOR, ".success-msg p")

    def __init__(self, driver, timeout=20):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    # --- Internal helpers ---
    def _js_click(self, element):
        try:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            self.driver.execute_script("arguments[0].click();", element)
        except WebDriverException:
            element.click()

    def _wait_for_element_text(self, locator, expected_text, timeout=None, contains=False):
        wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        def _predicate(driver):
            try:
                el = driver.find_element(*locator)
                text = el.get_attribute("innerText") or el.text or ""
                text = text.strip()
                if contains:
                    return text if expected_text in text else False
                return text if text == expected_text else False
            except Exception:
                return False
        return wait.until(_predicate)

    def _safe_save_screenshot(self, name):
        try:
            self.driver.save_screenshot(name)
        except Exception:
            logger.exception("Failed to save screenshot %s", name)

    # --- Navigation Methods ---
    def go_to_input_form_submit(self):
        logger.info("Clicking on 'Input Form Submit'")
        try:
            try:
                el = self.wait.until(EC.element_to_be_clickable(self.INPUT_FORM_SUBMIT_LINK))
            except Exception:
                el = self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'input form submit')]")
                ))

            try:
                el.click()
            except Exception:
                self._js_click(el)

            # Switch to new window/tab if opened
            if len(self.driver.window_handles) > 1:
                current = self.driver.current_window_handle
                for h in self.driver.window_handles:
                    if h != current:
                        self.driver.switch_to.window(h)
                        break

            # Wait until either the URL contains the expected path OR the NAME_FIELD is visible
            WebDriverWait(self.driver, 30).until(
                lambda d: ("/input-form-submit" in d.current_url)
                or (len(d.find_elements(*self.NAME_FIELD)) > 0 and d.find_element(*self.NAME_FIELD).is_displayed())
            )

            logger.info(f"Navigation validated: {self.driver.current_url}")
        except TimeoutException:
            logger.exception("Failed to navigate to Input Form Submit")
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            try:
                self.driver.save_screenshot(f"screenshots/go_to_input_form_submit_failure_{ts}.png")
            except Exception:
                logger.debug("Screenshot save failed.")
            try:
                with open(f"screenshots/go_to_input_form_submit_failure_{ts}.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
            except Exception:
                logger.debug("Saving page source failed.")
            raise

    def go_to_simple_form_demo(self):
        logger.info("Clicking on Simple Form Demo")
        try:
            el = self.wait.until(EC.element_to_be_clickable(self.SIMPLE_FORM_DEMO_LINK))
            try:
                el.click()
            except Exception:
                self._js_click(el)

            WebDriverWait(self.driver, 30).until(EC.url_contains("/simple-form-demo"))
            logger.info(f"URL validated: {self.driver.current_url}")
        except TimeoutException:
            logger.exception("Failed to navigate to Simple Form Demo")
            self._safe_save_screenshot("screenshots/go_to_simple_form_demo_failure.png")
            raise

    def go_to_checkbox_demo(self):
        logger.info("Clicking on Checkbox Demo")
        try:
            el = self.wait.until(EC.element_to_be_clickable(self.CHECKBOX_DEMO_LINK))
            try:
                el.click()
            except Exception:
                self._js_click(el)

            self.wait.until(EC.url_contains("/checkbox-demo"))
            self.wait.until(EC.visibility_of_element_located(self.SINGLE_CHECKBOX))
            logger.info(f"URL and Checkbox Demo page validated: {self.driver.current_url}")
        except TimeoutException:
            logger.exception("Failed to navigate to Checkbox Demo")
            self._safe_save_screenshot("screenshots/go_to_checkbox_demo_failure.png")
            raise

    # --- Interaction Methods (Form Submit) ---
    def fill_form(self, data):
        logger.info("Filling the input form with provided data.")
        self.wait.until(EC.visibility_of_element_located(self.NAME_FIELD)).send_keys(data.get("name", ""))
        self.driver.find_element(*self.EMAIL_FIELD).send_keys(data.get("email", ""))
        self.driver.find_element(*self.PASSWORD_FIELD).send_keys(data.get("password", ""))
        self.driver.find_element(*self.COMPANY_FIELD).send_keys(data.get("company", ""))
        self.driver.find_element(*self.WEBSITE_FIELD).send_keys(data.get("website", ""))

        try:
            country_dropdown = Select(self.driver.find_element(*self.COUNTRY_DROPDOWN))
            if data.get("country"):
                country_dropdown.select_by_visible_text(data.get("country"))
        except Exception:
            logger.debug("Country selection failed or not present; continuing.")

        self.driver.find_element(*self.CITY_FIELD).send_keys(data.get("city", ""))
        self.driver.find_element(*self.ADDRESS_1_FIELD).send_keys(data.get("address1", ""))
        self.driver.find_element(*self.ADDRESS_2_FIELD).send_keys(data.get("address2", ""))
        self.driver.find_element(*self.STATE_FIELD).send_keys(data.get("state", ""))
        self.driver.find_element(*self.ZIPCODE_FIELD).send_keys(data.get("zipcode", ""))

    def click_submit_button(self):
        logger.info("Clicking the 'Submit' button.")
        try:
            btn = self.wait.until(EC.element_to_be_clickable(self.SUBMIT_BUTTON))
            try:
                btn.click()
            except Exception:
                self._js_click(btn)
        except TimeoutException:
            logger.exception("Submit button not clickable")
            self._safe_save_screenshot("screenshots/click_submit_button_failure.png")
            raise

    # --- Interaction Methods (Simple Form Demo) ---
    def enter_message(self, message):
        logger.info(f"Entering message: '{message}' into Single Input Field.")
        try:
            el = self.wait.until(EC.visibility_of_element_located(self.SINGLE_INPUT_FIELD))
            el.clear()
            el.send_keys(message)
        except TimeoutException:
            logger.exception("Single input field not visible")
            self._safe_save_screenshot("screenshots/enter_message_failure.png")
            raise

    def click_get_checked_value(self):
        logger.info("Clicking 'Get Checked Value' button.")
        try:
            btn = self.wait.until(EC.element_to_be_clickable(self.GET_CHECKED_VALUE_BUTTON))
            try:
                btn.click()
            except Exception:
                self._js_click(btn)
        except TimeoutException:
            logger.exception("Get Checked Value button not clickable")
            self._safe_save_screenshot("screenshots/click_get_checked_value_failure.png")
            raise

    # --- Two Input Fields (enter & click) ---
    def enter_values_for_sum(self, a, b):
        logger.info("Entering values for sum: %s, %s", a, b)
        try:
            f1 = self.wait.until(EC.visibility_of_element_located(self.FIRST_INPUT_FIELD))
            f2 = self.wait.until(EC.visibility_of_element_located(self.SECOND_INPUT_FIELD))
            f1.clear()
            f1.send_keys(str(a))
            f2.clear()
            f2.send_keys(str(b))
        except TimeoutException:
            logger.exception("Sum input fields not visible")
            self._safe_save_screenshot("screenshots/enter_values_for_sum_failure.png")
            raise

    def click_get_values_button(self):
        logger.info("Clicking Get Values (sum) button.")
        try:
            btn = self.wait.until(EC.element_to_be_clickable(self.GET_VALUES_BUTTON))
            try:
                btn.click()
            except Exception:
                self._js_click(btn)
        except TimeoutException:
            logger.exception("Get values button not clickable")
            self._safe_save_screenshot("screenshots/click_get_values_button_failure.png")
            raise

    # --- Interaction Methods (Checkbox Demo) ---
    def click_single_checkbox(self):
        logger.info("Clicking single checkbox.")
        try:
            cb = self.wait.until(EC.element_to_be_clickable(self.SINGLE_CHECKBOX))
            try:
                cb.click()
            except Exception:
                self._js_click(cb)
        except TimeoutException:
            logger.exception("Single checkbox not clickable")
            self._safe_save_screenshot("screenshots/click_single_checkbox_failure.png")
            raise

    # --- Validation Methods ---
    def get_html5_validation_message(self, locator):
        """Retrieves the HTML5 validation message from an input element via JavaScript."""
        try:
            element = self.driver.find_element(*locator)
            return self.driver.execute_script("return arguments[0].validationMessage;", element)
        except Exception:
            logger.exception("Failed to get HTML5 validation message")
            return ""

    def validate_message_displayed(self, expected_message):
        logger.info(f"Validating message displayed: '{expected_message}'")
        try:
            try:
                displayed_text = self._wait_for_element_text(self.MESSAGE_DISPLAYED_LOCATOR, expected_message, timeout=20, contains=True)
            except TimeoutException:
                alt_locators = [
                    (By.ID, "display"),
                    (By.ID, "message"),
                    (By.CSS_SELECTOR, ".message"),
                    (By.XPATH, f"//*[contains(text(), '{expected_message}')]")
                ]
                displayed_text = None
                for loc in alt_locators:
                    try:
                        displayed_text = self._wait_for_element_text(loc, expected_message, timeout=8, contains=True)
                        if displayed_text:
                            break
                    except TimeoutException:
                        continue

            if not displayed_text:
                logger.error("Expected message not found on page")
                self._safe_save_screenshot("screenshots/validate_message_displayed_failure.png")
                raise AssertionError(f"Expected message not displayed: {expected_message}")

            assert expected_message in displayed_text, f"Message validation failed. Expected to contain: '{expected_message}', Found: '{displayed_text}'"
            logger.info(f"Message validated successfully: '{displayed_text}'")
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"Validation failed for message '{expected_message}'. Error: {e}")
            self._safe_save_screenshot("screenshots/validate_message_displayed_exception.png")
            raise

    def validate_submission_success(self, expected_message):
        logger.info(f"Validating success message: '{expected_message}'")
        try:
            try:
                displayed_text = self._wait_for_element_text(self.SUCCESS_MESSAGE, expected_message, timeout=20, contains=True)
            except TimeoutException:
                alt_locators = [
                    (By.CSS_SELECTOR, ".alert-success"),
                    (By.XPATH, f"//*[contains(text(), '{expected_message}')]")
                ]
                displayed_text = None
                for loc in alt_locators:
                    try:
                        displayed_text = self._wait_for_element_text(loc, expected_message, timeout=8, contains=True)
                        if displayed_text:
                            break
                    except TimeoutException:
                        continue

            if not displayed_text:
                logger.error("Expected success message not found on page")
                self._safe_save_screenshot("screenshots/validate_submission_success_failure.png")
                raise AssertionError(f"Success message not displayed: {expected_message}")

            assert expected_message in displayed_text, f"Success message validation failed. Expected: '{expected_message}', Found: '{displayed_text}'"
            logger.info(f"Success message validated successfully: '{displayed_text}'")
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"Validation failed for success message. Error: {e}")
            self._safe_save_screenshot("screenshots/validate_submission_success_exception.png")
            raise

    def validate_sum_displayed(self, expected_sum):
        logger.info(f"Validating sum displayed: '{expected_sum}'")
        try:
            try:
                displayed_text = self._wait_for_element_text(self.SUM_DISPLAYED_LOCATOR, expected_sum, timeout=15, contains=True)
            except TimeoutException:
                alt_locators = [
                    (By.ID, "displayvalue"),
                    (By.CSS_SELECTOR, ".sum-result"),
                    (By.XPATH, f"//*[contains(text(), '{expected_sum}')]")
                ]
                displayed_text = None
                for loc in alt_locators:
                    try:
                        displayed_text = self._wait_for_element_text(loc, expected_sum, timeout=6, contains=True)
                        if displayed_text:
                            break
                    except TimeoutException:
                        continue

            if not displayed_text:
                logger.error("Expected sum not found on page")
                self._safe_save_screenshot("screenshots/validate_sum_displayed_failure.png")
                raise AssertionError(f"Sum not displayed: {expected_sum}")

            assert expected_sum in displayed_text, f"Sum validation failed. Expected: '{expected_sum}', Found: '{displayed_text}'"
            logger.info(f"Sum validated successfully: '{displayed_text}'")
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"Validation failed for sum '{expected_sum}'. Error: {e}")
            self._safe_save_screenshot("screenshots/validate_sum_displayed_exception.png")
            raise

    def validate_single_checkbox_success_message(self):
        expected_message = "Success - Check box is checked"
        logger.info(f"Validating single checkbox success message: '{expected_message}'")
        try:
            displayed_text = self._wait_for_element_text(self.SINGLE_CHECKBOX_SUCCESS_MESSAGE, expected_message, timeout=12, contains=True)
            if not displayed_text:
                logger.error("Expected checkbox message not found on page")
                self._safe_save_screenshot("screenshots/validate_single_checkbox_failure.png")
                raise AssertionError(f"Checkbox success message not displayed: {expected_message}")
            assert expected_message in displayed_text, f"Checkbox success message validation failed. Expected: '{expected_message}', Found: '{displayed_text}'"
            logger.info(f"Single checkbox success message validated successfully: '{displayed_text}'")
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"Validation failed for checkbox success message. Error: {e}")
            self._safe_save_screenshot("screenshots/validate_single_checkbox_exception.png")
            raise
