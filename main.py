from astrbot.api.event import filter, AstrMessageEvent
import astrbot.api.message_components as Comp
from astrbot.api.star import Context, Star, register
from astrbot.api import AstrBotConfig
@register("qqjiazhi", "BUGJI", "一键估算QQ号价值", "1.0.0")
class qqjiazhi(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.bot_qq = config.get("bot_qq", "请先配置bot_qq")
    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
    @filter.command("QQ估价")
    async def QQ估价(self, event: AstrMessageEvent, qq: str = None):
        """估量QQ号的价值"""
        result = "初始化"
        if self.bot_qq == "请先配置bot_qq":
            yield event.plain_result("请先配置bot_qq")
            return
        bot_qq = self.bot_qq # or await event.get_bot_qq()
        message_chain = event.message_obj.message
        at_qq = next((c.qq for c in reversed(message_chain) if isinstance(c, Comp.At) and str(c.qq) != str(bot_qq)), None)
        user_id = (str(at_qq or qq or "")).strip() or event.get_sender_id()
        temp = str(user_id).replace('/', '').replace(' ', '')
        if len(temp) <= 3: result = '/' + temp
        result = '/' + '/'.join([temp[i:i+3] for i in range(0, len(temp), 3)])
        chain = [
            Comp.Plain(" 你的QQ账号估算结果："),
            Comp.Image.fromURL("https://c.bmcx.com/temp/qqjiazhi"+result+".jpg?v=2"), # 从 URL 发送图片
            Comp.Plain("注：结果仅供参考，来源 qqjiazhi.bmcx.com")
        ]
        yield event.chain_result(chain)
    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
