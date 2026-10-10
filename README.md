# MPFA Open Data

Automatically mirrored open data published by the Hong Kong Mandatory Provident Fund Schemes Authority (MPFA) through [DATA.GOV.HK](https://data.gov.hk/en-datasets/provider/mpfa).

## Included data

The repository tracks seven MPFA datasets:

- Number of MPF trustees, schemes and funds
- Contributions received and benefits paid of MPF schemes
- Number of MPF accounts
- Net asset values of approved constituent funds
- MPF assets invested in Default Investment Strategy constituent funds
- Number of accounts investing in Default Investment Strategy constituent funds
- Number of MPF intermediaries

For each dataset, the updater downloads the English, Traditional Chinese and Simplified Chinese resources in CSV and XLSX format, together with the published data dictionary PDF.

The source catalogue and resource URLs are maintained in [`config/datasets.json`](config/datasets.json). Current files are stored under [`data/current`](data/current), grouped by dataset, language and format. The generated [`data/latest.json`](data/latest.json) consolidates all CSV rows into one application-friendly file while preserving separate dataset and language sections. `data/manifest.json` records the fetch time, source URL, file size and SHA-256 hash for every downloaded resource.

## Updating locally

Requires Python 3.11 or newer and uses only the Python standard library:

```powershell
python scripts/update_data.py
```

The command is idempotent: unchanged source files are not rewritten. If a source resource is temporarily unavailable, the error is recorded in `data/manifest.json` and the command fails so the scheduled workflow does not commit a partial update.

## Automated updates

The [GitHub Actions workflow](.github/workflows/update.yml) runs on the 15th of every month at 02:17 UTC and can also be started manually. When downloaded files change, it commits the updated raw data, consolidated JSON and manifest back to the default branch.

## Attribution

Source: [Mandatory Provident Fund Schemes Authority](https://www.mpfa.org.hk/en/) via [DATA.GOV.HK](https://data.gov.hk/en-datasets/provider/mpfa). Please check the source pages and data dictionaries for licensing, definitions and limitations before using the data.
