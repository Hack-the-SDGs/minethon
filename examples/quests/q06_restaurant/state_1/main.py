from minethon import EventAdaptor, create_bot

seen = []  # 記錄已處理過的廣播訊息，避免重複觸發

class Stage1Handler(EventAdaptor):
    def on_messagestr(self, message, *_):
        msg_str = str(message)
        print(msg_str)

        if "請幫我找零" not in msg_str:
            return

        if msg_str in seen:
            return
        seen.append(msg_str)

        # 使用字串切割提取金額
        raw_num = msg_str.split("請幫我找零")[1].split("元")[0].strip()
        target_money = int(raw_num)
        print("目標金額：", target_money, "元")

        # 計算最少硬幣組合
        gold = target_money // 50
        target_money %= 50

        iron = target_money // 10
        target_money %= 10

        copper = target_money // 5
        target_money %= 5

        nugget = target_money
        # 執行硬幣丟棄
        if gold != 0:
            print("丟出",gold, "個 金錠")
            bot.drop("gold_ingot", gold)
        if iron != 0:
            print("丟出",iron, "個 鐵錠")
            bot.drop("iron_ingot", iron)
        if copper != 0:
            print("丟出", copper, "個 銅錠")
            bot.drop("copper_ingot", copper)
        if nugget != 0:
            print("丟出", nugget, "個 鐵粒")
            bot.drop("iron_nugget", nugget)


bot = create_bot("g_restaurant")
bot.bind(Stage1Handler())
bot.run_forever()
