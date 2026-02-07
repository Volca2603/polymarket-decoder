from dataclasses import dataclass
from decimal import Decimal
from web3 import Web3
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Polymarket交易所合约地址
EXCHANGE_ADDRESSES = {
    "CTF": "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E",
    "NegRisk": "0xC5d563A36AE78145C45a50134d48A1215220f80a"
}

# OrderFilled事件ABI
ORDER_FILLED_ABI = {
    "anonymous": False,
    "inputs": [
        {"indexed": True, "name": "orderHash", "type": "bytes32"},
        {"indexed": True, "name": "maker", "type": "address"},
        {"indexed": True, "name": "taker", "type": "address"},
        {"indexed": False, "name": "makerAssetId", "type": "uint256"},
        {"indexed": False, "name": "takerAssetId", "type": "uint256"},
        {"indexed": False, "name": "makerAmountFilled", "type": "uint256"},
        {"indexed": False, "name": "takerAmountFilled", "type": "uint256"},
        {"indexed": False, "name": "fee", "type": "uint256"}
    ],
    "name": "OrderFilled",
    "type": "event"
}

# 生成事件签名
ORDER_FILLED_SIGNATURE = Web3.keccak(text="OrderFilled(bytes32,address,address,uint256,uint256,uint256,uint256,uint256)").hex()

@dataclass(frozen=True)
class Trade:
    """交易数据类"""
    tx_hash: str
    log_index: int
    exchange: str
    order_hash: str
    maker: str
    taker: str
    maker_asset_id: str
    taker_asset_id: str
    maker_amount: str
    taker_amount: str
    fee: str
    price: str
    token_id: str
    side: str

class TradeDecoder:
    """交易解码器"""
    def __init__(self):
        """初始化解码器"""
        rpc_url = os.getenv("RPC_URL")
        if not rpc_url:
            raise ValueError("RPC_URL not set in .env file")
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        
    def decode_trades(self, tx_hash):
        """解码交易中的OrderFilled事件
        
        Args:
            tx_hash: 交易哈希
            
        Returns:
            交易列表
        """
        try:
            # 获取交易回执
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            trades = []
            
            for log in receipt["logs"]:
                # 检查是否是OrderFilled事件
                if len(log["topics"]) > 0:
                    try:
                        # 尝试解码事件数据
                        decoded_log = self._decode_order_filled(log)
                        
                        # 检查是否是Polymarket交易所合约
                        if log["address"].lower() in [addr.lower() for addr in EXCHANGE_ADDRESSES.values()]:
                            # 过滤重复日志
                            if decoded_log["taker"].lower() == log["address"].lower():
                                continue
                            
                            # 计算价格和方向
                            price, token_id, side = self._calculate_price_and_side(
                                decoded_log["makerAssetId"],
                                decoded_log["takerAssetId"],
                                decoded_log["makerAmountFilled"],
                                decoded_log["takerAmountFilled"]
                            )
                            
                            # 创建交易对象
                            trade = Trade(
                                tx_hash=tx_hash,
                                log_index=log["logIndex"],
                                exchange=log["address"],
                                order_hash=str(decoded_log["orderHash"]),
                                maker=decoded_log["maker"],
                                taker=decoded_log["taker"],
                                maker_asset_id=str(decoded_log["makerAssetId"]),
                                taker_asset_id=str(decoded_log["takerAssetId"]),
                                maker_amount=str(decoded_log["makerAmountFilled"]),
                                taker_amount=str(decoded_log["takerAmountFilled"]),
                                fee=str(decoded_log["fee"]),
                                price=str(price),
                                token_id=str(token_id),
                                side=side
                            )
                            trades.append(trade)
                    except Exception as e:
                        # 忽略解码失败的日志
                        continue
            
            return trades
        except Exception as e:
            print(f"Error decoding trades: {e}")
            return []
    
    def _decode_order_filled(self, log):
        """解码OrderFilled事件数据
        
        Args:
            log: 日志对象
            
        Returns:
            解码后的事件数据
        """
        # 使用web3.py解码事件
        # 创建临时合约对象
        contract = self.w3.eth.contract(address=log["address"], abi=[ORDER_FILLED_ABI])
        decoded = contract.events.OrderFilled().process_log(log)
        
        return {
            "orderHash": decoded["args"]["orderHash"],
            "maker": decoded["args"]["maker"],
            "taker": decoded["args"]["taker"],
            "makerAssetId": decoded["args"]["makerAssetId"],
            "takerAssetId": decoded["args"]["takerAssetId"],
            "makerAmountFilled": decoded["args"]["makerAmountFilled"],
            "takerAmountFilled": decoded["args"]["takerAmountFilled"],
            "fee": decoded["args"]["fee"]
        }
    
    def _calculate_price_and_side(self, maker_asset_id, taker_asset_id, maker_amount, taker_amount):
        """计算价格和交易方向
        
        Args:
            maker_asset_id: 挂单方资产ID
            taker_asset_id: 吃单方资产ID
            maker_amount: 挂单方金额
            taker_amount: 吃单方金额
            
        Returns:
            (price, token_id, side)
        """
        if maker_asset_id == 0:
            # maker支付USDC，买入token
            price = Decimal(maker_amount) / Decimal(taker_amount)
            token_id = taker_asset_id
            side = "BUY"
        else:
            # maker支付token，卖出获取USDC
            price = Decimal(taker_amount) / Decimal(maker_amount)
            token_id = maker_asset_id
            side = "SELL"
        
        return price, token_id, side

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--tx-hash", required=True, help="交易哈希")
    parser.add_argument("--output", default=None, help="输出文件路径")
    args = parser.parse_args()
    
    decoder = TradeDecoder()
    trades = decoder.decode_trades(args.tx_hash)
    
    # 转换为字典列表
    trades_dict = [
        {
            "tx_hash": t.tx_hash,
            "log_index": t.log_index,
            "exchange": t.exchange,
            "order_hash": t.order_hash,
            "maker": t.maker,
            "taker": t.taker,
            "maker_asset_id": t.maker_asset_id,
            "taker_asset_id": t.taker_asset_id,
            "maker_amount": t.maker_amount,
            "taker_amount": t.taker_amount,
            "fee": t.fee,
            "price": t.price,
            "token_id": t.token_id,
            "side": t.side
        }
        for t in trades
    ]
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(trades_dict, f, indent=2, ensure_ascii=False)
        print(f"交易解析结果已保存到: {args.output}")
    else:
        print(json.dumps(trades_dict, indent=2, ensure_ascii=False))
