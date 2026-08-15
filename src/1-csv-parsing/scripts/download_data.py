import io
import zipfile
from pathlib import Path

import httpx


def download_csv(url: str, output_path: str | Path) -> Path:
    output_path = Path(output_path)

    with httpx.Client(follow_redirects=True, timeout=60.0) as client:
        response = client.get(url)
        response.raise_for_status()

    content = response.content

    # Check whether the downloaded content is a ZIP
    if zipfile.is_zipfile(io.BytesIO(content)):
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            csv_files = [name for name in z.namelist() if name.lower().endswith(".csv")]

            if not csv_files:
                raise ValueError("ZIP file does not contain a CSV.")

            if len(csv_files) > 1:
                print(f"Multiple CSVs found; using: {csv_files[0]}")

            with z.open(csv_files[0]) as src:
                output_path.write_bytes(src.read())

    else:
        # Assume it's already a CSV
        output_path.write_bytes(content)

    return output_path


def download_data(
    url: str,
    filename: str,
    target_path: str | Path = ".",
) -> Path:
    """Create a data folder if needed and download a CSV into it."""
    target_path = Path(target_path)

    data_folder = target_path / "data"
    data_folder.mkdir(parents=True, exist_ok=True)

    output_path = data_folder / filename

    return download_csv(url, output_path)
