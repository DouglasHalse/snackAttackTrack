# Snack Attack Track™ Website

This directory contains the GitHub Pages website for Snack Attack Track.

## Viewing the Site

Once GitHub Pages is enabled, the site will be available at:
`https://douglashalse.github.io/snackAttackTrack/`

## Enabling GitHub Pages

1. Go to your repository settings on GitHub
2. Navigate to **Pages** section (under Code and automation)
3. Under **Source**, select `Deploy from a branch`
4. Select branch: `main`
5. Select folder: `/docs`
6. Click **Save**

GitHub will automatically build and deploy the site within a few minutes.

## Local Development

To preview the site locally, simply open `index.html` in your web browser:

```bash
# From the repository root
cd docs
# Open in your default browser (Windows)
start index.html
# Or (Linux/macOS)
open index.html
```

## Customization

- **index.html** - Main landing page with all content
- **_config.yml** - Jekyll configuration (optional)

### Adding Screenshots

Replace the placeholder section in `index.html` with actual screenshots:

```html
<img src="screenshot.png" alt="Snack Attack Track Interface" style="width: 100%; border-radius: 12px;">
```

### Updating Content

All content is in `index.html`. The page is fully self-contained with inline CSS for easy editing.

## Features of the Website

- ✅ Responsive design (mobile-friendly)
- ✅ Modern, clean interface
- ✅ Feature highlights
- ✅ Quick start guides
- ✅ Technology stack showcase
- ✅ Hardware requirements
- ✅ Documentation links
- ✅ Contribution guidelines

## Analytics

To add Google Analytics, update `_config.yml` with your tracking ID.

## Custom Domain (Optional)

To use a custom domain:

1. Create a file named `CNAME` in this directory
2. Add your domain name (e.g., `snackattack.example.com`)
3. Configure DNS records with your domain provider
4. Point to GitHub Pages (see [GitHub docs](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site))
