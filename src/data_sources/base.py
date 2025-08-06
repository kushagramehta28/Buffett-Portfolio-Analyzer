from abc import ABC, abstractmethod
from typing import Dict, List, Any
from datetime import datetime

class DataSourceInterface(ABC):
    """Abstract base class for all data sources"""
    
    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the data source"""
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """Close connection to the data source"""
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, List[str]]:
        """Return the schema of the data source"""
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """Check if the data source is available and responding"""
        pass
    
    @abstractmethod
    def execute_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a query on the data source"""
        pass

class DataSourceMetadata:
    """Metadata for data sources"""
    def __init__(self, name: str, type: str, description: str):
        self.name = name
        self.type = type
        self.description = description
        self.last_updated = datetime.now()
        self.is_active = True
        self.error_count = 0
        
    def update_status(self, is_active: bool, error_message: str = None):
        self.is_active = is_active
        if not is_active and error_message:
            self.error_count += 1 