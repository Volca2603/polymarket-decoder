from dataclasses import dataclass
from web3 import Web3
import json
import os
from dotenv import load_dotenv
from .ctf.derive import derive_binary_positions
import requests

load_dotenv()

GAMMA_API_BASE = "https://gamma-api.polymarket.com"
# USDC.e 地址（Polymarket 使用的抵押品）
USDC_E_ADDRESS = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"

# ConditionPreparation 事件 ABI
CONDITION_PREPARATION_ABI = {
    "anonymous": False,
    "inputs": [
        {"indexed": True, "name": "conditionId", "type": "bytes32"},
        {"indexed": True, "name": "oracle", "type": "address"},
        {"indexed": False, "name": "questionId", "type": "bytes32"},
        {"indexed": False, "name": "outcomeSlotCount", "type": "uint256"}
    ],
    "name": "ConditionPreparation",
    "type": "event"
}

@dataclass(frozen=True)
class Market:
    """市场数据类"""
    condition_id: str
    question_id: str
    oracle: str
    collateral_token: str
    yes_token_id: str
    no_token_id: str
    outcome_slot_count: int = 2

class MarketDecoder:
    """市场参数解码器"""
    def __init__(self):
        """初始化解码器"""
        rpc_url = os.getenv("RPC_URL")
        if not rpc_url:
            raise ValueError("RPC_URL not set in .env file")
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
    
    def decode_from_condition_id(self, condition_id):
        """根据 conditionId 解码市场参数
        
        Args:
            condition_id: 条件ID
            
        Returns:
            市场对象
        """
        # 注意：这里需要从其他渠道获取 oracle 和 questionId
        # 由于没有提供具体的获取方法，这里使用示例值
        # 实际使用时，需要通过 Gamma API 或其他方式获取
        oracle = "0x157Ce2d672854c848c9b79C49a8Cc6cc89176a49"  # 示例预言机地址
        question_id = "0x0000000000000000000000000000000000000000000000000000000000000000"  # 示例问题ID
        
        # 计算 YES/NO TokenId
        positions = derive_binary_positions(
            oracle=oracle,
            question_id=question_id,
            condition_id=condition_id,
            collateral_token=USDC_E_ADDRESS
        )
        
        # 创建市场对象
        market = Market(
            condition_id=condition_id,
            question_id=question_id,
            oracle=oracle,
            collateral_token=USDC_E_ADDRESS,
            yes_token_id=positions.position_yes,
            no_token_id=positions.position_no
        )
        
        return market
    
    def get_event_by_slug(self, slug):
        """通过 slug 从 Gamma API 获取事件信息
    
        Args:
            slug: 事件短标识
        
        Returns:
            市场信息字典
        
        Raises:
            ValueError: 如果 API 调用失败或事件不存在
        """
        # 使用正确的 API 端点
        url = f"https://gamma-api.polymarket.com/events?slug={slug}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            events = response.json()
            
            # 检查响应是否为空
            if not events:
                raise ValueError(f"No events found for slug '{slug}'")
            
            # 获取第一个事件（通常只有一个）
            event = events[0]
            
            # 检查是否有 markets 字段
            if "markets" not in event or not event["markets"]:
                raise ValueError(f"No markets found for event with slug '{slug}'")
            
            # 获取第一个市场（通常只有一个）
            market = event["markets"][0]
            
            # 从市场对象中提取必要的字段
            market_info = {
                "conditionId": market.get("conditionId"),
                "questionId": market.get("questionID"),  # 注意：API 中是 questionID 而不是 questionId
                "oracle": "0x157Ce2d672854c848c9b79C49a8Cc6cc89176a49",  # 示例预言机地址
                "clobTokenIds": market.get("clobTokenIds")  # 用于验证
            }
            
            return market_info
            
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch market: {str(e)}")
        except (IndexError, KeyError) as e:
            raise ValueError(f"Invalid API response structure: {str(e)}")

    def decode_from_log(self, log):
        """根据 ConditionPreparation 事件日志解码市场参数
        
        Args:
            log: 日志对象
            
        Returns:
            市场对象
        """
        try:
            # 解码事件数据
            decoded_log = self._decode_condition_preparation(log)
            
            # 计算 YES/NO TokenId
            positions = derive_binary_positions(
                oracle=decoded_log["oracle"],
                question_id=decoded_log["questionId"],
                condition_id=decoded_log["conditionId"],
                collateral_token=USDC_E_ADDRESS
            )
            
            # 创建市场对象
            market = Market(
                condition_id=decoded_log["conditionId"],
                question_id=decoded_log["questionId"],
                oracle=decoded_log["oracle"],
                collateral_token=USDC_E_ADDRESS,
                yes_token_id=positions.position_yes,
                no_token_id=positions.position_no,
                outcome_slot_count=decoded_log["outcomeSlotCount"]
            )
            
            return market
        except Exception as e:
            print(f"Error decoding from log: {e}")
            raise
    
    def _decode_condition_preparation(self, log):
        """解码 ConditionPreparation 事件数据
        
        Args:
            log: 日志对象
            
        Returns:
            解码后的事件数据
        """
        # 创建临时合约对象
        contract = self.w3.eth.contract(address=log["address"], abi=[CONDITION_PREPARATION_ABI])
        decoded = contract.events.ConditionPreparation().process_log(log)
        
        return {
            "conditionId": decoded["args"]["conditionId"].hex(),
            "oracle": decoded["args"]["oracle"],
            "questionId": decoded["args"]["questionId"].hex(),
            "outcomeSlotCount": decoded["args"]["outcomeSlotCount"]
        }
    
    def to_json(self, market):
        """将市场对象转换为JSON
        
        Args:
            market: 市场对象
            
        Returns:
            JSON字符串
        """
        market_dict = {
            "conditionId": market.condition_id,
            "questionId": market.question_id,
            "oracle": market.oracle,
            "collateralToken": market.collateral_token,
            "yesTokenId": market.yes_token_id,
            "noTokenId": market.no_token_id,
            "outcomeSlotCount": market.outcome_slot_count
        }
        return json.dumps(market_dict, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--condition-id", help="条件ID")
    parser.add_argument("--tx-hash", help="包含 ConditionPreparation 事件的交易哈希")
    parser.add_argument("--log-index", type=int, help="ConditionPreparation 事件的日志索引")
    parser.add_argument("--output", default=None, help="输出文件路径")
    parser.add_argument("--event-slug", help="事件短标识 (slug)")
    args = parser.parse_args()
    
    decoder = MarketDecoder()
    
    if args.event_slug:
        # 通过 Gamma API slug 获取事件信息
        market_info = decoder.get_event_by_slug(args.event_slug)
        
        # 从市场信息中提取 conditionId
        condition_id = market_info.get("conditionId")
        if not condition_id:
            raise ValueError(f"ConditionId not found in market {args.event_slug}")
        
        # 提取 oracle 和 questionId
        oracle = market_info.get("oracle", "0x157Ce2d672854c848c9b79C49a8Cc6cc89176a49")
        question_id = market_info.get("questionId", "0x0000000000000000000000000000000000000000000000000000000000000000")
        
        # 优先使用 Gamma API 返回的 clobTokenIds
        yes_token_id = None
        no_token_id = None
        
        if "clobTokenIds" in market_info and market_info["clobTokenIds"]:
            clob_token_ids = market_info["clobTokenIds"]
            
            # 确保 clob_token_ids 是一个有效的列表
            if isinstance(clob_token_ids, list) and len(clob_token_ids) >= 2:
                yes_token_id = clob_token_ids[0]
                no_token_id = clob_token_ids[1]
            elif isinstance(clob_token_ids, list) and len(clob_token_ids) == 1:
                yes_token_id = clob_token_ids[0]
                # 如果只有一个 TokenId，仍然计算 NO TokenId
                positions = derive_binary_positions(
                    oracle=oracle,
                    question_id=question_id,
                    condition_id=condition_id,
                    collateral_token=USDC_E_ADDRESS
                )
                no_token_id = positions.position_no
            else:
                # 如果不是有效的列表，使用计算的 TokenId
                print("Warning: clobTokenIds is not a valid list, will calculate TokenIds")
        
        # 如果没有 clobTokenIds，使用计算的 TokenId
        if not yes_token_id or not no_token_id:
            positions = derive_binary_positions(
                oracle=oracle,
                question_id=question_id,
                condition_id=condition_id,
                collateral_token=USDC_E_ADDRESS
            )
            if not yes_token_id:
                yes_token_id = positions.position_yes
            if not no_token_id:
                no_token_id = positions.position_no
        
        # 创建市场对象
        market = Market(
            condition_id=condition_id,
            question_id=question_id,
            oracle=oracle,
            collateral_token=USDC_E_ADDRESS,
            yes_token_id=yes_token_id,
            no_token_id=no_token_id
        )
        
        # 验证 TokenId 是否与 Gamma API 返回的一致
        if "clobTokenIds" in market_info and market_info["clobTokenIds"]:
            gamma_token_ids = market_info["clobTokenIds"]
            calculated_token_ids = [yes_token_id, no_token_id]
            
            # 检查是否有匹配的 TokenId
            match_found = False
            for gamma_id in gamma_token_ids:
                for calc_id in calculated_token_ids:
                    if str(gamma_id) == str(calc_id):
                        match_found = True
                        break
                if match_found:
                    break
            
            if not match_found:
                print("Warning: Token IDs do not match Gamma API token IDs")
                print(f"Gamma token IDs: {gamma_token_ids}")
                print(f"Used token IDs: {calculated_token_ids}")
    elif args.condition_id:
        # 根据 conditionId 解码
        market = decoder.decode_from_condition_id(args.condition_id)
    elif args.tx_hash and args.log_index:
        # 根据交易哈希和日志索引解码
        receipt = decoder.w3.eth.get_transaction_receipt(args.tx_hash)
        target_log = None
        for log in receipt["logs"]:
            if log["logIndex"] == args.log_index:
                target_log = log
                break
        
        if not target_log:
            raise ValueError(f"Log index {args.log_index} not found in transaction {args.tx_hash}")
        
        market = decoder.decode_from_log(target_log)
    else:
        parser.error("Either --event-slug, --condition-id, or both --tx-hash and --log-index must be provided")
    
    # 转换为 JSON
    market_json = decoder.to_json(market)
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(market_json)
        print(f"市场解析结果已保存到: {args.output}")
    else:
        print(market_json)
