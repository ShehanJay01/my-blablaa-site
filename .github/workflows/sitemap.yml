name: Generate XML Sitemap

on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    env:
      FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true
      
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.x'

      - name: Install dependencies
        run: pip install requests

      - name: Run sitemap script
        run: python generate_sitemap.py

      - name: Run sitemap script
        run: |
          python generate_sitemap.py
          ls -l # දැනට folder එකේ තියෙන files list එකක් පෙන්වන්න

      - name: Commit and push changes
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "github-actions[bot]@users.noreply.github.com"
          if [ -f sitemap.xml ]; then
            git add sitemap.xml
            git commit -m "Auto-update sitemap [skip ci]" || echo "No changes to commit"
            git push origin main
          else
            echo "sitemap.xml not found! Skipping commit."
            exit 1
          fi
