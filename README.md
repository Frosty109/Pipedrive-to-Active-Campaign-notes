# Pipedrive to Active Campaign Note Sync Tool (Beta)

⚠️ **CAUTION: This tool is currently under development and not fully completed. Use with caution in production environments.**

A Python-based tool for synchronizing notes between Pipedrive and Active Campaign platforms. If you plan to use this tool, test with a small number of notes first.

## Features

* **One-way synchronization of notes from Pipedrive to Active Campaign**
* Account matching between platforms
* User matching between platforms
* HTML cleanup for note content
* Pagination handling for large datasets
* Duplicate note detection

## Requirements

```python
python
beautifulsoup4
requests
```

## Configuration

The tool requires the following credentials:

### Pipedrive
* API token
* Base URL

### Active Campaign
* Base URL (format: https://account_name.api-us1.com)
* API keys for users (configured in `active_campaign_api_list`)

## Usage

1. Configure the required API credentials in the script
2. Run the script:
   ```bash
   python main.py
   ```
3. Enter the requested Pipedrive API token when prompted
4. Enter the Active Campaign base URL when prompted

## Known Limitations

* One-way sync only (Pipedrive → Active Campaign)
* Requires manual API key configuration
* Limited error handling
* No logging system implemented
* User matching may require manual verification

## Process Flow

1. Retrieves notes from Pipedrive
2. Gets account list from Active Campaign
3. Gets user list from Active Campaign
4. Matches accounts and users between platforms
5. Syncs notes to matched Active Campaign accounts
6. Performs note content cleanup
7. Checks for duplicate notes before syncing

## Security Notes

* Store API keys securely (not in the script)
* Validate all data before syncing
* Test thoroughly in a non-production environment first

## Future Improvements

* Improved error handling
* Logging system
* Configuration file support
* Bidirectional sync support
* Better security measures
* Progress tracking
* Automated testing
