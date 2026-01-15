import re
from typing import List

from semver import Version


class UpdateData:
    release_versions: List[Version]
    release_version_steps: dict
    latest_version: Version

    def __init__(self, updatescript: str):
        self.release_versions = self._get_release_versions(updatescript)
        self.latest_version = self.release_versions[-1] if self.release_versions else None
        self.release_version_steps = self._get_release_steps(updatescript)

    def _get_release_versions(self, updatescript: str) -> List[Version]:
        match = re.search(r"releases\{([^}]*)}", updatescript, re.DOTALL)
        if not match:
            return []

        block_content = match.group(1)

        versions = []
        for line in block_content.splitlines():
            if line.strip():
                try:
                    version = Version.parse(line.strip())
                except:
                    continue

                versions.append(version)

        versions.sort()
        return versions

    def _get_release_steps(self, updatescript: str) -> dict:
        release_steps = {}

        matches = re.findall(r"release:(.*?)\{([^}]*)}", updatescript)
        if not matches:
            return {}

        for match in matches:
            version_nr = match[0]
            block_content = match[1]

            step = {
                'files_to_download': self._get_filenames_to_download(block_content)
            }

            release_steps[version_nr] = step

        return release_steps

    def _get_filenames_to_download(self, step_content: str) -> List[str]:
        matches = re.findall(r"DownloadFile:(.*?)\n", step_content)
        if not matches:
            return []

        filenames = []
        for match in matches:
            filenames.append(match)

        return filenames
