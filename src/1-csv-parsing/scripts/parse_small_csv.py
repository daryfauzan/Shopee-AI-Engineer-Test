from pathlib import Path

import pandas as pd


def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(str(path))
    return df
