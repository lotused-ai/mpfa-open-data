# Data layout

The updater creates this structure:

```text
data/
  current/
    <dataset-slug>/
      en/
        *.csv
        *.xlsx
      tc/
        *.csv
        *.xlsx
      sc/
        *.csv
        *.xlsx
  dictionaries/
    *.pdf
  manifest.json
```

Files are downloaded from the URLs published in `config/datasets.json`. Historical versions are not copied into the repository; the DATA.GOV.HK pages expose historical archive downloads separately.

