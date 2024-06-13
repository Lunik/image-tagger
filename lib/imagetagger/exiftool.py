import json
import subprocess


class ExifTool:
    def __init__(self, executable="exiftool"):
        self.executable = executable

    def _execute(self, command):
        """
        Execute a command.
        """
        result = subprocess.run(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        if result.returncode != 0:
            print(f"Error executing command: {command}")
            print(result.stderr.decode("utf-8"))
            return None

        return result.stdout.decode("utf-8")

    def _cleanup_value(self, value):
        """
        Cleanup a value.
        """
        return value.strip().replace("'", "'\\''")

    def list_all(self, path):
        """
        List all metadata of the given image.
        """
        command = f"{self.executable} -json '{path}'"
        result = self._execute(command)
        if result is None:
            return None

        return json.loads(result)[0].keys()

    def get_attribute(self, path, attribute):
        """
        Get the given attribute of the given image.
        """
        command = f"{self.executable} -{attribute} -json '{path}'"
        result = self._execute(command)
        if result is None:
            return None

        if attribute not in json.loads(result)[0]:
            return []

        values = json.loads(result)[0][attribute]
        if isinstance(values, str):
            values = [values]

        return values

    def set_attribute(self, path, attribute, value):
        """
        Set the given attribute of the given image.
        """
        value = self._cleanup_value(value)

        command = f"{self.executable} -{attribute}+='{value}' '{path}'"
        result = self._execute(command)
        if result is None:
            return False

        return True

    def remove_attribute(self, path, attribute, value):
        """
        Remove the given attribute of the given image.
        """
        value = self._cleanup_value(value)

        command = f"{self.executable} -{attribute}-='{value}' '{path}'"
        result = self._execute(command)
        if result is None:
            return False

        return True

    def replace_attribute(self, path, attribute, values):
        """
        Replace the given attribute of the given image.
        """
        options = ""
        for value in values:
            value = self._cleanup_value(value)

            options += f" -{attribute}='{value}'"

        command = f"{self.executable} {options} '{path}'"
        result = self._execute(command)
        if result is None:
            return False

        return True
