# Playwright Codegen Instructions

## Step 2: Record Actions with Playwright Codegen

This is the most important step to get the correct "selectors" for all the elements you need to interact with.

### Launch Codegen

```bash
cd /home/nichols-ai/sylectus-monitor
source venv/bin/activate
python -m playwright codegen https://www.sylectus.net/
```

### Perform Actions in the Browser

A browser window will open. Perform the following actions slowly and deliberately. The code will be generated for you in the Playwright Codegen window.

1. **Log In**: Type your username and password, then click the login button.

2. **Navigate**: Go to the page that lists the items/leads you want to monitor.

3. **Identify a Single Item**: Find one complete listing block on the page. Click on its main container div to get a selector for what one "item" looks like.

4. **Identify Data Points**: Within that single item, click on the specific pieces of data you want to scrape:
   - The item's title
   - The price
   - The pickup location
   - The delivery location
   - The "bid" button or contact info

5. **Copy the Code**: Copy all the generated Python code from the Codegen window into a temporary text file. This is your reference.

### Update the Scraper

Once you have the selectors from Codegen, update `scraper_sylectus.py`:

1. Replace the login selectors in the login sequence
2. Replace the item container selector: `.selector-for-one-item-block`
3. Replace the data point selectors:
   - `.selector-for-the-title`
   - `.selector-for-the-price`
   - `.selector-for-pickup`
   - `.selector-for-delivery`

### Example Selectors to Look For

Based on typical Sylectus structure:
- Login form: `input[name="username"]`, `input[type="password"]`
- Item containers: `table tr`, `.load-row`, `[class*="item"]`
- Data points: `td:nth-child(1)`, `td:nth-child(2)`, etc.
- Links: `a[href*="load"]`, `a[href*="bid"]`

### Testing

1. Run with `headless=False` first to watch the browser
2. Check that login works correctly
3. Verify that items are being found and scraped
4. Test the duplicate prevention with multiple runs

```bash
# Test the scraper
python scraper_sylectus.py
```