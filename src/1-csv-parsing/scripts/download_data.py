import zipfile
from pathlib import Path

import gdown


def download_csv(url: str, output_path: str | Path) -> Path:
    output_path = Path(output_path)

    # Download to a temporary file first so we can determine whether
    # the downloaded file is a ZIP or a CSV.
    temp_path = output_path.with_suffix(".download")

    try:
        downloaded_path = gdown.download(
            url=url,
            output=str(temp_path),
            quiet=False,
        )

        if downloaded_path is None:
            raise RuntimeError(f"Failed to download file from: {url}")

        # Check whether the downloaded content is a ZIP
        if zipfile.is_zipfile(temp_path):
            with zipfile.ZipFile(temp_path) as z:
                csv_files = [
                    name for name in z.namelist() if name.lower().endswith(".csv")
                ]

                if not csv_files:
                    raise ValueError("ZIP file does not contain a CSV.")

                if len(csv_files) > 1:
                    print(f"Multiple CSVs found; using: {csv_files[0]}")

                with z.open(csv_files[0]) as src:
                    output_path.write_bytes(src.read())

        else:
            # Assume it's already a CSV
            temp_path.replace(output_path)

    finally:
        # Remove temporary file if it still exists
        if temp_path.exists():
            temp_path.unlink()

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

    if output_path.exists():
        print(f"Skipping download. Data already exists {output_path}")
        return output_path

    return download_csv(url, output_path)
