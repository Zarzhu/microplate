from dataclasses import dataclass, field
import pandas as pd
import numpy as np
from typing import Optional, Union, Dict

@dataclass
class Microplate:
    rows: int = 8  # Standard 96-well plate has 8 rows (A-H)
    cols: int = 12 # Standard 96-well plate has 12 columns (1-12)
    plate_name: Optional[str] = None
    plate_id: Optional[str] = None
    sample_ids: Optional[Union[Dict[str, str], pd.DataFrame]] = None
    df: pd.DataFrame = field(init=False)

    def __post_init__(self):
        # Generate well indices (A1, A2, etc)
        well_indices = []
        rows = []
        cols = []
        for col in range(1, self.cols + 1):
            for row in range(self.rows):
                row_letter = chr(65 + row)  # 65 is ASCII for 'A'
                well_indices.append(f"{row_letter}{col}")
                rows.append(row_letter)
                cols.append(col)

        # Create base dataframe
        self.df = pd.DataFrame({
            'plate_name': [self.plate_name] * (self.rows * self.cols),
            'plate_id': [self.plate_id] * (self.rows * self.cols),
            'well_index': well_indices,
            'row': rows,
            'column': cols
        })

        # Handle different sample_ids input types
        if isinstance(self.sample_ids, dict):
            # If sample_ids is a dictionary, map well indices to sample IDs
            self.df['sample_id'] = self.df['well_index'].map(self.sample_ids)
        elif isinstance(self.sample_ids, pd.DataFrame):
            # If sample_ids is a DataFrame, merge on well_index
            self.df = self.df.merge(
                self.sample_ids[['well_index', 'sample_id']], 
                on='well_index', 
                how='left'
            )
        elif self.sample_ids is None:
            self.df['sample_id'] = None
        else:
            raise ValueError("sample_ids must be a dictionary, DataFrame, or None")

        # Validate plate name and ID consistency
        if len(self.df['plate_name'].unique()) > 1:
            raise ValueError("Plate name must be consistent across all wells")
        if len(self.df['plate_id'].unique()) > 1:
            raise ValueError("Plate ID must be consistent across all wells")

    def print_matrix(self):
        # Reshape the sample IDs into a matrix
        matrix = self.df['sample_id'].values.reshape(self.rows, self.cols)
        
        # Print plate information
        print(f"Plate Name: {self.plate_name}")
        print(f"Plate ID: {self.plate_id}")
        
        # Print column headers
        print("   " + " ".join(f"{i:^10}" for i in range(1, self.cols + 1)))
        
        # Print each row with row labels
        for i, row in enumerate(matrix):
            row_letter = chr(65 + i)
            print(f"{row_letter}  " + " ".join(f"{str(x):^10}" if x is not None else "    -     " for x in row))

# plate = Microplate(rows=8, cols=12, plate_name='test_plate')
# plate.print_matrix()
