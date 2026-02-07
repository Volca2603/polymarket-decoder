# Polymarket Decoder

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![Web3.py](https://img.shields.io/badge/Web3.py-6.0%2B-green?style=flat-square&logo=ethereum)](https://web3py.readthedocs.io/)
[![Polygon](https://img.shields.io/badge/Polygon-Mainnet-yellow?style=flat-square&logo=polygon)](https://polygon.technology/)
[![GitHub](https://img.shields.io/badge/GitHub-Open%20Source-lightgrey?style=flat-square&logo=github)](https://github.com/Volca2603/polymarket-decoder)

一个用于解析 Polygon 区块链上 Polymarket 交易事件和市场参数的综合工具。

## 功能特性

- **交易解析器**：解析 `OrderFilled` 事件并提取交易详情
- **市场解析器**：从 Gamma API 获取市场信息并计算代币 ID
- **Gamma API 集成**：使用事件 slug 获取市场数据
- **ERC-1155 代币 ID 计算**：为二元市场计算 YES/NO 代币 ID
- **JSON 输出**：生成结构化 JSON 输出，便于集成

## 安装说明

### 前提条件

- Python 3.8+
- Web3.py
- Requests
- python-dotenv

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/Volca2603/polymarket-decoder.git
   cd polymarket-decoder
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境变量**
   - 复制环境变量示例文件
     ```bash
     cp .env.example .env
     ```
   - 编辑 `.env` 文件并添加 Polygon RPC URL
     ```
     RPC_URL=https://polygon-mainnet.g.alchemy.com/v2/YOUR_API_KEY
     ```

## 使用方法

### 交易解析器

解析交易中的 `OrderFilled` 事件并提取交易详情。

```bash
# 解析交易中的订单事件
python -m src.trade_decoder --tx-hash 0x916cad96dd5c219997638133512fd17fe7c1ce72b830157e4fd5323cf4f19946

# 将输出保存到文件
python -m src.trade_decoder --tx-hash 0x916cad96dd5c219997638133512fd17fe7c1ce72b830157e4fd5323cf4f19946 --output ./data/trades.json
```

### 市场解析器

从 Gamma API 获取市场信息并计算代币 ID。

```bash
# 通过事件 slug 获取市场信息
python -m src.market_decoder --event-slug will-there-be-another-us-government-shutdown-by-january-31

# 将输出保存到文件
python -m src.market_decoder --event-slug will-there-be-another-us-government-shutdown-by-january-31 --output ./data/market.json

# 通过 condition ID 获取市场信息
python -m src.market_decoder --condition-id 0x43ec78527bd98a0588dd9455685b2cc82f5743140cb3a154603dc03c02b57de5
```

## 输出格式

### 交易解析器输出

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

### 市场解析器输出

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

## 项目结构

```
polymarket-decoder/
├── data/               # 输出文件
├── src/                # 源代码
│   ├── ctf/            # CTF 相关工具
│   │   ├── __init__.py
│   │   └── derive.py   # 代币 ID 计算
│   ├── __init__.py
│   ├── market_decoder.py  # 市场解析器实现
│   └── trade_decoder.py   # 交易解析器实现
├── .env                # 环境变量
├── .env.example        # 环境变量模板
├── .gitignore          # Git 忽略文件
├── README.md           # 本文档
└── requirements.txt    # 依赖项
```

## API 参考

### Gamma API

市场解析器使用 Gamma API 获取市场信息：

```
GET https://gamma-api.polymarket.com/events?slug={event-slug}
```

### Web3.py 事件解码

交易解析器使用 Web3.py 解析以太坊事件：

```python
# 事件解析示例
contract = w3.eth.contract(address=address, abi=ABI)
decoded = contract.events.OrderFilled().process_log(log)
```


## 许可证

MIT
