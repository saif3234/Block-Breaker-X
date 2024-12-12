import pygame
import sys
import time
from settings import *
from sprites import Player, Ball, Block, Upgrade, Projectile
from surfacemaker import SurfaceMaker
from random import choice, randint

class Game:
    def __init__(self):
        # Initialize the game environment
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Block Breaker X - Game')

        # Load background and prepare sprites
        self.bg = self.create_bg()
        self.all_sprites = pygame.sprite.Group()
        self.block_sprites = pygame.sprite.Group()
        self.upgrade_sprites = pygame.sprite.Group()
        self.projectile_sprites = pygame.sprite.Group()

        # Setup core game components
        self.surfacemaker = SurfaceMaker()
        self.player = Player(self.all_sprites, self.surfacemaker)
        self.stage_setup()
        self.ball = Ball(self.all_sprites, self.player, self.block_sprites)

        # Heart and projectile graphics
        self.heart_surf = pygame.image.load('../graphics/other/redhearts.png').convert_alpha()
        self.projectile_surf = pygame.image.load('../graphics/other/orangeprojectile.png').convert_alpha()

        # Shooting control
        self.can_shoot = True
        self.shoot_time = 0



        # Sound effects
        self.laser_sound = self.setup_sound('../sounds/thelaser.wav', 0.1)
        self.powerup_sound = self.setup_sound('../sounds/thepowerups.wav', 0.1)
        self.laserhit_sound = self.setup_sound('../sounds/thelaserhits.wav', 0.02)
        self.music = self.setup_sound('../sounds/thebackgroundmusic.wav', 0.1, play=True, loop=True)

    def setup_sound(self, path, volume, play=False, loop=False):
        # Utility to load and configure sound effects
        sound = pygame.mixer.Sound(path)
        sound.set_volume(volume)
        if play:
            sound.play(loops=-1 if loop else 0)
        return sound

    def create_upgrade(self, position):
        # Generate an upgrade at the given position
        upgrade_type = choice(UPGRADES)
        Upgrade(position, upgrade_type, [self.all_sprites, self.upgrade_sprites])

    def create_bg(self):
        # Load and scale the background image dynamically
        bg_image = pygame.image.load('../graphics/other/mainbackground.png').convert()
        scale_factor = WINDOW_HEIGHT / bg_image.get_height()
        new_width = int(bg_image.get_width() * scale_factor)
        new_height = int(bg_image.get_height() * scale_factor)
        return pygame.transform.scale(bg_image, (new_width, new_height))

    def stage_setup(self):
        # Populate the game stage using the block map
        for row_index, row in enumerate(BLOCK_MAP):
            for col_index, cell in enumerate(row):
                if cell != ' ':
                    x_pos = col_index * (BLOCK_WIDTH + GAP_SIZE) + GAP_SIZE // 2
                    y_pos = TOP_OFFSET + row_index * (BLOCK_HEIGHT + GAP_SIZE) + GAP_SIZE // 2
                    Block(cell, (x_pos, y_pos), [self.all_sprites, self.block_sprites], self.surfacemaker, self.create_upgrade)

    def display_hearts(self):
        # Render the player's remaining hearts on the screen
        for i in range(self.player.hearts):
            x_pos = 2 + i * (self.heart_surf.get_width() + 2)
            self.display_surface.blit(self.heart_surf, (x_pos, 4))

    def upgrade_collision(self):
        # Detect and handle collisions between the player and upgrades
        collided_upgrades = pygame.sprite.spritecollide(self.player, self.upgrade_sprites, True)
        for upgrade in collided_upgrades:
            self.player.upgrade(upgrade.upgrade_type)
            self.powerup_sound.play()

    def create_projectile(self):
        # Create projectiles and play sound
        self.laser_sound.play()
        for laser_rect in self.player.laser_rects:
            Projectile(
                laser_rect.midtop - pygame.math.Vector2(0, 30),
                self.projectile_surf,
                [self.all_sprites, self.projectile_sprites]
            )

    def laser_timer(self):
        # Manage the shooting cooldown
        if pygame.time.get_ticks() - self.shoot_time >= 500:
            self.can_shoot = True

    def projectile_block_collision(self):
        # Detect collisions between projectiles and blocks
        for projectile in self.projectile_sprites:
            hit_blocks = pygame.sprite.spritecollide(projectile, self.block_sprites, False)
            if hit_blocks:
                for block in hit_blocks:
                    block.get_damage(1)
                projectile.kill()
                self.laserhit_sound.play()

    def run(self):
        # Main game loop
        last_time = time.time()
        while True:
            dt = time.time() - last_time  # Delta time calculation
            last_time = time.time()

            # Handle user input and events
            for event in pygame.event.get():
                if event.type == pygame.QUIT or self.player.hearts <= 0:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.ball.active = True
                    if self.can_shoot:
                        self.create_projectile()
                        self.can_shoot = False
                        self.shoot_time = pygame.time.get_ticks()

            # Update the game state and draw the frame
            self.display_surface.blit(self.bg, (0, 0))
            self.all_sprites.update(dt)
            self.upgrade_collision()
            self.laser_timer()
            self.projectile_block_collision()
            self.all_sprites.draw(self.display_surface)
            self.display_hearts()  

            # Refresh the display
            pygame.display.update()

if __name__ == "__main__":
    game = Game()
    game.run()
