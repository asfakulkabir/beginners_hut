# Beginners Hut — Placeholder Assets

Every image and icon in the new portfolio frontend currently points at a file in
`static/images/placeholders/`. They are deliberately loud (dashed frame + label)
so they are easy to find and swap.

**To replace one:** overwrite the file with your own artwork using the **same
filename and aspect ratio**. Nothing else needs to change.

| File | Used for | Size | Notes |
| --- | --- | --- | --- |
| `logo.svg` | Navbar + footer brand mark | 48×48 | Also `favicon.svg` |
| `favicon.svg` | Favicon reference | 48×48 | `templates/portfolio/portfolio_base.html` still points at `images/icons/favicon.png` — replace that file too, or switch the tag |
| `hero-main.svg` | Homepage hero visual | 900×1000 | Displayed `aspect-[9/10]` on desktop, `4/3` on mobile |
| `hero-secondary.svg` | Office map card | 600×600 | Cropped to `16/9` |
| `about-team.svg` | About page team photo | 900×700 | |
| `cta-bg.svg` | CTA band texture | 1200×600 | Texture only — no label text |
| `icon-website.svg` | Service card icon | 64×64 | Gradient tile, white glyph |
| `icon-software.svg` | Service card icon | 64×64 | |
| `icon-graphics.svg` | Service card icon | 64×64 | Orange/yellow tile |
| `icon-ecommerce.svg` | Service card icon | 64×64 | |
| `icon-video.svg` | Service card icon | 64×64 | Orange/yellow tile |
| `icon-consultation.svg` | Spare icon | 64×64 | Not currently used |
| `icon-support.svg` | Spare icon | 64×64 | Not currently used |
| `project-1..6.svg` | Portfolio card fallback | 800×600 | Rotated when a project has no uploaded image |
| `blog-1..3.svg` | Blog card fallback | 800×500 | Rotated per card |
| `avatar-1..3.svg` | Testimonial / social-proof fallback | 200×200 | Square |
| `client-1..6.svg` | Client marquee logos | 200×64 | Duplicated for the seamless loop |

## Service icons

Currently referenced in `templates/portfolio/portfolio.html`. If you prefer a
different icon set, change the `src` for that card:

```django
<img src="{% static 'images/icons/your-icon.svg' %}" alt="..." width="56" height="56" ...>
```

Square icons with a transparent background work best — the tile shape is
provided by the surrounding rounded container.

## Real uploads (from the admin panel)

These are **not** placeholders and already render live data:

- `Website_Portfolio.image` → website cards
- `Print_Design.image` → print gallery
- `Post_Design.image` → social media gallery
- `Testimonial.image` → testimonial avatars
- `Blog_Post.image` → blog covers

Cards fall back to a placeholder automatically when the image field is empty.