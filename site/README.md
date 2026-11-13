# Fable 5.2 showcase

This site reuses the layout and styles of the Leadde Opus 5.5 showcase. Its content comes from this repository's `data/videos.json`, `data/library/`, `data/local-media.json`, `covers/`, and `media/`. The build includes all 203 current examples; unpublished prompts are labeled as such.

Build and check locally:

```sh
python3 site/build.py
python3 site/check.py
python3 -m http.server 4173 --bind 127.0.0.1 --directory _site
```

The output is in `_site/`. The Pages workflow builds the site on pushes to `main` after GitHub Pages is configured to use GitHub Actions. The expected URL is `https://leaddeopenlab.github.io/awesome-fable-5.2-video-prompts/`.
