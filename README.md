# Image Tagger

## Description

Image-Tagger is a simple command line tool to tag images using exiftool. It uses AI to detect the content of the image and add tags to the image metadata.

AI engine used is [Ollama](https://ollama.com) and the vision model is [LLava](https://llava-vl.github.io) and the llm model is [Phi3](https://azure.microsoft.com/en-us/products/phi-3).

## Requirements

Install [Ollama](https://ollama.com) and the required [LLava](https://ollama.com/library/llava), [Phi3](https://ollama.com/library/phi3) AI models.

```bash
ollama pull llava
ollama pull phi3
```

## Installation

To install Image-Tagger, simply run the following command:

```bash
pip install --user .
```

or with an isolated environment:

```bash
python -m venv ~/bin/image-tagger_venv
~/bin/image-tagger_venv/bin/pip install .

ln -s ~/bin/image-tagger_venv/bin/image-tagger ~/bin/image-tagger
```

## Usage

To use Image-Tagger, simply run the following command :

```bash
image-tagger --help
```

## Contributing

To contribute to Image-Tagger, simply fork the repository and create a pull request. Please make sure to include a detailed description of your changes. Here are the things I will check during the review :

- Is CHANGELOG.md have been updated (**required**)
- Is the lint score did not decrease (**required**)
- Is the test coverage did not decrease (**required**)
- Is the documentation have been updated (**if required**)
- If tests have been added (**optional**)

## Tips

### MacOS

Pour définir le nombre maximal de modèles chargés simultanément à deux, utilisez :
```bash
launchctl setenv OLLAMA_MAX_LOADED_MODELS 2
```