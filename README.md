# Polymarket Decoder

A comprehensive tool for decoding Polymarket trading events and market parameters on Polygon blockchain.

## Features

- **Trade Decoder**: Parses `OrderFilled` events and extracts trade details
- **Market Decoder**: Retrieves market information from Gamma API and calculates token IDs
- **Gamma API Integration**: Fetches market data using event slugs
- **ERC-1155 Token ID Calculation**: Computes YES/NO token IDs for binary markets
- **JSON Output**: Produces structured JSON output for easy integration

## Installation

### Prerequisites

- Python 3.8+
- Web3.py
- Requests
- python-dotenv

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Volca2603/polymarket-decoder.git
   cd polymarket-decoder
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   - Copy the example environment file
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` file and add your Polygon RPC URL
     ```
     RPC_URL=https://polygon-mainnet.g.alchemy.com/v2/YOUR_API_KEY
     ```

## Usage

### Trade Decoder

Parses `OrderFilled` events from a transaction and extracts trade details.

```bash
# Decode trades from a transaction
python -m src.trade_decoder --tx-hash 0x916cad96dd5c219997638133512fd17fe7c1ce72b830157e4fd5323cf4f19946

# Save output to file
python -m src.trade_decoder --tx-hash 0x916cad96dd5c219997638133512fd17fe7c1ce72b830157e4fd5323cf4f19946 --output ./data/trades.json
```

### Market Decoder

Retrieves market information and calculates token IDs using Gamma API.

```bash
# Get market info by event slug
python -m src.market_decoder --event-slug will-there-be-another-us-government-shutdown-by-january-31

# Save output to file
python -m src.market_decoder --event-slug will-there-be-another-us-government-shutdown-by-january-31 --output ./data/market.json

# Get market info by condition ID
python -m src.market_decoder --condition-id 0x43ec78527bd98a0588dd9455685b2cc82f5743140cb3a154603dc03c02b57de5
```

## Output Format

### Trade Decoder Output

```json
[
  {
    "order_hash": "0x7e611f8b982a8c80b383d5b27adc75d350d36affe8e346e6e752b3d13452239f",
    "maker": "0x38E59B36Aae31b164200d0Cad7C3fE5e0eE795E7",
    "taker": "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E",
    "maker_asset_id": "86248052962732477419195066171644927318594410242409575342562896779375831040862",
    "taker_asset_id": "14814299175597063627737248217188360009609372694600692883419322192401645888021",
    "maker_amount_filled": "100000000",
    "taker_amount_filled": "50000000",
    "fee": "0",
    "price": "0.5",
    "side": "buy",
    "token_id": "86248052962732477419195066171644927318594410242409575342562896779375831040862"
  }
]
```

### Market Decoder Output

```json
{
  "conditionId": "0x43ec78527bd98a0588dd9455685b2cc82f5743140cb3a154603dc03c02b57de5",
  "questionId": "0xa583fb75d98fe392d8d9e0a23a8cc2107e8d5203b817ce8b381c9562254936cf",
  "oracle": "0x157Ce2d672854c848c9b79C49a8Cc6cc89176a49",
  "collateralToken": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
  "yesTokenId": "86248052962732477419195066171644927318594410242409575342562896779375831040862",
  "noTokenId": "14814299175597063627737248217188360009609372694600692883419322192401645888021",
  "outcomeSlotCount": 2
}
```

## Project Structure

```
polymarket-decoder/
├── data/               # Output files
├── src/                # Source code
│   ├── ctf/            # CTF-related utilities
│   │   ├── __init__.py
│   │   └── derive.py   # Token ID calculation
│   ├── __init__.py
│   ├── market_decoder.py  # Market decoder implementation
│   └── trade_decoder.py   # Trade decoder implementation
├── .env                # Environment variables
├── .env.example        # Environment variables template
├── .gitignore          # Git ignore file
├── README.md           # This file
└── requirements.txt    # Dependencies
```

## API Reference

### Gamma API

The market decoder uses the Gamma API to fetch market information:

```
GET https://gamma-api.polymarket.com/events?slug={event-slug}
```

### Web3.py Event Decoding

The trade decoder uses Web3.py to parse Ethereum events:

```python
# Example event parsing
contract = w3.eth.contract(address=address, abi=ABI)
decoded = contract.events.OrderFilled().process_log(log)
```

## License

MIT

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Acknowledgments

- Polymarket for creating the CTF exchange
- Gamma for providing the market API
- Web3.py for Ethereum interaction
