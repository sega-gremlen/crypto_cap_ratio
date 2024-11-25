# TokenCap Ratio Analyzer

## Description
This script collects and processes cryptocurrency data using APIs from Cryptorank and CoinMarketCap. It retrieves current market capitalization, all-time high (ATH) market cap, and launch dates for the top coins. The data is filtered and sorted by the ratio of current market cap to ATH market cap, helping to identify tokens with significant market cap discrepancies. Ideal for analyzing undervalued or overvalued assets in the crypto market.

## Brief Algorithm

1. **Load Environment Variables**:
   - Loads API keys from `.env` file.

2. **Collect Primary Data**:
   - Fetches coins data from Cryptorank API.

3. **Parse ATH Market Cap**:
   - Parse ATH market cap from Cryptorank website.

4. **Get Launch Dates**:
   - Fetches launch dates from CoinMarketCap API.

5. **Filter Launch Dates**:
   - Filters coins launched after January 1, 2021.

6. **Sort by Market Cap Ratio**:
   - Sorts coins by the ratio of current to ATH market cap.

## Adjustable Settings in the Class Attributes

- **`filter_coin_launch_date`**:
  - **Description**: Defines the cutoff date for filtering coins.
  - **Default**: `January 1, 2021`

- **`filter_toggle`**:
  - **Description**: Enables or disables the launch date filter.
  - **Default**: `False`

- **`res_file_name`**:
  - **Description**: Name of the file where data is saved.
  - **Default**: `'test.json'`

- **`top_coins_count`**:
  - **Description**: Number of top coins to fetch.
  - **Default**: `100`

- **`cryptorank_api_key`** and **`cmc_api_key`**:
  - **Description**: API keys loaded from environment variables.
  - **Default**: Loaded from `.env` file
