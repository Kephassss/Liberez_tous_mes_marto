from abc import ABC, abstractmethod
import os

class BaseDownloader(ABC):
    """Abstract base class for all music downloaders."""

    @abstractmethod
    def accept(self, query: str) -> bool:
        """
        Determines if this downloader can handle the given query or URL.
        """
        pass

    @abstractmethod
    def download(self, query: str, output_path: str = ".", no_cover: bool = False) -> dict:
        """
        Downloads the track(s) from the query to the output_path.
        Returns a dict with result info (status, files, etc.).
        """
        pass
