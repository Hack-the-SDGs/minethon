from minethon import create_bot

bot = create_bot("g_dance")
queue = []
flag = True

while True:
    if bot.get_block(39, 63, -403) == "glass":
        if bot.get_block_property(40,66,-406,"lit") and flag:
            flag = False
            queue.append(1)
        elif bot.get_block_property(38,66,-406,"lit") and flag:
            flag = False
            queue.append(2)
        elif bot.get_block_property(36,66,-406,"lit") and flag:
            flag = False
            queue.append(3)
        elif bot.get_block_property(42,66,-406,"lit") and flag:
            flag = False
            queue.append(4)
        if bot.get_block_property(40,66,-406,"lit") == 0 and bot.get_block_property(38,66,-406,"lit") == 0 and bot.get_block_property(36,66,-406,"lit") == 0 and bot.get_block_property(42,66,-406,"lit") == 0:
            flag = True
            
    else:
        for step in queue:    
            if step == 1:
                bot.move_forward()
                bot.move_backward()
            elif step == 2:
                bot.move_backward()
                bot.move_forward()
            elif step == 3:
                bot.move_left()
                bot.move_right()
            elif step == 4:
                bot.move_right()
                bot.move_left()
        queue.clear()