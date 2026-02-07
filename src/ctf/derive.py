from web3 import Web3

class Positions:
    """头寸数据类"""
    def __init__(self, yes, no):
        self.position_yes = yes
        self.position_no = no

def derive_binary_positions(oracle, question_id, condition_id, collateral_token):
    """计算二元市场的YES/NO TokenId
    
    Args:
        oracle: 预言机地址
        question_id: 问题ID
        condition_id: 条件ID
        collateral_token: 抵押品代币地址
        
    Returns:
        Positions对象，包含yesTokenId和noTokenId
    """
    # 计算YES和NO的collectionId
    parent_collection_id = b'\x00' * 32  # 更简单的方式表示全零字节
    
    # 确保 condition_id 是字节
    if isinstance(condition_id, str) and condition_id.startswith('0x'):
        condition_id_bytes = bytes.fromhex(condition_id[2:])
    else:
        condition_id_bytes = condition_id
    
    # 对于YES，indexSet为1 (0b01)
    index_set_yes = b'\x00' * 31 + b'\x01'  # 32字节，最后一个字节为1
    collection_id_yes = Web3.keccak(
        parent_collection_id + 
        condition_id_bytes + 
        index_set_yes
    )
    
    # 对于NO，indexSet为2 (0b10)
    index_set_no = b'\x00' * 31 + b'\x02'  # 32字节，最后一个字节为2
    collection_id_no = Web3.keccak(
        parent_collection_id + 
        condition_id_bytes + 
        index_set_no
    )
    
    # 确保 collateral_token 是字节
    if isinstance(collateral_token, str) and collateral_token.startswith('0x'):
        collateral_token_bytes = bytes.fromhex(collateral_token[2:])
    else:
        collateral_token_bytes = collateral_token
    
    # 计算TokenId
    yes_token_id = Web3.keccak(
        collateral_token_bytes + 
        collection_id_yes
    )
    
    no_token_id = Web3.keccak(
        collateral_token_bytes + 
        collection_id_no
    )
    
    # 返回整数形式的TokenId（与Gamma API一致）
    return Positions(str(int.from_bytes(yes_token_id, 'big')), str(int.from_bytes(no_token_id, 'big')))
