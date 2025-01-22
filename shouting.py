import pyxel
import math
from random import randint, uniform

class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Player:
    def __init__(self):
        self.pos = Vec2(pyxel.width / 2, pyxel.height - 20)
        self.speed = 4
        self.bullets = []
        self.size = 8
        self.shoot_cooldown = 0
        self.power = 1 

    def update(self):
     
        if pyxel.btn(pyxel.KEY_LEFT) and self.pos.x > 0:
            self.pos.x -= self.speed
        if pyxel.btn(pyxel.KEY_RIGHT) and self.pos.x < pyxel.width:
            self.pos.x += self.speed
        if pyxel.btn(pyxel.KEY_UP) and self.pos.y > 0:
            self.pos.y -= self.speed
        if pyxel.btn(pyxel.KEY_DOWN) and self.pos.y < pyxel.height:
            self.pos.y += self.speed

 
        self.shoot_cooldown = max(0, self.shoot_cooldown - 1)
        if pyxel.btn(pyxel.KEY_Z) and self.shoot_cooldown == 0:
            if self.power == 1:
               
                self.bullets.append(Vec2(self.pos.x, self.pos.y - 10))
            elif self.power == 2:
               
                self.bullets.append(Vec2(self.pos.x - 5, self.pos.y - 10))
                self.bullets.append(Vec2(self.pos.x + 5, self.pos.y - 10))
            else:
            
                self.bullets.append(Vec2(self.pos.x, self.pos.y - 10))
                self.bullets.append(Vec2(self.pos.x - 8, self.pos.y - 8))
                self.bullets.append(Vec2(self.pos.x + 8, self.pos.y - 8))
            self.shoot_cooldown = 5

   
        for bullet in self.bullets[:]:
            bullet.y -= 6
            if bullet.y < 0:
                self.bullets.remove(bullet)

    def draw(self):
        
        pyxel.rect(self.pos.x - 4, self.pos.y - 4, 8, 8, 11)
        
      
        for bullet in self.bullets:
            pyxel.rect(bullet.x - 1, bullet.y - 4, 2, 8, 10)

class Enemy:
    def __init__(self, x, y):
        self.pos = Vec2(x, y)
        self.bullets = []
        self.shoot_timer = 0
        self.pattern = randint(0, 2)
        self.health = 10  
        self.alive = True
        self.size = 16    

    def update(self):
        if not self.alive:
            return

        self.shoot_timer += 1
        if self.shoot_timer >= 30:
            self.shoot()
            self.shoot_timer = 0

        
        for bullet in self.bullets[:]:
            bullet[0].x += bullet[1].x
            bullet[0].y += bullet[1].y
            if (bullet[0].y > pyxel.height or bullet[0].y < 0 or
                bullet[0].x > pyxel.width or bullet[0].x < 0):
                self.bullets.remove(bullet)

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.alive = False
            self.bullets.clear()  
            return True
        return False

    def shoot(self):
        if not self.alive:
            return

        if self.pattern == 0:  
            for angle in range(0, 360, 30):
                rad = math.radians(angle)
                velocity = Vec2(math.cos(rad) * 2, math.sin(rad) * 2)
                self.bullets.append([Vec2(self.pos.x, self.pos.y), velocity])
        elif self.pattern == 1: 
            for angle in range(-30, 31, 10):
                rad = math.radians(angle + 90)
                velocity = Vec2(math.cos(rad) * 2, math.sin(rad) * 2)
                self.bullets.append([Vec2(self.pos.x, self.pos.y), velocity])
        else: 
            for _ in range(5):
                angle = uniform(0, 360)
                rad = math.radians(angle)
                velocity = Vec2(math.cos(rad) * 2, math.sin(rad) * 2)
                self.bullets.append([Vec2(self.pos.x, self.pos.y), velocity])

    def draw(self):
        if not self.alive:
            return
            
     
        pyxel.rect(self.pos.x - 8, self.pos.y - 8, 16, 16, 8)
        
     
        hp_width = (self.health / 10) * 16
        pyxel.rect(self.pos.x - 8, self.pos.y - 12, hp_width, 2, 11)
        
        
        for bullet in self.bullets:
            pyxel.circ(bullet[0].x, bullet[0].y, 2, 14)

class App:
    def __init__(self):
        pyxel.init(160, 240, title="Shooting Game")
        self.game_state = "TITLE"  
        self.instruction_page = 0
        self.reset_game()
        pyxel.run(self.update, self.draw)

    def reset_game(self):
        self.player = Player()
        self.enemies = [Enemy(40, 40), Enemy(80, 40), Enemy(120, 40)]
        self.game_over = False
        self.score = 0
        self.power_items = []

    def check_collision(self):
       
        for enemy in self.enemies:
            if not enemy.alive: 
                continue
            for bullet in enemy.bullets:
                dx = self.player.pos.x - bullet[0].x
                dy = self.player.pos.y - bullet[0].y
                if math.sqrt(dx * dx + dy * dy) < self.player.size:
                    self.game_over = True


        for enemy in self.enemies:
            if not enemy.alive:
                continue
            for bullet in self.player.bullets[:]:
                dx = enemy.pos.x - bullet.x
                dy = enemy.pos.y - bullet.y
                if abs(dx) < enemy.size/2 and abs(dy) < enemy.size/2:
                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)
                    if enemy.take_damage(1):
                        self.score += 1000
                        if self.player.power < 3:
                            self.power_items.append(Vec2(enemy.pos.x, enemy.pos.y))

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        if self.game_state == "TITLE":
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.game_state = "INSTRUCTION"
        
        elif self.game_state == "INSTRUCTION":
            if pyxel.btnp(pyxel.KEY_SPACE):
                if self.instruction_page < 2:
                    self.instruction_page += 1
                else:
                    self.game_state = "PLAYING"
                    self.instruction_page = 0
        
        elif self.game_state == "PLAYING":
            if not self.game_over:
                self.player.update()
                for enemy in self.enemies:
                    enemy.update()
                self.check_collision()
                
         
                for item in self.power_items[:]:
                    item.y += 1
                    dx = self.player.pos.x - item.x
                    dy = self.player.pos.y - item.y
                    if math.sqrt(dx * dx + dy * dy) < 12:
                        self.player.power = min(self.player.power + 1, 3)
                        self.power_items.remove(item)
                    elif item.y > pyxel.height:
                        self.power_items.remove(item)
                
        
                if all(not enemy.alive for enemy in self.enemies):
                    self.game_state = "CLEAR"
            else:
                self.game_state = "GAME_OVER"
        
        elif self.game_state == "GAME_OVER":
            if pyxel.btnp(pyxel.KEY_R):
                self.reset_game()
                self.game_state = "PLAYING"
        
        elif self.game_state == "CLEAR":
            if pyxel.btnp(pyxel.KEY_R):
                self.reset_game()
                self.game_state = "PLAYING"

    def draw(self):
        pyxel.cls(0)

        if self.game_state == "TITLE":
            self.draw_title()
        elif self.game_state == "INSTRUCTION":
            self.draw_instruction()
        elif self.game_state == "PLAYING":
            self.draw_game()
        elif self.game_state == "GAME_OVER":
            self.draw_game()
            self.draw_game_over()
        elif self.game_state == "CLEAR":
            self.draw_game()
            self.draw_clear()

    def draw_title(self):
     
        pyxel.text(45, 80, "DANMAKU SHOOTER", pyxel.frame_count % 16)
        pyxel.text(35, 140, "PRESS SPACE TO START", 7)
        

        t = pyxel.frame_count
        for i in range(8):
            angle = t + i * 45
            x = 80 + math.cos(math.radians(angle)) * 30
            y = 100 + math.sin(math.radians(angle)) * 30
            pyxel.circ(x, y, 2, 8 + (i % 7))

    def draw_instruction(self):
        if self.instruction_page == 0:
            pyxel.text(50, 30, "HOW TO PLAY", 7)
            pyxel.text(20, 60, "MOVE: ARROW KEYS", 7)
            pyxel.text(20, 80, "SHOOT: Z KEY", 7)
            pyxel.text(20, 100, "QUIT: Q KEY", 7)
            pyxel.text(20, 120, "RESTART: R KEY", 7)
            
        elif self.instruction_page == 1:
            pyxel.text(50, 30, "POWER UPS", 7)
            pyxel.text(20, 60, "DEFEAT ENEMIES TO", 7)
            pyxel.text(20, 80, "GET POWER UPS!", 7)
            pyxel.text(20, 100, "MAX POWER LEVEL: 3", 7)
            pyxel.text(20, 120, "MORE BULLETS = MORE FUN!", 7)
            
        elif self.instruction_page == 2:
            pyxel.text(50, 30, "OBJECTIVES", 7)
            pyxel.text(20, 60, "DEFEAT ALL ENEMIES", 7)
            pyxel.text(20, 80, "AVOID ENEMY BULLETS", 7)
            pyxel.text(20, 100, "GET HIGH SCORE!", 7)
            pyxel.text(20, 120, "GOOD LUCK!", 7)

        pyxel.text(20, 200, f"PAGE {self.instruction_page + 1}/3", 7)
        pyxel.text(20, 220, "PRESS SPACE TO CONTINUE", 7)

    def draw_game(self):
        self.player.draw()
        for enemy in self.enemies:
            enemy.draw()
        for item in self.power_items:
            pyxel.circ(item.x, item.y, 4, 9)
        

        pyxel.text(5, 5, f"SCORE: {self.score}", 7)
        pyxel.text(5, 15, f"POWER: {self.player.power}", 7)
        

        enemies_left = sum(1 for enemy in self.enemies if enemy.alive)
        pyxel.text(5, 25, f"ENEMIES: {enemies_left}", 7)

    def draw_game_over(self):
        pyxel.text(60, 120, "GAME OVER", pyxel.frame_count % 16)
        pyxel.text(45, 130, "PRESS R TO RESTART", pyxel.frame_count % 16)
        pyxel.text(45, 140, "FINAL SCORE: " + str(self.score), 7)

    def draw_clear(self):
      
        color = (pyxel.frame_count // 4) % 15 + 1
        
   
        pyxel.text(60, 100, "STAGE CLEAR!", color)
        pyxel.text(45, 120, f"FINAL SCORE: {self.score}", 7)
  
        t = pyxel.frame_count
        for i in range(8):
            angle = t + i * 45
            radius = 20 + math.sin(t * 0.1) * 10
            x = 80 + math.cos(math.radians(angle)) * radius
            y = 80 + math.sin(math.radians(angle)) * radius
            pyxel.circ(x, y, 2, (i + t) % 15 + 1)

        if (pyxel.frame_count // 30) % 2 == 0:
            pyxel.text(35, 140, "PRESS R TO PLAY AGAIN", 7)

App()
