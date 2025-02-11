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

    # Initialize the dataframe with well indexes, rows, columns, and sample IDs
    def __post_init__(self):
        # Generate well indices (A1, A2, etc)
        well_indexes = []
        rows = []
        cols = []
        for col in range(1, self.cols + 1):
            for row in range(self.rows):
                row_letter = chr(65 + row)  # 65 is ASCII for 'A'
                well_indexes.append(f"{row_letter}{col}")
                rows.append(row_letter)
                cols.append(col)

        # Create base dataframe
        self.df = pd.DataFrame({
            'plate_name': [self.plate_name] * (self.rows * self.cols),
            'plate_id': [self.plate_id] * (self.rows * self.cols),
            'well_index': well_indexes,
            'row': rows,
            'column': cols,
            'sample_id': None
        })

        # # Handle different sample_ids input types
        # if isinstance(self.sample_ids, dict):
            # # If sample_ids is a dictionary, map well indices to sample IDs
            # self.df['sample_id'] = self.df['well_index'].map(self.sample_ids)
        # elif isinstance(self.sample_ids, pd.DataFrame):
        #     # If sample_ids is a DataFrame, merge on well_index
        #     self.df = self.df.merge(
        #         self.sample_ids[['well_index', 'sample_id']], 
        #         on='well_index', 
        #         how='left'
        #     )
        # elif self.sample_ids is None:
        #     self.df['sample_id'] = None
        # else:
        #     raise ValueError("sample_ids must be a dictionary, DataFrame, or None")

        # Add samples to the dataframe
        self.add_samples(self.sample_ids)

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

    def add_samples(self, sample_ids: Optional[Union[Dict[str, str], pd.DataFrame]]):
        """
        Adds sample IDs to the microplate based on the well index. Accepts a dictionary or Dataframe. 

        Parameters
        ----------
        sample_ids: dict or pd.DataFrame
            If a dictionary, the keys are the well indices and the values are the sample IDs.
            If a DataFrame, the DataFrame must have a 'well_index' column and a 'sample_id' column.

        """

        if sample_ids is None:
            print("No samples provided.")
            return

        elif isinstance(sample_ids, dict):
            # Update only the wells that are in the dictionary
            self.df.loc[self.df['well_index'].isin(sample_ids.keys()), 'sample_id'] = \
                self.df.loc[self.df['well_index'].isin(sample_ids.keys()), 'well_index'].map(sample_ids)
        
        elif isinstance(sample_ids, pd.DataFrame):
            if 'well_index' not in sample_ids.columns or 'sample_id' not in sample_ids.columns:
                raise ValueError("DataFrame must have 'well_index' and 'sample_id' columns.")
            
            self.df = pd.merge(
                self.df,
                sample_ids[['well_index', 'sample_id']],
                on='well_index',
                how='left',
                suffixes=('', '_new')
            )
            # Update sample_id with new values where available
            self.df['sample_id'] = self.df['sample_id_new'].fillna(self.df['sample_id'])
            self.df = self.df.drop('sample_id_new', axis=1)
        
        else:
            print("Invalid input type. Expected a dictionary or DataFrame.")

# plate = Microplate(rows=8, cols=12, plate_name='test_plate')
# plate.print_matrix()