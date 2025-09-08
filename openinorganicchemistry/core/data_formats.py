from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import csv
import sqlite3

logger = logging.getLogger(__name__)


class DataExporter:
    """Unified data export utility for multiple formats."""
    
    @staticmethod
    def to_json(
        data: Any, 
        output_path: Union[str, Path],
        indent: int = 2,
        ensure_serializable: bool = True
    ) -> None:
        """Export data to JSON format."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if ensure_serializable:
            data = DataExporter._make_serializable(data)
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=indent, default=str)
        
        logger.info(f"Data exported to JSON: {output_path}")
    
    @staticmethod
    def to_csv(
        data: List[Dict[str, Any]], 
        output_path: Union[str, Path],
        fieldnames: Optional[List[str]] = None
    ) -> None:
        """Export list of dictionaries to CSV format."""
        if not data:
            logger.warning("No data to export to CSV")
            return
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if fieldnames is None:
            fieldnames = list(data[0].keys())
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        logger.info(f"Data exported to CSV: {output_path} ({len(data)} rows)")
    
    @staticmethod
    def to_sqlite(
        data: Dict[str, List[Dict[str, Any]]], 
        output_path: Union[str, Path]
    ) -> None:
        """Export data to SQLite database."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(output_path)
        
        try:
            for table_name, rows in data.items():
                if not rows:
                    continue
                
                # Create table based on first row structure
                columns = list(rows[0].keys())
                column_defs = [f"{col} TEXT" for col in columns]
                create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_defs)})"
                conn.execute(create_sql)
                
                # Insert data
                placeholders = ', '.join(['?' for _ in columns])
                insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                
                for row in rows:
                    values = [str(row.get(col, '')) for col in columns]
                    conn.execute(insert_sql, values)
            
            conn.commit()
            logger.info(f"Data exported to SQLite: {output_path}")
        
        finally:
            conn.close()
    
    @staticmethod
    def _make_serializable(obj: Any) -> Any:
        """Convert object to JSON-serializable format."""
        if isinstance(obj, (str, int, float, bool)) or obj is None:
            return obj
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: DataExporter._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [DataExporter._make_serializable(item) for item in obj]
        else:
            return str(obj)


class DataImporter:
    """Unified data import utility for multiple formats."""
    
    @staticmethod
    def from_json(input_path: Union[str, Path]) -> Any:
        """Import data from JSON format."""
        input_path = Path(input_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        with open(input_path, 'r') as f:
            data = json.load(f)
        
        logger.info(f"Data imported from JSON: {input_path}")
        return data
    
    @staticmethod
    def from_csv(input_path: Union[str, Path]) -> List[Dict[str, str]]:
        """Import data from CSV format."""
        input_path = Path(input_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        data = []
        with open(input_path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        
        logger.info(f"Data imported from CSV: {input_path} ({len(data)} rows)")
        return data
    
    @staticmethod
    def from_sqlite(
        input_path: Union[str, Path], 
        query: str = "SELECT name FROM sqlite_master WHERE type='table';"
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Import data from SQLite database."""
        input_path = Path(input_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        conn = sqlite3.connect(input_path)
        
        try:
            # Get table names
            cursor = conn.execute(query)
            if "SELECT name FROM sqlite_master" in query:
                tables = [row[0] for row in cursor.fetchall()]
                
                # Import all tables
                data = {}
                for table in tables:
                    cursor = conn.execute(f"SELECT * FROM {table}")
                    columns = [description[0] for description in cursor.description]
                    rows = cursor.fetchall()
                    data[table] = [dict(zip(columns, row)) for row in rows]
                
                logger.info(f"Data imported from SQLite: {input_path} ({len(tables)} tables)")
                return data
            else:
                # Execute custom query
                cursor = conn.execute(query)
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                data = [dict(zip(columns, row)) for row in rows]
                
                logger.info(f"Query result from SQLite: {input_path} ({len(data)} rows)")
                return {"query_result": data}
        
        finally:
            conn.close()


class ExperimentArchiver:
    """Archive and restore complete experiment data."""
    
    def __init__(self, base_dir: Union[str, Path] = "experiments"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def archive_experiment(
        self,
        experiment_name: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        """Archive a complete experiment."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        experiment_dir = self.base_dir / f"{experiment_name}_{timestamp}"
        experiment_dir.mkdir(parents=True, exist_ok=True)
        
        # Save metadata
        if metadata is None:
            metadata = {}
        
        metadata.update({
            "experiment_name": experiment_name,
            "timestamp": timestamp,
            "archived_at": datetime.now().isoformat()
        })
        
        DataExporter.to_json(metadata, experiment_dir / "metadata.json")
        
        # Save main data
        DataExporter.to_json(data, experiment_dir / "data.json")
        
        # If data contains tables, also save to SQLite
        if any(isinstance(v, list) and v and isinstance(v[0], dict) for v in data.values()):
            table_data = {k: v for k, v in data.items() 
                         if isinstance(v, list) and v and isinstance(v[0], dict)}
            if table_data:
                DataExporter.to_sqlite(table_data, experiment_dir / "data.db")
        
        logger.info(f"Experiment archived: {experiment_dir}")
        return experiment_dir
    
    def list_experiments(self) -> List[Dict[str, str]]:
        """List all archived experiments."""
        experiments = []
        
        for exp_dir in self.base_dir.iterdir():
            if exp_dir.is_dir():
                metadata_file = exp_dir / "metadata.json"
                if metadata_file.exists():
                    try:
                        metadata = DataImporter.from_json(metadata_file)
                        experiments.append({
                            "name": metadata.get("experiment_name", exp_dir.name),
                            "timestamp": metadata.get("timestamp", "unknown"),
                            "path": str(exp_dir)
                        })
                    except Exception as e:
                        logger.warning(f"Could not read metadata for {exp_dir}: {e}")
        
        return sorted(experiments, key=lambda x: x["timestamp"], reverse=True)
    
    def restore_experiment(self, experiment_path: Union[str, Path]) -> Dict[str, Any]:
        """Restore an archived experiment."""
        experiment_path = Path(experiment_path)
        
        if not experiment_path.exists():
            raise FileNotFoundError(f"Experiment directory not found: {experiment_path}")
        
        # Load metadata
        metadata_file = experiment_path / "metadata.json"
        metadata = DataImporter.from_json(metadata_file) if metadata_file.exists() else {}
        
        # Load main data
        data_file = experiment_path / "data.json"
        data = DataImporter.from_json(data_file) if data_file.exists() else {}
        
        logger.info(f"Experiment restored: {experiment_path}")
        return {"metadata": metadata, "data": data}