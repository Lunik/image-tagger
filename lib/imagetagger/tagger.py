"""
Root module for ImageTagger.
"""

import sys
import os
import argparse
import json
import io

from PIL import Image as PILImage
from exif import Image as ExifImage
from ollama import generate

from .log import console, error_console
from .exiftool import ExifTool


class ImageTaggerParser(argparse.ArgumentParser):
    """
    Custom python parser for image-tagger.
    """

    def error(self, message):
        """
        Print an error message and exit.
        """
        error_console.print(f"error: {message}\n", style="bold red")
        self.print_help()
        sys.exit(2)


class ImageTagger:
    """
    Root class for image-tagger.
    """

    def __init__(self, version):
        self.version = version
        self.exiftool = ExifTool()

    @property
    def parser(self):
        """
        Construct the parser for image-tagger.
        Returns an instance of ImageTaggerParser.
        """
        parser = ImageTaggerParser(
            description="Tool for tagging images.",
            epilog=f"version : {sys.argv[0]}@{self.version}",
        )

        parser.add_argument(
            "directory",
            type=str,
            help="Directory containing images to tag.",
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Perform a dry run without modifying any files.",
        )

        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Confirm each tag before applying it.",
        )

        parser.add_argument(
            "--vision-model",
            type=str,
            default="llava",
            help="Vision model to use for describing images.",
        )

        parser.add_argument(
            "--tagger-model",
            type=str,
            default="phi3",
            help="LLM model to use for generating tags from descriptions.",
        )

        parser.add_argument(
            "--lang",
            type=str,
            default="french",
            help="Language to translate the tags to.",
        )

        return parser

    def _optimize_image(self, path, resolution=None):
        """
        Optimize the given image before processing it.
        """
        if not resolution:
            resolution = (256, 256)

        try:
            image = PILImage.open(path)
            image.thumbnail(resolution)

            bytes_io = io.BytesIO()
            image.save(bytes_io, format="JPEG")
            bytes_io.seek(0)
        except Exception as e:
            error_console.print(f"Error optimizing an image: {e}", style="bold red")
            return None

        return bytes_io

    def _make_ai_request(self, *args, **kwargs):
        """
        Make an AI request using the given arguments.
        """
        try:
            response = generate(*args, **kwargs)
        except Exception as e:
            error_console.print(f"Error making AI request: {e}", style="bold red")
            return None

        return response

    def _describe_image(self, image, vision_model):
        """
        Describe the given image.
        """

        response = self._make_ai_request(
            vision_model,
            "quickly in describe notable object in the following picture:",
            images=[image],
            stream=False,
            keep_alive=300,
        )

        if not response:
            return None

        description = response["response"].strip()

        return description

    def _generate_tags(self, description, tagger_model):
        """
        Generate tags for the given description.
        """
        response = self._make_ai_request(
            tagger_model,
            f'You are an image tagger expert. You will be given the description of an image in natural language and your task is to return a list of short keyword that best describe the image. A keyword is composed of a single word, this is mandatory.\nReturn the keywords in a JSON parsable list of strings : ["tag1", "tag2", "tag3"]\nIf the description doesn\'t or fail to describe the image, just return an empty list. Be concise. \n\nFor example :\nDescription: A person in front of a beautiful lake with tree around, frogs in the front and water lily on the watter surface.\n{{"tags": ["person", "lake", "frog", "tree", "water lily"]}}\n\n==========\n\nDescription: {description}',
            stream=False,
            keep_alive=300,
        )

        if not response:
            return None

        raw_tags = response["response"].strip()
        try:
            data = json.loads(raw_tags)
            if isinstance(data, dict):
                tags = data.get("tags", [])
            elif isinstance(data, list):
                tags = data
            else:
                tags = []
        except json.JSONDecodeError as e:
            error_console.print(f"Error decoding tags: {raw_tags}", style="bold red")
            error_console.print(f"Error: {e}", style="bold red")
            return None

        return tags

    def _translate_tags(self, tags, lang, tagger_model):
        """
        Translate the given tags to the given language.
        """
        response = self._make_ai_request(
            tagger_model,
            f'Translate the following content in "{lang.upper()}". DO NOT alter the content, just translate it. DO NOT change the JSON format of the list.\n\nFor example :\nTags: ["person", "lake", "frog", "tree", "water lily"]\n{{"tags": ["personne", "lac", "grenouille", "arbre", "nénuphar"]}}\n\n==========\n\nTags: {tags}',
            stream=False,
            keep_alive=300,
            format="json",
        )

        if not response:
            return None

        raw_translated_tags = response["response"].strip()
        print("====================================")
        print(raw_translated_tags)
        print("====================================")
        try:
            data = json.loads(raw_translated_tags)
            if isinstance(data, dict):
                translated_tags = data.get("tags", [])
            elif isinstance(data, list):
                translated_tags = data
            else:
                translated_tags = []
        except json.JSONDecodeError as e:
            error_console.print(
                f"Error decoding translated tags: {raw_translated_tags}",
                style="bold red",
            )
            error_console.print(f"Error: {e}", style="bold red")
            return None

        return translated_tags

    def _construct_categories_tags(self, tags):
        result = "<Categories>"

        for index, tag in enumerate(tags):
            result += f'<Category Assigned="{index + 1}">{tag}</Category>'

        result += "</Categories>"

        return result

    def _prepare_tags(self, tags):
        ordered_tags = []

        # We add the People tags first
        for tag in tags:
            if tag.startswith("People"):
                ordered_tags.append(tag)

        # We add the rest of the tags
        for tag in tags:
            if tag not in ordered_tags:
                ordered_tags.append(tag.lower())

        return ordered_tags

    def _apply_tags(self, path, tags):
        """
        Apply the given tags to the given image.
        """
        for attribute in [
            "Keywords",
            "Subject",
            "TagsList",
            "CatalogSets",
            "LastKeywordXMP",
            "HierarchicalSubject",
            "Categories",
        ]:
            if attribute == "Categories":
                current_values = set(self.exiftool.get_attribute(path, attribute))
                new_values = [
                    self._construct_categories_tags(current_values.union(tags))
                ]
            else:
                current_values = set(self.exiftool.get_attribute(path, attribute))
                new_values = current_values.union(tags)

            sorted_new_values = self._prepare_tags(list(new_values))

            result = self.exiftool.replace_attribute(path, attribute, sorted_new_values)
            if not result:
                error_console.print(
                    f"Error applying tags({attribute}) to the image: {path}",
                    style="bold red",
                )
                return None

        return True

    def _process_image(self, path, vision_model, tagger_model, lang):
        """
        Process the given image.
        """
        with console.status(
            f"[bold green]Processing image[/bold green]: {path}"
        ) as status:
            ######################
            # Optimize the image #
            ######################
            console.print(f"> [bold blue]Optimizing image[/bold blue]: {path}")
            image = self._optimize_image(path)
            if not image:
                error_console.print(
                    f"Error optimizing the image: {path}", style="bold red"
                )
                status.stop()
                return

            ######################
            # Describe the image #
            ######################
            console.print(f"> [bold blue]Describing image[/bold blue]: {path}")
            description = self._describe_image(path, vision_model)
            if not description:
                error_console.print(
                    f"Error describing the image: {path}", style="bold red"
                )
                status.stop()
                return
            console.print(f"> [bold green]Description[/bold green]: {description}")

            #################
            # Generate tags #
            #################
            console.print(f"> [bold blue]Generating tags for image[/bold blue]: {path}")
            tags = self._generate_tags(description, tagger_model)
            if not tags:
                error_console.print(
                    f"Error generating tags for the image: {path}", style="bold red"
                )
                status.stop()
                return
            console.print(f"> [bold green]Tags[/bold green]: {tags}")

            ######################
            # Translate the tags #
            ######################
            console.print(
                f"> [bold blue]Translating tags to user language[/bold blue]: {path}"
            )
            translated_tags = self._translate_tags(tags, lang, tagger_model)
            if not translated_tags:
                error_console.print(
                    f"Error translating tags for the image: {path}", style="bold red"
                )
                status.stop()
                return
            console.print(
                f"> [bold green]Translated tags[/bold green]: {translated_tags}"
            )

            ##################
            # Apply the tags #
            ##################
            console.print(f"> [bold blue]Applying tags to image[/bold blue]: {path}")
            result = self._apply_tags(path, translated_tags)
            if not result:
                error_console.print(
                    f"Error applying tags to the image: {path}", style="bold red"
                )
                status.stop()
                return
            console.print(f"> [bold green]Tags applied successfully[/bold green]")

    def run(self, args):
        """
        Run image-tagger with the given arguments.
        """
        for root, _, files in os.walk(args.directory):
            for file in files:
                if file.endswith((".jpg", ".jpeg", ".png")):
                    path = os.path.join(root, file)
                    self._process_image(
                        path, args.vision_model, args.tagger_model, args.lang
                    )
