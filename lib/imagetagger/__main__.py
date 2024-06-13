"""
Main function for image-tagger.
"""

import sys

from .tagger import ImageTagger
from .exception import TaggerException
from .log import error_console
from . import __version__

image_tagger = ImageTagger(version=__version__)
args = image_tagger.parser.parse_args()

try:
    image_tagger.run(args)
    sys.exit(0)

except Exception as error:  # pylint: disable=broad-except
    if isinstance(error, TaggerException):
        error_console.print(error, style="bold red")
    else:
        error_console.print_exception()

    sys.exit(1)
