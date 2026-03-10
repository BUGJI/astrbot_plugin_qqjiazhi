import re
from typing import Optional

from astrbot.api.event import filter, AstrMessageEvent
import astrbot.api.message_components as Comp
from astrbot.api.star import Context, Star, register
from astrbot.api import AstrBotConfig
from astrbot.api import logger


@register("qqjiazhi", "BUGJI", "一键估算QQ号价值", "1.0.0")
class QQJiaZhiPlugin(Star):
    """QQ号价值估算插件"""
    
    # QQ号正则表达式（5-12位数字）
    QQ_PATTERN = re.compile(r'^\d{5,12}$')
    
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.bot_qq = str(config.get("bot_qq", ""))
        # self.source = config.get("source", ["保留参数，后续升级用"])
        
    async def initialize(self) -> None:
        """插件初始化方法，实例化后自动调用"""
        # 验证bot_qq配置
        if self.bot_qq and not self._is_valid_qq(self.bot_qq):
            self.bot_qq = ""  # 清空无效配置
            logger.warning("bot_qq配置无效，请设置为有效的QQ号")
    
    @filter.command("QQ估价")
    async def estimate_qq_value(self, event: AstrMessageEvent, qq: str = None) -> None:
        """一键估算QQ号价值，拼接@或者QQ号可估对方QQ号价格"""
        
        # 1. 验证bot_qq配置
        if not self.bot_qq:
            yield event.plain_result(" 请先配置bot_qq")
            return
        
        #  转换成合法类型
        if qq is not None:
            qq = str(qq)
        
        # 2. 获取待估价的QQ号
        target_qq = await self._extract_target_qq(event, qq)
        if not target_qq:
            yield event.plain_result(" 无法获取有效的QQ号，请通过@、直接输入或回复消息指定QQ号")
            return
        
        # 3. 验证QQ号格式
        if not self._is_valid_qq(target_qq):
            yield event.plain_result(f" '{target_qq}' 不是有效的QQ号（应为5-12位数字）")
            return
        
        # 4. 构建图片URL路径
        url_path = self._build_url_path(target_qq)
        if not url_path:
            yield event.plain_result(" QQ号处理失败")
            return
        
        # 5. 返回结果
        chain = [
            Comp.Plain(" QQ账号估算结果："),
            Comp.Image.fromURL(f"https://c.bmcx.com/temp/qqjiazhi{url_path}.jpg?v=2"),
            Comp.Plain("注：结果仅供参考，来源 qqjiazhi.bmcx.com")
        ]
        yield event.chain_result(chain)
    
    def _extract_at_qq(self, event: AstrMessageEvent) -> Optional[str]:
        """
        从消息中提取被@的QQ号（排除作为命令前缀的机器人自己）
        
        处理逻辑：
        1. 如果消息第一项是@机器人，则将其视为命令前缀并跳过
        2. 返回后续第一个非机器人@的QQ号
        
        Args:
            event: 消息事件对象
            
        Returns:
            Optional[str]: 被@的其他QQ号，没有则返回None
        """
        message_chain = event.message_obj.message
        if not isinstance(message_chain, list) or len(message_chain) == 0:
            return None
        
        start_index = 0
        
        # 检查第一项是否为@机器人（命令前缀）
        first_comp = message_chain[0]
        if isinstance(first_comp, Comp.At) and str(first_comp.qq) == self.bot_qq:
            start_index = 1  # 跳过作为命令前缀的@机器人
        
        # 从剩余消息中查找第一个@
        for component in message_chain[start_index:]:
            if isinstance(component, Comp.At) and str(component.qq):
                return str(component.qq)
        
        return None
    
    async def _extract_target_qq(self, event: AstrMessageEvent, input_qq: Optional[str]) -> Optional[str]:
        """从多种来源提取目标QQ号"""
        # 1. 从@提及中提取（已处理命令前缀情况）
        at_qq = self._extract_at_qq(event)
        if at_qq:
            return at_qq
        
        # 2. 从命令参数中提取
        if input_qq and input_qq.strip():
            return input_qq.strip()
        
        # 3. 从发送者ID提取
        return event.get_sender_id()
    
    def _is_valid_qq(self, qq: str) -> bool:
        """
        验证QQ号是否有效
        
        Args:
            qq: 待验证的QQ号
            
        Returns:
            bool: 是否为有效QQ号
        """
        if not qq or not isinstance(qq, str):
            return False
        
        qq = qq.strip()
        return bool(self.QQ_PATTERN.match(qq))
    
    def _build_url_path(self, qq: str) -> str:
        """
        构建URL路径（每3位一组用/分隔）
        
        Args:
            qq: 已验证的QQ号
            
        Returns:
            str: URL路径部分，以'/'开头
        """
        groups = [qq[i:i+3] for i in range(0, len(qq), 3)]
        return '/' + '/'.join(groups)
    
    async def terminate(self) -> None:
        """插件销毁方法，卸载/停用时调用"""
        logger.info("QQ估价插件已卸载")
