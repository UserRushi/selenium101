# conftest.py
import pytest
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Load credentials from .env
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create folders if they don't exist
os.makedirs('screenshots', exist_ok=True)
os.makedirs('videos', exist_ok=True)
os.makedirs('artifacts', exist_ok=True)


def _timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _save_artifacts_for_test(driver, test_name):
    """Save screenshot and page source to artifacts/ for debugging failures."""
    ts = _timestamp()
    base = f"{test_name}_{ts}"
    png_path = None
    html_path = None
    try:
        png_path = os.path.join("artifacts", f"{base}.png")
        driver.save_screenshot(png_path)
    except Exception as e:
        logger.debug(f"Failed to save screenshot: {e}")

    try:
        html_path = os.path.join("artifacts", f"{base}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
    except Exception as e:
        logger.debug(f"Failed to save page source: {e}")

    logger.info(f"[ARTIFACTS] screenshot: {png_path}, page_source: {html_path}")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item):
    """Hook to capture the test outcome for use in the fixture teardown."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call":
        item.runtest_report = report
    return report


@pytest.fixture(scope='function')
def driver(request):
    """Fixture to set up and tear down the WebDriver.

    - When USE_LAMBDATEST=true, creates a remote session on LambdaTest using ChromeOptions
      and options.set_capability(...) (no desired capabilities).
    - Otherwise, uses local Chrome (webdriver-manager).
    On failure, saves artifacts and marks LambdaTest session status when applicable.
    """
    use_lambdatest = os.getenv('USE_LAMBDATEST', 'false').lower() == 'true'
    driver = None

    if use_lambdatest:
        username = os.getenv('LT_USERNAME')
        access_key = os.getenv('LT_ACCESS_KEY')

        if not username or not access_key:
            raise ValueError("Set LT_USERNAME and LT_ACCESS_KEY in environment (.env or GitHub Secrets)")

        lt_hub = f"https://{username}:{access_key}@hub.lambdatest.com/wd/hub"

        # Read matrix/env overrides if present
        lt_browser = os.getenv('LT_BROWSER', 'chrome')
        lt_browser_version = os.getenv('LT_BROWSER_VERSION', 'latest')
        lt_platform = os.getenv('LT_PLATFORM', 'Windows 10')

        options = ChromeOptions()
        # you may add options.add_argument('--headless=new') for headless runs if desired
        # provider-specific options under LT:Options (W3C style) — avoids legacy desired capabilities
        lt_options = {
            'username': username,
            'accessKey': access_key,
            'platformName': lt_platform,
            'browserVersion': lt_browser_version,
            'build': os.getenv('LT_BUILD', 'Selenium Assignment - LambdaTest Playground'),
            'name': request.node.name,
            'console': True,
            'network': True,
            'visual': True,
            'video': True,
            # additional flags if desired:
            # 'enableVNC': True,
            # 'w3c': True
        }

        # Set top-level browserName and attach provider options under the capability key.
        # Using options.set_capability to avoid desired_capabilities usage.
        options.set_capability("browserName", lt_browser)
        options.set_capability("LT:Options", lt_options)

        logger.info(f"Starting remote LambdaTest session: {request.node.name} [{lt_platform} / {lt_browser} {lt_browser_version}]")
        driver = webdriver.Remote(command_executor=lt_hub, options=options)
        # print session id for easy lookup in LT dashboard
        try:
            logger.info(f"[LT] session_id: {driver.session_id}")
        except Exception:
            pass

    else:
        chrome_options = ChromeOptions()
        # local dev options; remove headless for visible runs if you prefer
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        # chrome_options.add_argument('--headless=new')  # enable when CI headless needed
        chrome_options.add_argument('--disable-gpu')

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.info("Running locally with Chrome")

    try:
        driver.maximize_window()
    except Exception:
        logger.debug("Could not maximize window (headless or remote). Continuing.")

    # sensible implicit wait; prefer explicit waits in tests/pages
    driver.implicitly_wait(10)

    yield driver

    # Teardown: inspect test result and save artifacts or mark LT session
    try:
        report = getattr(request.node, "runtest_report", None)

        if use_lambdatest:
            # set LambdaTest pass/fail status via script
            try:
                status = "passed" if (report and not report.failed) else "failed"
                driver.execute_script(f"lambda-status={status}")
                logger.info(f"LambdaTest session for {request.node.name} finished. Status: {status.upper()}")
                # Save artifacts from remote run if failed
                if report and report.failed:
                    _save_artifacts_for_test(driver, request.node.name)
            except Exception as e:
                logger.exception(f"Failed to set LambdaTest status or save artifacts: {e}")
        else:
            # local run: save artifacts and logs on failure
            try:
                if report and report.failed:
                    _save_artifacts_for_test(driver, request.node.name)
                    logger.error(f"Saved artifacts for failed test: {request.node.name}")
            except Exception as e:
                logger.exception(f"Failed saving local artifacts: {e}")

            # Try to capture console logs (may not be supported on all drivers)
            try:
                logs = driver.get_log('browser')
                for log_entry in logs[-20:]:
                    logger.info(f"Console Log: {log_entry}")
            except Exception:
                logger.debug("Browser console logs not available.")

    except Exception as e:
        logger.error(f"Error during teardown for {request.node.name}: {e}")
        # best-effort: attempt to mark LT session failed
        try:
            if use_lambdatest and driver:
                driver.execute_script('lambda-status=failed')
        except Exception:
            logger.debug("Unable to set lambda-status during exception handling.")
    finally:
        try:
            driver.quit()
        except Exception:
            logger.exception("Error quitting driver in teardown.")
