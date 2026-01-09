# App Development Resources

Reference document for building a nutrition tracking app with meal planning capabilities.

## General Nutrition Databases

### USDA FoodData Central (Recommended for Generic Foods)

**Overview:**
* Official USDA database with comprehensive nutritional data
* Best choice for meal planning with common ingredients (like "1 cup of milk")
* Website: https://fdc.nal.usda.gov/

**Formats Available:**
* CSV files (downloadable)
* Excel files (downloadable)
* JSON (via API and some downloads)
* XML (via API)
* RESTful API for programmatic access

**Datasets:**
* Foundation Foods
* Experimental Foods
* Legacy Foods (SR Legacy)
* Food and Nutrient Database for Dietary Studies (FNDDS)
* USDA Global Branded Food Products Database (includes UPCs)

**Download Location:**
* https://fdc.nal.usda.gov/download-datasets.html

**API:**
* https://fdc.nal.usda.gov/api-guide.html
* Requires API key (free signup)

**Open-Source Database Implementation:**
* **USDA-SQLite**: Converts USDA data into SQLite format
* GitHub: https://github.com/alyssaq/usda-sqlite
* Includes scripts to generate schema and import data
* Makes querying and integration easier

### Open Food Facts

**Overview:**
* Collaborative, crowdsourced database
* Good for branded products worldwide
* Free and open-source
* Open Database License
* Website: https://world.openfoodfacts.org/

**Formats Available:**
* JSON (API and downloads)
* CSV exports
* MongoDB dumps
* Parquet format (~4.44 GB, more efficient)

**API:**
* RESTful API: `https://world.openfoodfacts.org/api/v0/product/{barcode}.json`
* Example: `https://world.openfoodfacts.org/api/v0/product/3017620422003.json`
* API docs: https://openfoodfacts.github.io/openfoodfacts-server/api/
* No API key required

**Download Location:**
* https://world.openfoodfacts.org/data
* Daily data exports available

### Other Databases

**OpenNutrition Foods:**
* Free, public nutritional database
* AI-enhanced for accuracy
* Open Database License
* Includes generic, branded, and restaurant foods
* Website: https://www.opennutrition.app/

**FooDB:**
* Open-access database for unprocessed foods
* Chemical composition data
* Good for raw ingredients

**Open Food Repo:**
* Community-driven database for barcoded products
* Good coverage of European products
* Website: https://www.foodrepo.org/
* API available

## SKU/Barcode Lookup Solutions

### Open Food Facts (Best Open-Source Option)

**Features:**
* Full barcode/UPC lookup support
* Free and open-source
* Returns nutrition facts panel data (matches product labels)
* Mobile app available for scanning
* Works with any programming language via REST API

**API Endpoint:**
```
GET https://world.openfoodfacts.org/api/v0/product/{barcode}.json
```

**Language Support:**
* Works via REST API from any language (JavaScript, Python, Go, Rust, Java, C#, etc.)
* No special libraries required - just HTTP GET requests
* Returns JSON response

**NPM Packages (if using JavaScript/TypeScript):**
* `openfoodfacts-nodejs`
* `openfoodfacts-api`

**Python Packages:**
* `openfoodfacts` (PyPI)

### Other Barcode Lookup Options

**Open Food Repo:**
* Barcode scanning support
* Community-driven open database
* API available for barcode lookups
* Good coverage of European products

**Nutritionix (Commercial with Free Tier):**
* UPC/barcode lookup via API
* Large verified database
* Free tier available (limited requests)
* May require API key
* Website: https://www.nutritionix.com/

**Datakick:**
* Open product database
* Barcode scanning support
* Includes nutrition facts and ingredients
* Website: https://gtinsearch.org/

## Downloadable Databases for Local/Offline Use

### Open Food Facts Data Dumps

**Disk Space Requirements:**
* **Compressed (JSONL)**: ~7 GB
* **Decompressed (JSONL)**: ~43 GB
* **Parquet format**: ~4.44 GB (more efficient, recommended)
* **With product images**: Additional space (varies, can be substantial)
* **Minimum recommended**: 50 GB free space
* **Recommended**: 60-70 GB for processing and temporary files

**Formats Available:**
* JSON dumps
* CSV exports
* MongoDB dumps
* Parquet format (most efficient)

**Download Location:**
* https://world.openfoodfacts.org/data
* Daily exports available

**Import Options:**
* Import into SQLite (index by barcode for fast lookups)
* Import into PostgreSQL/MySQL
* Import into MongoDB (if using MongoDB dumps)
* Use Parquet format with tools like DuckDB for efficient querying

**Space-Saving Tips:**
* Download only nutrition-related fields (skip images, ingredients text, etc.)
* Use Parquet format instead of JSON
* Filter by country/region if only needing specific markets
* Use incremental updates instead of full dumps

### USDA FoodData Central Downloads

**API key***
I signed up with brandon_draper4@yahoo.com, and my key is exported by .zshrc with name: USDA_API_KEY

**Formats:**
* CSV files
* Excel files
* JSON (via API)

**Datasets:**
* Foundation Foods
* Branded Foods (includes UPCs for barcode matching)
* SR Legacy
* FNDDS

**Import Options:**
* Import CSV/Excel into any database (SQLite, PostgreSQL, MySQL, etc.)
* Use USDA-SQLite project for pre-built SQLite database
* Data is public domain - can process however you like

## Implementation Approaches

### Option A: Use API (Online)

**Pros:**
* Simple HTTP GET requests
* No data storage needed
* Always up-to-date
* Works from any programming language

**Cons:**
* Requires internet connection
* API rate limits may apply
* Slower for high-volume lookups

**Example (Open Food Facts):**
```javascript
// JavaScript example
fetch(`https://world.openfoodfacts.org/api/v0/product/${barcode}.json`)
  .then(response => response.json())
  .then(data => {
    // Access nutrition data: data.product.nutriments
  });
```

### Option B: Download and Use Locally (Offline)

**Pros:**
* No internet required after download
* Fast lookups (indexed database)
* No API rate limits
* Better for high-volume usage

**Cons:**
* Requires significant disk space (50+ GB for full Open Food Facts)
* Need to update database periodically
* Initial setup more complex

**Setup Steps:**
1. Download Open Food Facts JSON/CSV dump or Parquet file
2. Import into SQLite (or preferred database)
3. Index by barcode/UPC
4. Query locally without internet

### Option C: Hybrid Approach

**Strategy:**
* Download database for common products
* Use API as fallback for missing products
* Cache API results locally

**Benefits:**
* Fast lookups for common items (offline)
* Coverage for rare products (via API)
* Gradually build local cache

## Recommendations

**For SKU/Barcode Lookups:**
* **Open Food Facts** is the best open-source option
* Supports both API access and downloadable dumps
* Works with any programming language via REST API
* Can be used offline if you download the data dumps

**For Generic Foods (Meal Planning):**
* **USDA FoodData Central** is most authoritative
* Also has downloadable datasets
* Branded Foods dataset includes UPCs, so you can match barcodes
* Use USDA-SQLite project for pre-built SQLite database

**Best Strategy:**
* Use both: USDA for generic ingredients, Open Food Facts for branded products with barcode scanning
* Start with API approach for MVP
* Move to local database if you need offline support or high-volume lookups

## Resources

* Open Food Facts API Docs: https://openfoodfacts.github.io/openfoodfacts-server/api/
* USDA FoodData Central API Guide: https://fdc.nal.usda.gov/api-guide.html
* USDA-SQLite Project: https://github.com/alyssaq/usda-sqlite
* Open Food Facts Data Downloads: https://world.openfoodfacts.org/data
* USDA Data Downloads: https://fdc.nal.usda.gov/download-datasets.html

