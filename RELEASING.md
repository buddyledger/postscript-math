## Releasing to CTAN

The [CTAN upload](https://github.com/buddyledger/pst-numeric/actions/workflows/ctan-upload.yml) workflow sends the package to CTAN on demand.
It never runs on its own; someone has to start it.

### Before a release

1. Bump `\fileversion` and `\filedate` in `tex/pst-numeric.tex`. CTAN requires an update to have a different version from the one it already holds.
2. Put the same date and version in `\ProvidesPackage` in `latex/pst-numeric.sty`, and at the top of `README`.
3. Add an entry to `Changes`.
4. Rebuild `doc/pst-numeric-doc.pdf` with `tools/make-doc.sh`. CTAN rejects an archive without PDF documentation.
5. Run `python tools/make-ctan.py`. It builds the archive, and fails if a file is missing or if the versions in `tex/`, `latex/` and `Changes` disagree.
6. Commit and push to `main`, and check that the test workflow passes.

### Running the workflow

From the GitHub website: open the **Actions** tab, choose **CTAN upload**, click **Run workflow**, pick a mode and fill in the optional fields.

From a terminal with the GitHub CLI:

```bash
gh workflow run ctan-upload.yml -f mode=validate
```

```bash
gh workflow run ctan-upload.yml -f mode=upload -f update=false -f announcement="What changed in this release"
```

| Input | Meaning |
|---|---|
| `mode` | `validate` is a dry run: CTAN checks the archive and the fields, and stores nothing. `upload` validates first and submits only if validation is clean. |
| `update` | `false` for the first upload of pst-numeric, which creates a new package on CTAN; `true` for every later version. |
| `announcement` | Optional text for the CTAN announcement mailing list. Leave empty for no announcement. |
| `note` | Optional private note to the CTAN upload managers. |

Run `validate` first, read the log, then run `upload`.

### What the workflow does

1. Builds and checks `pst-numeric.zip` with `tools/make-ctan.py`: `README`, `Changes`, `doc/`, `dvips/`, `latex/`, `tex/` and `source/` (without `gs.bat`) under a top-level `pst-numeric/` folder. It reads the version from `\fileversion` in `tex/pst-numeric.tex`.
2. Saves the zip as a downloadable artifact on the workflow run.
3. Posts the zip and the package fields to CTAN's submit API, and prints CTAN's messages in the log.

The run fails if CTAN reports any error, or if an upload is not confirmed with "Upload succeeded".

### After an upload

An upload is not published immediately. The CTAN upload managers review it by hand, and they reply to the uploader's email address. The new version appears on CTAN once they have installed it. After the first upload, use `update=true`.

### Setup

The workflow needs two repository secrets (**Settings → Secrets and variables → Actions**):

| Secret | Value |
|---|---|
| `CTAN_UPLOADER` | Name of the person uploading |
| `CTAN_EMAIL` | Their email address |

To set or change them from a terminal (each command prompts for the value):

```bash
gh secret set CTAN_UPLOADER
```

```bash
gh secret set CTAN_EMAIL
```

The fixed package fields (author, licence, summary, description, CTAN path, home page and bug tracker) are set in
[.github/workflows/ctan-upload.yml](.github/workflows/ctan-upload.yml).
