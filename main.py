# Import the required modules
import os
import sys
import pygame
from random import randint, choice
from pygame.locals import (
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    K_SPACE,
    KEYDOWN,
    K_LSHIFT,
    K_RETURN,
    QUIT,
)


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller.
    URL: https://stackoverflow.com/questions/31836104/pyinstaller-and-onefile-how-to-include-an-image-in-the-exe-file
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS2  # Adjust to MEIPASS2 if not working
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Define constants for the screen width and height
WIDTH = 500
HEIGHT = 580

# Setup for sounds. Defaults are good.
pygame.mixer.init()

# Initialize pygame
pygame.init()


# Variable to keep the main loop running
paused = False
music_paused = False
score = 0
lane_distance = 50  # Distance between each lane
num_lanes = WIDTH // lane_distance  # Calculate the number of lanes based on width

# Fonts
END_GAME_FONT = pygame.font.SysFont("Calibri", 30, True, True)


# Create the screen object
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Markanove Kamiondžije")


# Load all sound files
crash_sound = pygame.mixer.Sound(resource_path("sounds\\Crash.ogg"))

# Set the base volume for all sounds
crash_sound.set_volume(0.5)

car_icons = [resource_path("images\\Car1.jpg"),
             resource_path("images\\Car2.jpg"),
             resource_path("images\\Car3.jpg")]


# Define a Player object by extending pygame.sprite.Sprite
# The surface drawn on the screen is now an attribute of "player"
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.image.load(resource_path("images\\Truck.jpg")).convert()
        self.surf.set_colorkey((BLACK), RLEACCEL)
        self.rect = self.surf.get_rect()
        self.rect.centerx = WIDTH // 2  # Set center x-coordinate
        self.rect.centery = HEIGHT  # Set bottom y-coordinate

    # Move the sprite based on user keypresses
    def update(self, pressed_keys):
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -5)
        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, 5)
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-5, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(5, 0)

        # Keep player on the screen
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.right >= WIDTH:
            self.rect.right = WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT


# Define the enemy object by extending pygame.sprite.Sprite
# The surface you draw on the screen is now an attribute of 'enemy'
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()
        self.car_icon = choice(car_icons)
        self.surf = pygame.image.load(self.car_icon).convert()
        self.surf.set_colorkey((BLACK), RLEACCEL)
        # The starting position is randomly generated, while the speed is 5
        self.rect = self.surf.get_rect()
        self.speed = 5
        # Determine the lane based on x-axis
        self.lane = self.rect.centerx // lane_distance

    def generate_enemy_position(self):
        lane = randint(0, num_lanes - 1)  # Generate random lane
        lane_x = lane * lane_distance  # Calculate x-coordinate based on lane
        return lane_x

    def generate_new_enemy(self):
        # Determines the lane based on x-axis
        self.lane = self.generate_enemy_position() // lane_distance
        self.rect.center = (self.lane * lane_distance + lane_distance // 2,
                            randint(-100, -20))

    # Move the sprite based on speed and lane
    # Remove the sprite when it passes the bottom edge of the screen
    def update(self):
        global score

        self.rect.move_ip(0, self.speed)
        if self.rect.top > HEIGHT:
            self.kill()
            score += 1
        # Update the x-coordinate based on lane
        self.rect.centerx = self.lane * lane_distance + lane_distance // 2


# Creating a custom event for adding a new enemy
ADDENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(ADDENEMY, 500)

# Instantiate player.
player = Player()

# Create groups to hold enemy sprites and all sprites
# - enemies is used for collision detection and position updates
# - all_sprites is used for rendering
enemies = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)


# Start the first song
current_song_index = 0

# Define the function to play the next song in the songs list
def play_next_song():
    global current_song_index
    new_song_index = current_song_index
    while new_song_index == current_song_index:
        new_song_index = choice(range(len(songs)))
    current_song_index = new_song_index
    current_song = songs[current_song_index]
    pygame.mixer.music.load(current_song)
    pygame.mixer.music.play()


# Load and play background music
songs = [resource_path("sounds\\Kamiondzije.ogg"),
         resource_path("sounds\\Kad coveka snadje beda.ogg"),
         resource_path("sounds\\Ajde_selo_da_selimo.ogg"),
         resource_path("sounds\\Kamiondzije_Tema.ogg"),
         resource_path("sounds\\Vokijevo_kolo.ogg"),
         resource_path("sounds\\Ovamo_Cigani.ogg"),
         resource_path("sounds\\Priča_Mala_E_Pa_Šta.ogg"),
         resource_path("sounds\\Prazna_Čaša_Na_Mom_Stolu.ogg"),
         resource_path("sounds\\Dance.ogg")]

background_music = pygame.mixer.music.load(songs[current_song_index])
pygame.mixer.music.set_endevent(pygame.constants.USEREVENT)
pygame.mixer.music.play()


def draw_road():
    # Fill the screen with yellow lanes
    lane_width = 7  # Width of each lane

    for i in range(num_lanes + 1):
        lane_x = i * lane_distance  # X-coordinate

        # Draw solid lines for left, right and middle lane
        if i == 0 or i == num_lanes or i == num_lanes // 2:
            pygame.draw.line(screen, YELLOW, (lane_x, 0),
                             (lane_x, HEIGHT), lane_width)
        else:
            # Draw dashed lines for other lanes
            dash_length = 10  # Length of each dash
            gap_length = 10  # Length of each gap between dashes

            # Calculate the number of dashes and gaps based on lane width
            num_dashes = (HEIGHT // (dash_length + gap_length)) + 1

            for j in range(num_dashes):
                dash_y = j * (dash_length + gap_length)
                pygame.draw.line(screen, YELLOW, (lane_x, dash_y),
                                 (lane_x, dash_y + dash_length), lane_width)


def display_welcome_message(message):
    screen.fill(BLACK)
    lines = [line.strip() for line in message.split("\n")]
    line_height = END_GAME_FONT.get_height()
    y_position = (HEIGHT - line_height * len(lines)) // 2

    for line in lines:
        line_text = END_GAME_FONT.render(line, 1, YELLOW)
        x_position = (WIDTH - line_text.get_width()) // 2
        screen.blit(line_text, (x_position, y_position))
        y_position += line_height

    pygame.display.update()

    # Shorter time delay for the welcome message
    pygame.time.delay(100)


def display_end_message(message):
    pygame.time.delay(2500)
    screen.fill(BLACK)
    lines = [line.strip() for line in message.split("\n")]
    line_height = END_GAME_FONT.get_height()
    y_position = (HEIGHT - line_height * len(lines)) // 2

    for line in lines:
        line_text = END_GAME_FONT.render(line, 1, YELLOW)
        x_position = (WIDTH - line_text.get_width()) // 2
        screen.blit(line_text, (x_position, y_position))
        y_position += line_height

    pygame.display.update()


def display_score():
    # Define the font, size, bold, non italic
    font = pygame.font.SysFont("Calibri", 25, True, False)
    # Render the text. "True" for anti-aliasing text.
    # Put the BLUE color.
    # Note: This line creates an image of the letters,
    # but does not put it on the screen yet.
    text = font.render("Score: " + str(score), True, BLUE)
    # Put the image of the text on the screen at 10x10
    screen.blit(text, [10, 10])


def reset_game():
    global score, player, enemies, lost, waiting
    score = 0 # Reset the score
    player = Player()
    all_sprites.empty()
    all_sprites.add(player)
    enemies.empty()
    lost = False
    waiting = False


def game():
    global running, paused, music_paused, lost, waiting
    FPS = 30
    clock = pygame.time.Clock()
    running = True

    # Reset the game flag when starting a new game
    lost = False

    while running:
        clock.tick(FPS)

        # Look at every event in the queue
        for event in pygame.event.get():
            # Did the user hit a key?
            if event.type == KEYDOWN:
                # Was it the Escape key? If so, stop the loop.
                if event.key == K_ESCAPE:
                    running = False
                if event.key == K_SPACE:
                    # Toggle the pause state when SPACE key is pressed
                    paused = not paused
                    # Check if the game is paused
                    if paused:
                        # Pause the music if the game is paused
                        pygame.mixer.music.pause()
                        music_paused = True
                    else:
                        # Unpause the musicif the game is unpaused
                        pygame.mixer.music.unpause()
                        music_paused = False
                if event.key == K_LSHIFT:
                    play_next_song()
                if not pygame.mixer.music.get_busy() and not music_paused:
                    play_next_song()

            # Did the user click the window close button? If so, stop the loop.
            elif event.type == QUIT:
                running = False

            # Add a new enemy?
            elif event.type == ADDENEMY:
                # Create the new enemy and add it to the sprite groups
                if not paused:  # Add enemies only if the game is not paused
                    new_enemy = Enemy()
                    new_enemy.generate_new_enemy()
                    # Check overlap
                    while pygame.sprite.spritecollideany(new_enemy, enemies): 
                        # Generate new position until no overlap
                        new_enemy.generate_new_enemy() 
                    enemies.add(new_enemy)
                    all_sprites.add(new_enemy)

        if not paused: # Update enemy position only if the game is not paused 
            # Update enemy position
            enemies.update()
            # Get the set of keys pressed and check for user input
            pressed_keys = pygame.key.get_pressed()
            player.update(pressed_keys)

        # Fill the scene with black color
        screen.fill((BLACK))

        draw_road()

        # Draw all sprites except player
        for entity in all_sprites:
            if entity != player:
                screen.blit(entity.surf, entity.rect)

        # Draw player sprite on top
        screen.blit(player.surf, player.rect)

        # Check if any enemies have collided with the player
        if not paused:  # Check collisions only if the game is not paused
            if pygame.sprite.spritecollideany(player, enemies):
                # If so, then remove the player and stop the loop
                player.kill()
                crash_sound.play()

                message = f"""You have LOST!
                                Press ENTER if you want to play again,
                                or press \"ESCAPE\" if you want to quit."""

                display_end_message(message)

                # Wait for player to click or press ESCAPE
                waiting = True
                lost = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == KEYDOWN:
                            if event.key == K_RETURN and lost:
                                reset_game()
                                waiting = False
                            elif event.key == K_ESCAPE:
                                running = False
                                waiting = False

        # Display the score
        display_score()

        # Flip everything to the display
        pygame.display.flip()

    # Quit pygame and mixer
    pygame.mixer.quit()
    pygame.quit()


def main():
    global running, message
    running = True

    # Display the welcome message
    message = """Welcome to the Kamiondžije game,
                inspired by the ex-yu
                tv show bearing the same name.
                The goal is to evade incoming cars.
                For every evaded car,
                you receive 1 score.
                Move your car with arrow keys,
                pause with "SPACE" and
                change the music with "LEFT SHIFT" key.
                Press "ENTER" to start the game."""
    display_welcome_message(message)

    while running:
        # Wait for the player to press ENTER
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == KEYDOWN and event.key == K_RETURN:
                    waiting = False
                elif event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    running = False
                    waiting = False

        if running:
            game()

    pygame.quit()
    pygame.mixer.quit()


if __name__ == "__main__":
    main()