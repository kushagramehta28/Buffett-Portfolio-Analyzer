import pandas as pd
from typing import Dict, List, Any
from .base import DataSourceInterface, DataSourceMetadata

class AnalystDataSource(DataSourceInterface):
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.metadata = DataSourceMetadata(
            name="analyst_data",
            type="csv",
            description="Analyst ratings and technical indicators from CSV"
        )
        self.df = None

    def connect(self) -> bool:
        """Load CSV data into DataFrame"""
        try:
            self.df = pd.read_csv(self.csv_path)
            return True
        except Exception as e:
            self.metadata.update_status(False, str(e))
            return False

    def disconnect(self) -> bool:
        """Clear DataFrame"""
        self.df = None
        return True

    def get_schema(self) -> Dict[str, List[str]]:
        """Return the schema of the CSV data"""
        if self.df is not None:
            return {
                'analyst_ratings': self.df.columns.tolist()
            }
        return {}

    def health_check(self) -> bool:
        """Verify data is loaded and accessible"""
        return self.df is not None and not self.df.empty

    def execute_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Execute query on the DataFrame"""
        try:
            if 'symbol' in query:
                result = self.df[self.df['symbol'] == query['symbol']]
                if not result.empty:
                    return result.iloc[0].to_dict()
                return {'error': f"No data found for symbol {query['symbol']}"}
            else:
                return {'error': "Query must include symbol"}
        except Exception as e:
            self.metadata.update_status(False, str(e))
            return {'error': str(e)} 