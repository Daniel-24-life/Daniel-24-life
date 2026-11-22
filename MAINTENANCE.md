# Profile maintenance

The gallery is curated in [README.md](README.md). Its six entries also appear in
[featured.json](featured.json). Store desk-sized image files under
`assets/work/`, with specific alt text and a link to the corresponding repository.
The [Chinese navigation](README.zh.md) links to the same work. The full
portfolio catalog is maintained in [AIfile](https://github.com/Daniel-24-life/AIfile).

## Verify changes

```sh
python scripts/update_metrics.py --check
```

The check validates gallery order, GitHub links, local image references and SVG syntax.
It uses the committed snapshot and runs without network access.

## Refresh the public snapshot

The [scheduled workflow](.github/workflows/update-metrics.yml) runs weekly and
supports a manual run. It reads repository metadata and language totals from the
GitHub API and writes the light and dark SVG files. It only commits changes to
those two files after validation. If fetching or rendering fails, the committed
snapshot remains available.

To refresh locally with an authenticated API environment, run
`python scripts/update_metrics.py` and review the SVG diff. The command accepts
an optional `GITHUB_TOKEN` from the environment. It requests only the public
repositories listed in `featured.json`.
