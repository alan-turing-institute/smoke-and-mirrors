# Smoke and Mirrors
Prototype dynamic AI emulators for OT hardware.

May 2025: [Technical Snapshot](https://airgapped.substack.com/p/update-may-2025-technical-snapshot)

## Description
 
This repository contains code samples relating to the use of LLMs for emulating devices on industrial Operational Technology (OT) networks. 
**This is the sanitised version of our full codebase. If you require access to the full version, please get in touch.**

The current prototype focuses on the [Modbus](https://en.wikipedia.org/wiki/Modbus) protocol, the *de facto* standard in industrial cyber-physical systems.


## Contents

- **LLM response generation.** A [Jupyter notebook](notebooks/llm-response-generation.ipynb) demonstrating several approaches to generating Modbus responses by direct LLM prompting with requests in the form of hexadecimal strings.

- **LLM code generation.** A [Jupyter notebook](notebooks/llm-code-generation.ipynb) containing prompts for generating a standalone Python module capable of handling requests in the Modbus protocol. An example of automatically-generated code can be found in [`modbus_handler.py`](src/llm-generated-code/modbus_handler.py).

Note: these notebooks make calls to the OpenAI API, which requires access to an [API key](https://platform.openai.com/docs/api-reference/authentication). To do this, create a file named `.env` at the root of the repository, containing the following line:
```
OPENAI_API_KEY="<INSERT YOUR KEY HERE>"
```

## Installation

To install this package with dev dependencies:
```bash
pip install -e ".[dev,modbus]"
```

Install pre-commit hooks with:
```
pre-commit install
```
