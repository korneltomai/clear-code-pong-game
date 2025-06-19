from settings import * 
from random import choice, uniform

class Paddle(pygame.sprite.Sprite):
    def __init__(self, groups, position = (0, 0), speed = 0):
        super().__init__(groups)
        self.image = pygame.Surface(SIZE["paddle"], pygame.SRCALPHA)
        pygame.draw.rect(self.image, COLORS["paddle"], pygame.FRect((0, 0), (SIZE["paddle"])), 0, 5)
        self.rect = self.image.get_frect(center = position)
        self.old_rect = self.rect.copy()
        
        self.shadow_surface = self.image.copy()
        pygame.draw.rect(self.shadow_surface, COLORS["paddle shadow"], pygame.FRect((0, 0), (SIZE["paddle"])), 0, 5)

        self.speed = speed
        self.direction = 0

        self.grown = False
        self.grow_time = 0

    def update(self, delta_time):
        self.old_rect = self.rect.copy()
        self.get_direction()
        self.move(delta_time)
        self.grow_timer()

    def move(self, delta_time):
        self.rect.centery += self.direction * self.speed * delta_time 

        self.rect.top = 0 if self.rect.top < 0 else self.rect.top
        self.rect.bottom = WINDOW_HEIGHT if self.rect.bottom > WINDOW_HEIGHT else self.rect.bottom

    def grow(self):
        if not self.grown:
            self.image = pygame.transform.smoothscale_by(self.image, (1, 1.5))
            self.rect = self.image.get_frect(center = self.rect.center)
            self.shadow_surface = self.image.copy()
            pygame.draw.rect(self.shadow_surface, COLORS["paddle shadow"], pygame.FRect((0, 0), self.rect.size), 0, 5)
            self.grow_time = pygame.time.get_ticks()
            self.grown = True

    def grow_timer(self):
        if self.grown:
            currentTime = pygame.time.get_ticks()
            if currentTime - self.grow_time > 10000:
                self.image = pygame.transform.smoothscale_by(self.image, (1, 2/3))
                self.rect = self.image.get_frect(center = self.rect.center)
                self.shadow_surface = self.image.copy()
                pygame.draw.rect(self.shadow_surface, COLORS["paddle shadow"], pygame.FRect((0, 0), self.rect.size), 0, 5)
                self.grown = False

    def reset(self, pos):
        self.rect.center = pos
        if self.grown:
            self.image = pygame.transform.smoothscale_by(self.image, (1, 2/3))
            self.rect = self.image.get_frect(center = self.rect.center)
            self.shadow_surface = self.image.copy()
            pygame.draw.rect(self.shadow_surface, COLORS["paddle shadow"], pygame.FRect((0, 0), self.rect.size), 0, 5)
            self.grown = False

    def get_direction():
        pass

class Player(Paddle):
    def __init__(self, groups):
        super().__init__(groups, POS["player"], SPEED["player"])
        
    def get_direction(self):
        keys = pygame.key.get_pressed()
        self.direction = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w])

    def reset(self):
        super().reset(POS["player"])

class Opponent(Paddle):
    def __init__(self, groups, ball_sprites):
        super().__init__(groups, POS["opponent"], SPEED["opponent"])
        self.ball_sprites = ball_sprites
        self.closest_ball_pos = self.ball_sprites.sprites()[0].rect.center

    def move(self, delta_time):
        ball_distance_speed_multiplier = max(0.4, min(1, (abs(self.closest_ball_pos[1] - self.rect.centery) / 50 if abs(self.closest_ball_pos[1] - self.rect.centery) else 1))) 
        self.rect.centery += self.direction * self.speed * delta_time * ball_distance_speed_multiplier

        self.rect.top = 0 if self.rect.top < 0 else self.rect.top
        self.rect.bottom = WINDOW_HEIGHT if self.rect.bottom > WINDOW_HEIGHT else self.rect.bottom

    def get_direction(self):
        self.closest_ball_pos = self.ball_sprites.sprites()[0].rect.center
        for ball in self.ball_sprites:
            if abs(ball.rect.centerx - self.rect.centerx) < abs(self.closest_ball_pos[0] - self.rect.centerx):
                self.closest_ball_pos = ball.rect.center

        if self.rect.centery == self.closest_ball_pos[1]:
            self.direction = 0
        elif self.rect.centery < self.closest_ball_pos[1]:
            self.direction = 1
        else:
            self.direction = -1

    def reset(self):
        super().reset(POS["opponent"])

class Ball(pygame.sprite.Sprite):
    def __init__(self, groups, paddle_sprites, update_score, pos = POS["ball"]):
        super().__init__(groups)
        self.image = pygame.Surface(SIZE["ball"], pygame.SRCALPHA)
        pygame.draw.circle(self.image, COLORS["ball"], (SIZE["ball"][0] / 2, SIZE["ball"][1] / 2), SIZE["ball"][0] / 2)
        self.rect = self.image.get_frect(center = pos)
        self.old_rect = self.rect.copy()

        self.shadow_surface = self.image.copy()
        pygame.draw.circle(self.shadow_surface, COLORS["ball shadow"], (SIZE["ball"][0] / 2, SIZE["ball"][1] / 2), SIZE["ball"][0] / 2)

        self.paddle_sprites = paddle_sprites
        self.update_score = update_score

        # reset
        self.create_time = pygame.time.get_ticks()
        self.can_move = False

        # movement
        self.speed = SPEED["ball"]
        self.direction = pygame.Vector2(choice((-1, 1)), uniform(0.7, 0.8) * choice((-1, 1)))
        self.speed_up_event = pygame.event.custom_type()
        pygame.time.set_timer(self.speed_up_event, 200)

    def update(self, delta_time):
        if self.can_move:
            self.old_rect = self.rect.copy()
            self.move(delta_time)
            self.wall_collision()
        else:
            self.move_timer()

    def move(self, delta_time):
            self.rect.x += self.direction.x * self.speed * delta_time 
            self.collision(True)
            self.rect.y += self.direction.y * self.speed * delta_time 
            self.collision(False)

            self.speed_up()

    def wall_collision(self):
        if self.rect.top < 0:
            self.rect.top = 0
            self.direction.y *= -1

        elif self.rect.bottom > WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT
            self.direction.y *= -1 

        if self.rect.left < 20 or self.rect.right > WINDOW_WIDTH - 20:
            self.update_score("player" if self.rect.x < WINDOW_WIDTH / 2 else "opponent")

    def move_timer(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.create_time >= 2000:
            self.can_move = True

    def collision(self, moving_horizontal):
        for sprite in self.paddle_sprites:
            if sprite.rect.colliderect(self.rect):
                if moving_horizontal:
                    if self.rect.right > sprite.rect.left and self.old_rect.right <= sprite.old_rect.left:
                        self.rect.right = sprite.rect.left
                    if self.rect.left < sprite.rect.right and self.old_rect.left >= sprite.old_rect.right:
                        self.rect.left = sprite.rect.right
                    self.direction.x *= -1
                else:
                    if self.rect.bottom > sprite.rect.top and self.old_rect.bottom <= sprite.old_rect.top:
                        self.rect.bottom = sprite.rect.top
                    if self.rect.top < sprite.rect.bottom and self.old_rect.top >= sprite.old_rect.bottom:
                        self.rect.top = sprite.rect.bottom
                    self.direction.y *= -1

    def speed_up(self):
        for event in pygame.event.get():
            if event.type == self.speed_up_event:
                self.speed += 5

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, groups, ball_sprites, pos, color, shadow_color):
        super().__init__(groups)
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.aacircle(self.image, color, (10, 10), 10)
        self.rect = self.image.get_frect(center = pos)
        self.position = pos
        self.ball_sprites = ball_sprites

        self.shadow_surface = self.image.copy()
        pygame.draw.aacircle(self.shadow_surface, shadow_color, (10, 10), 10)

    def update(self, _):
        self.check_collision()

    def check_collision(self):
        for ball in self.ball_sprites:
            if ball.rect.colliderect(self.rect):
                self.active(ball)
                self.kill()
    
    def active(self, ball):
        pass

class SpeedPowerUp(PowerUp):
    def __init__(self, groups, ball_sprites, pos):
        super().__init__(groups, ball_sprites, pos, "red", "darkred")

    def active(self, ball):
        ball.speed += 50

class BallPowerUp(PowerUp):
    def __init__(self, groups, ball_sprites, pos, ball_groups, paddle_sprites, update_score):
        super().__init__(groups, ball_sprites, pos, "green", "darkgreen")
        self.ball_groups = ball_groups
        self.paddle_sprites = paddle_sprites
        self.update_score = update_score

    def active(self, ball):
        new_ball = Ball(self.ball_groups, self.paddle_sprites, self.update_score, self.rect.center)
        new_ball.can_move = True

        new_ball.direction.x = ball.direction.x

class PedalPowerUp(PowerUp):
    def __init__(self, groups, ball_sprites, pos, player, opponent):
        super().__init__(groups, ball_sprites, pos, "blue", "darkblue")
        self.player = player
        self.opponent = opponent

    def active(self, ball):
        self.opponent.grow() if ball.direction.x > 0 else self.player.grow()