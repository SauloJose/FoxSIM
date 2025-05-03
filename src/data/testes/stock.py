                isInside, _ = field.RectUtil.check_point_inside(point)
                if isInside:
                    ball.x, ball.y = screen_to_virtual([x, y]) 
                    ball.collision_object.x = ball.x
                    ball.collision_object.y = ball.y
                    ball.velocity = np.array([0,0],dtype=float)


                #Verifica se cliquei em algum dos robôs e puxo o ponteiro do robô selecionado
                bots = blue_team.robots + red_team.robots
                for bot in bots:
                    if bot.collision_object.check_point_inside(point):
                        # Se o jogo estiver pausado, mova o robô
                        if is_game_paused:
                            bot.x, bot.y = screen_to_virtual([x, y])
                            bot.collision_object.x = bot.x
                            bot.collision_object.y = bot.y
                            bot.velocity = np.array([0,0],dtype=float)