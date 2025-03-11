from typing import Dict, List
from .base import DataSourceInterface
import logging

class DataSourceManager:
    def __init__(self):
        self.sources: Dict[str, DataSourceInterface] = {}
        self.logger = logging.getLogger(__name__)

    def register_source(self, source: DataSourceInterface) -> bool:
        """Register a new data source"""
        try:
            if source.connect():
                self.sources[source.metadata.name] = source
                self.logger.info(f"Registered data source: {source.metadata.name}")
                return True
            else:
                self.logger.error(f"Failed to connect to data source: {source.metadata.name}")
                return False
        except Exception as e:
            self.logger.error(f"Error registering data source: {str(e)}")
            return False

    def remove_source(self, source_name: str) -> bool:
        """Remove a data source"""
        if source_name in self.sources:
            source = self.sources[source_name]
            source.disconnect()
            del self.sources[source_name]
            self.logger.info(f"Removed data source: {source_name}")
            return True
        return False

    def get_source(self, source_name: str) -> DataSourceInterface:
        """Get a specific data source"""
        return self.sources.get(source_name)

    def get_all_sources(self) -> List[str]:
        """Get list of all registered data sources"""
        return list(self.sources.keys())

    def get_combined_schema(self) -> Dict[str, Dict[str, List[str]]]:
        """Get combined schema from all data sources"""
        combined_schema = {}
        for name, source in self.sources.items():
            combined_schema[name] = source.get_schema()
        return combined_schema

    def health_check_all(self) -> Dict[str, bool]:
        """Check health of all data sources"""
        return {name: source.health_check() for name, source in self.sources.items()}

    def cleanup(self):
        """Cleanup all data source connections"""
        for source in self.sources.values():
            source.disconnect()
        self.sources.clear() 