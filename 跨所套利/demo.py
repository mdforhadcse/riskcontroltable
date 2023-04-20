# for testing purpose
from notify import notifier
from notify import Platform


def lab001():
    filepath = "notify/notify.toml"
    notifier.set_platforms_with_file(filepath)

    # notifier.notify("策略提醒：", "非交易日，不抓取数据，程序退出", Platform.Lark)
    # notifier.notify("策略提醒：", "非交易日，不抓取数据，程序退出", "weixin")
    # notifier.notify("策略提醒：", "非交易日，不抓取数据，程序退出", Platform.Weixin)
    # notifier.notify("策略提醒：", "非交易日，不抓取数据，程序退出", "dingtalk")
    # notifier.notify("策略提醒：", "非交易日，不抓取数据，程序退出", "telegram")
    # notifier.notify("策略提醒：", "非交易日，不抓取数据，程序退出", Platform.Discord)
    # notifier.notify("策略提醒：", "非交易日，不抓取数据，程序退出", Platform.Bark)
    notifier.notify("持仓表", "持仓数据表", file_path='2022-06-28-RiskControlTable.xlsx', platform=Platform.Mail)

    # notifier.lark("策略提醒：", "非交易日，不抓取数据，程序退出",
    #               "https://open.larksuite.com/open-apis/bot/v2/hook/xxx")


def run():
    lab001()
    pass


if __name__ == '__main__':
    run()
