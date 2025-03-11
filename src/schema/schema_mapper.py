from typing import Dict, List, Any, Optional
from difflib import SequenceMatcher
import json
import os
from datetime import datetime
import logging
from abc import ABC, abstractmethod

class SchemaField:
    def __init__(self, name: str, data_type: str, source: str, description: str = None):
        self.name = name
        self.data_type = data_type
        self.source = source
        self.description = description
        self.aliases = self._generate_aliases()
        
    def _generate_aliases(self) -> List[str]:
        """Generate possible aliases for the field name"""
        name_parts = self.name.lower().replace('_', ' ').split()
        aliases = [self.name.lower()]
        
        # Add common variations
        if 'ratio' in name_parts:
            aliases.append(self.name.lower().replace('ratio', 'r'))
        if 'price' in name_parts:
            aliases.append(self.name.lower().replace('price', 'p'))
        if 'earnings' in name_parts:
            aliases.append(self.name.lower().replace('earnings', 'e'))
            
        return aliases

class SchemaMapper:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.source_schemas = {}
        self.field_mappings = {}
        self.mapping_history = []
        self.mapping_file = 'schema_mappings.json'
        self.load_mappings()

    def load_mappings(self):
        """Load existing mappings from file"""
        try:
            if os.path.exists(self.mapping_file):
                with open(self.mapping_file, 'r') as f:
                    saved_mappings = json.load(f)
                    self.field_mappings = saved_mappings.get('mappings', {})
                    self.mapping_history = saved_mappings.get('history', [])
        except Exception as e:
            self.logger.error(f"Error loading mappings: {e}")

    def save_mappings(self):
        """Save current mappings to file"""
        try:
            with open(self.mapping_file, 'w') as f:
                json.dump({
                    'mappings': self.field_mappings,
                    'history': self.mapping_history,
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving mappings: {e}")

    def register_source_schema(self, source_name: str, schema: Dict[str, Any]):
        """Register a new data source schema"""
        self.source_schemas[source_name] = schema
        self._update_mappings(source_name)
        
    def remove_source_schema(self, source_name: str):
        """Remove a data source schema and update mappings"""
        if source_name in self.source_schemas:
            del self.source_schemas[source_name]
            self._cleanup_mappings(source_name)

    def _update_mappings(self, source_name: str):
        """Update mappings when a new source is added"""
        new_schema = self.source_schemas[source_name]
        
        # Track schema change
        self.mapping_history.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'source_added',
            'source': source_name,
            'schema': new_schema
        })
        
        # Generate new mappings
        for field_name, field_info in new_schema.items():
            self._map_field(source_name, field_name, field_info)

    def _map_field(self, source_name: str, field_name: str, field_info: Dict):
        """Map a field to existing fields or create new mapping"""
        if field_name not in self.field_mappings:
            # Check for similar existing fields
            similar_field = self._find_similar_field(field_name)
            
            if similar_field:
                # Add to existing mapping
                self.field_mappings[similar_field]['sources'][source_name] = {
                    'field_name': field_name,
                    'info': field_info
                }
            else:
                # Create new mapping
                self.field_mappings[field_name] = {
                    'sources': {
                        source_name: {
                            'field_name': field_name,
                            'info': field_info
                        }
                    },
                    'type': field_info.get('type', 'string'),
                    'created_at': datetime.now().isoformat()
                }

    def _find_similar_field(self, field_name: str, threshold: float = 0.8) -> Optional[str]:
        """Find similar existing field names"""
        for existing_field in self.field_mappings.keys():
            similarity = SequenceMatcher(None, field_name.lower(), existing_field.lower()).ratio()
            if similarity >= threshold:
                return existing_field
        return None

    def _cleanup_mappings(self, source_name: str):
        """Clean up mappings when a source is removed"""
        # Track schema change
        self.mapping_history.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'source_removed',
            'source': source_name
        })
        
        # Remove source from mappings
        for field_name in list(self.field_mappings.keys()):
            sources = self.field_mappings[field_name]['sources']
            if source_name in sources:
                del sources[source_name]
                if not sources:  # If no sources left, remove the field
                    del self.field_mappings[field_name]

    def get_field_mapping(self, source_name: str, field_name: str) -> Dict[str, Any]:
        """Get mapping for a specific field"""
        for unified_name, mapping in self.field_mappings.items():
            if source_name in mapping['sources'] and mapping['sources'][source_name]['field_name'] == field_name:
                return {
                    'unified_name': unified_name,
                    'mapping': mapping
                }
        return None

    def handle_schema_change(self, source_name: str, new_schema: Dict[str, Any]):
        """Handle changes in source schema"""
        old_schema = self.source_schemas.get(source_name, {})
        
        # Track schema change
        self.mapping_history.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'schema_changed',
            'source': source_name,
            'old_schema': old_schema,
            'new_schema': new_schema
        })
        
        # Update schema
        self.source_schemas[source_name] = new_schema
        
        # Find removed fields
        removed_fields = set(old_schema.keys()) - set(new_schema.keys())
        for field in removed_fields:
            self._handle_removed_field(source_name, field)
        
        # Find new fields
        new_fields = set(new_schema.keys()) - set(old_schema.keys())
        for field in new_fields:
            self._map_field(source_name, field, new_schema[field])
            
        self.save_mappings()

    def _handle_removed_field(self, source_name: str, field_name: str):
        """Handle removal of a field from source"""
        for mapping in self.field_mappings.values():
            if source_name in mapping['sources'] and mapping['sources'][source_name]['field_name'] == field_name:
                del mapping['sources'][source_name]

class FieldTransformer(ABC):
    @abstractmethod
    def transform(self, value: Any) -> Any:
        pass

class NumericTransformer(FieldTransformer):
    def transform(self, value: Any) -> float:
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0

class DateTransformer(FieldTransformer):
    def transform(self, value: Any) -> str:
        try:
            return datetime.strptime(value, '%Y-%m-%d').isoformat()
        except (ValueError, TypeError):
            return None

class SchemaTransformer:
    def __init__(self, schema_mapper: SchemaMapper):
        self.schema_mapper = schema_mapper
        self.transformers = {
            'numeric': NumericTransformer(),
            'date': DateTransformer()
        }

    def transform_data(self, source_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data according to schema mappings"""
        transformed = {}
        
        for field_name, value in data.items():
            mapping = self.schema_mapper.get_field_mapping(source_name, field_name)
            if mapping:
                unified_name = mapping['unified_name']
                field_type = mapping['mapping']['type']
                
                if field_type in self.transformers:
                    transformed[unified_name] = self.transformers[field_type].transform(value)
                else:
                    transformed[unified_name] = value
                    
        return transformed 