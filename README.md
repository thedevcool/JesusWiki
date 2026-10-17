# JesusWiki

An open source wiki that sets what the Bible records about Jesus beside independent sources from outside the Bible: Roman historians, Jewish writers, hostile critics, and others. Every claim is graded by evidence strength and carries its strongest objection.

The goal is a resource that is useful to believers, skeptics, and students alike, which means it only works if it is honest about weak evidence as well as strong evidence.

## How it works

- Each entry is one JSON file in `entries/`.
- `scripts/build.mjs` validates every entry and builds the site into `dist/`.
- GitHub Actions deploys `dist/` to GitHub Pages on every merge to `main`.
- Pull requests are validated automatically before anyone reviews them.

## Run it locally

```
node scripts/build.mjs
npx serve dist
```

Live site: https://thedevcool.github.io/JesusWiki/

## Publish your own copy

1. Create a repository named `jesuswiki` on GitHub and push this folder to it.
2. In the repository, go to Settings, then Pages, and set the source to **GitHub Actions**.
3. In `site/index.html`, change the `REPO` line to point at your repository.
4. Push to `main`. The site appears at `https://YOUR-USERNAME.github.io/jesuswiki/`.

## Contribute

See [CONTRIBUTING.md](CONTRIBUTING.md). Short version: open an issue with the entry form, or add a JSON file to `entries/` and open a pull request.

## Licenses

Code is MIT (see `LICENSE`). Entry text in `entries/` is CC BY-SA 4.0, so it can be reused with credit and the same terms.
