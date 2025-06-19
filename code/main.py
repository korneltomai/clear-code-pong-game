from settings import * 
from sprites import *
from groups import AllSprites
from random import randint
import json

class Game():
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pong")
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = True

        # groups
        self.all_sprites = AllSprites()
        self.paddle_sprites = pygame.sprite.Group()
        self.ball_sprites = pygame.sprite.Group()
        self.powerup_sprites = pygame.sprite.Group()

        # sprites
        self.player = Player((self.all_sprites, self.paddle_sprites))
        Ball((self.all_sprites, self.ball_sprites), self.paddle_sprites, self.update_score)
        self.opponent = Opponent((self.all_sprites, self.paddle_sprites), self.ball_sprites)

        # score
        try:
            with open(join("data", "score.txt")) as score_file:
                self.score = json.load(score_file)
        except:
            self.score = {"player": 0, "opponent": 0}
        self.font = pygame.font.Font(None, 160)
        self.pause_font = pygame.font.Font(None, 60)

        # powerups
        self.spawn_power_up_event = pygame.event.custom_type()

    def run(self):
        # main game loop
        while self.running:
            delta_time = self.clock.tick(60) /  1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    with open(join("data", "score.txt"), "w") as score_file:
                        json.dump(self.score, score_file)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_game()
                if event.type == self.spawn_power_up_event:
                    self.spawn_powerup()

                if self.paused:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                            self.paused = False
                            self.ball_sprites.sprites()[0].create_time = pygame.time.get_ticks()
                            pygame.time.set_timer(self.spawn_power_up_event, 15000)

            # update only when the game is not paused
            if not self.paused:
                self.all_sprites.update(delta_time)

            # draw
            self.display_surface.fill(COLORS["bg"])
            self.display_score()
            self.all_sprites.draw()

            if self.paused:
                pause_text_surf = self.pause_font.render("Press 'space' or 'return' to start the game!", True, "red")
                pause_text_rect = pause_text_surf.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
                self.display_surface.blit(pause_text_surf, pause_text_rect)

            pygame.display.update()

        pygame.quit()

    def display_score(self):
        player_score_surf = self.font.render(str(self.score["player"]), True, COLORS["bg detail"])
        player_score_rect = player_score_surf.get_frect(center = (WINDOW_WIDTH / 2 + 100, WINDOW_HEIGHT / 2))
        self.display_surface.blit(player_score_surf, player_score_rect)

        opponent_score_surf = self.font.render(str(self.score["opponent"]), True, COLORS["bg detail"])
        opponent_score_rect = opponent_score_surf.get_frect(center = (WINDOW_WIDTH / 2 - 100, WINDOW_HEIGHT / 2))
        self.display_surface.blit(opponent_score_surf, opponent_score_rect)

        pygame.draw.line(self.display_surface, COLORS["bg detail"], (WINDOW_WIDTH / 2, 0), (WINDOW_WIDTH / 2, WINDOW_HEIGHT), 6)

    def update_score(self, side):
        self.score["player" if side == "player" else "opponent"] += 1

        for paddle in self.paddle_sprites:
            paddle.reset()

        for ball in self.ball_sprites:
            ball.kill()
        new_ball = Ball((self.all_sprites, self.ball_sprites), self.paddle_sprites, self.update_score)
        new_ball.reset_time = pygame.time.get_ticks()

    def reset_game(self):
        self.paused = True
        self.spawn_power_up_event = pygame.event.custom_type()
        self.score = {"player": 0, "opponent": 0}
        with open(join("data", "score.txt"), "w") as score_file:
            json.dump(self.score, score_file)

        for paddle in self.paddle_sprites:
            paddle.reset()

        for ball in self.ball_sprites:
            ball.kill()
        Ball((self.all_sprites, self.ball_sprites), self.paddle_sprites, self.update_score)
        self.spawn_power_up_event = pygame.event.custom_type()

        for powerup in self.powerup_sprites:
            powerup.kill()

    def spawn_powerup(self):
        random_powerup = randint(0, 2)
        random_pos = (randint(400, WINDOW_WIDTH - 400), randint(50, WINDOW_HEIGHT - 50))
        if random_powerup == 0:
            SpeedPowerUp((self.all_sprites, self.powerup_sprites), self.ball_sprites, random_pos)
        elif random_powerup == 1:
            BallPowerUp((self.all_sprites, self.powerup_sprites), self.ball_sprites, random_pos, (self.all_sprites, self.ball_sprites), self.paddle_sprites, self.update_score)
        elif random_powerup == 2:
            PedalPowerUp((self.all_sprites, self.powerup_sprites), self.ball_sprites, random_pos, self.player, self.opponent)

if __name__ == "__main__":
    game = Game()
    game.run()