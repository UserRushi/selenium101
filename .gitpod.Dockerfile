# .gitpod.Dockerfile: Base image with Python and browser tools for Selenium
FROM gitpod/workspace-full

# Install Python 3.11 (latest stable)
USER root
RUN sudo apt-get update && sudo apt-get install -y python3.11 python3.11-venv python3-pip

# Set Python 3.11 as default
RUN sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
RUN sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1
RUN python -m pip install --user --upgrade pip

# Pre-install some Python tools (Selenium will be installed via requirements.txt)
RUN python -m pip install --user pytest webdriver-manager

USER gitpod