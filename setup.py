from setuptools import setup, find_packages

setup(
    name="generate-prompt-ollama-plugin",
    version="1.0.0",
    description="Stable Diffusion WebUI plugin for automatic prompt enhancement via Ollama API",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
        "pydantic>=1.10.0",
        "python-dotenv>=1.0.0",
        "gradio>=3.0.0"
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)