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

        # 初始化 dp 格子分別為：總幣數、金粒、鐵錠、銅粒、鐵粒
        dp = []
        for i in range(target_money+1):
            dp.append([257, 0, 0, 0, 0])
        dp[0] = [0, 0, 0, 0, 0]

        # 計算最少零錢數
        for i in range(1, target_money + 1):
            for val in [46, 10, 7, 1]:
                if val <= i and dp[i - val][0] + 1 < dp[i][0]:
                    dp[i] = dp[i - val].copy()
                    dp[i][0] += 1
                    if val == 46:
                        dp[i][1] += 1
                    elif val == 10:
                        dp[i][2] += 1
                    elif val == 7:
                        dp[i][3] += 1
                    else:
                        dp[i][4] += 1

        # 執行硬幣丟棄
        if dp[target_money][0] != 257:
            if dp[target_money][1] != 0:
                print("丟出",dp[target_money][1], "個 金粒")
                bot.drop("gold_nugget", dp[target_money][1])
            if dp[target_money][2] != 0:
                print("丟出",dp[target_money][2], "個 鐵錠")
                bot.drop("iron_ingot", dp[target_money][2])
            if dp[target_money][3] != 0:
                print("丟出", dp[target_money][3], "個 銅粒")
                bot.drop("raw_copper", dp[target_money][3])
            if dp[target_money][4] != 0:
                print("丟出", dp[target_money][4], "個 鐵粒")
                bot.drop("iron_nugget", dp[target_money][4])
bot = create_bot("g_restaurant")
bot.bind(Stage1Handler())
bot.run_forever()
