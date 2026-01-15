import pygame
import os
import cv2  
from start import StartScreen
from bg import Background
from char import Character
from tyme import Tyme
from spawn import TrashSpawner
from trashinfo import TrashInfo, DataBook, display_trash_info, hide_trash_info  
from achievement import Achievement
from finish import FinishScreen 

pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen_info = pygame.display.Info()
os_screen_width = screen_info.current_w
os_screen_height = screen_info.current_h
os.environ['SDL_VIDEO_WINDOW_POS'] = f"{(os_screen_width-SCREEN_WIDTH)//2},{(os_screen_height-SCREEN_HEIGHT)//2}"

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ocean Cleanup Game")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

bgm_path = os.path.join(os.path.dirname(__file__), "resource", "bgm.mp3")
pygame.mixer.music.load(bgm_path)
pygame.mixer.music.play(-1)  # Loop

# Game components
resource_path = os.path.join(os.path.dirname(__file__), "resource")
start_screen = StartScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
beach_bg = Background(os.path.join(resource_path, "beach.png"), SCREEN_WIDTH, SCREEN_HEIGHT)
ocean_bg = Background(os.path.join(resource_path, "ocean.png"), SCREEN_WIDTH, SCREEN_HEIGHT)
timer = Tyme(3)  
trash_info = TrashInfo()
achievement = Achievement()
finish_screen = FinishScreen(SCREEN_WIDTH, SCREEN_HEIGHT)  
data_book = DataBook()  

# Game states
STATE_START = "start"
STATE_DAY1 = "day1"
STATE_DAY2 = "day2"
STATE_END = "end"
STATE_DATA_BOOK = "data_book"

global character, trash_spawner, state, total_score, previous_state, skip_video
character = Character(100, 100, os.path.join(resource_path, "character1.png"))
trash_spawner = TrashSpawner(*beach_bg.get_image_size(), data_book=data_book)  # background size, data_book instance
state = STATE_START
previous_state = None  
total_score = 0
skip_video = False  

def play_video(video_path):
    cap = cv2.VideoCapture(video_path)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = pygame.surfarray.make_surface(frame)
        frame = pygame.transform.rotate(frame, -90)
        frame = pygame.transform.flip(frame, True, False)
        frame = pygame.transform.scale(frame, (SCREEN_WIDTH, SCREEN_HEIGHT))  # limit video size to screen size
        screen.blit(frame, (0, 0))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                pygame.quit()
                exit()
    cap.release()

def run_game():
    global state, character, trash_spawner, total_score, previous_state, skip_video
    running = True
    clock = pygame.time.Clock()

    screen_offset_x = 0
    screen_offset_y = 0

    # speed and velocity settings
    SCREEN_SPEED_X = 5  # Horizontal display movement speed
    SCREEN_SPEED_Y = 5  # Vertical display movement speed
    VELOCITY_A = 5      # Base velocity
    VELOCITY_B = 5      # Axial snap velocity (equal to base velocity)
    AXIS_TOLERANCE = 2  # Tolerance for axis alignment checks

    # Adjust overall game speed
    BASE_FPS = 60  # Keep FPS constant to ensure smoothness

    # Initialize spawn timer
    spawn_timer = pygame.time.get_ticks()
    SPAWN_DELAY = 1000  # Spawn new trash every 1 second

    while running:
        current_time = pygame.time.get_ticks()
        
        dt = clock.tick(BASE_FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                previous_state = state 
                state = STATE_DATA_BOOK

        if state == STATE_START:
            screen.fill(WHITE)
            start_screen.draw(screen)
            if start_screen.start_button_clicked():
                if not skip_video:
                    play_video(os.path.join(resource_path, "intro.mp4"))
                state = STATE_DAY1
                timer.reset()
                total_score = 0  # Reset total score at the start of the game
            elif start_screen.achievement_button_clicked():
                achievement.show(screen)
            elif start_screen.help_button_clicked(): 
                # description screen
                screen.fill(WHITE)
                font = pygame.font.Font(pygame.font.match_font('Tahoma'), 24)
                text = font.render("Clean the ocean", True, (0, 0, 0))
                screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, screen.get_height() // 2))
                pygame.display.flip()
                pygame.time.wait(3000)  # 3 seconds
                state = STATE_START
            elif start_screen.skip_video_button_clicked():
                skip_video = not skip_video

        elif state in [STATE_DAY1, STATE_DAY2]:
            screen.fill(WHITE)
            bg = beach_bg if state == STATE_DAY1 else ocean_bg
            keys = pygame.key.get_pressed()

            screen_is_moving = False
            screen_movement = [0, 0]  # [dx, dy] for display screen

            if keys[pygame.K_LEFT] and screen_offset_x > 0:
                screen_movement[0] = -SCREEN_SPEED_X
                screen_is_moving = True
            elif keys[pygame.K_RIGHT] and screen_offset_x < bg.image_width - SCREEN_WIDTH:
                screen_movement[0] = SCREEN_SPEED_X
                screen_is_moving = True

            if keys[pygame.K_UP] and screen_offset_y > 0:
                screen_movement[1] = -SCREEN_SPEED_Y
                screen_is_moving = True
            elif keys[pygame.K_DOWN] and screen_offset_y < bg.image_height - SCREEN_HEIGHT:
                screen_movement[1] = SCREEN_SPEED_Y
                screen_is_moving = True

            if screen_is_moving:
                char_pos = character.get_center()
                screen_center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                on_y_axis, on_x_axis = character.check_axis_alignment(char_pos, screen_center)

                if not on_y_axis:  
                    screen_movement[0] = 0
                if not on_x_axis:  
                    screen_movement[1] = 0

                screen_offset_x += screen_movement[0]
                screen_offset_y += screen_movement[1]

            screen_bounds = bg.get_screen_bounds(screen_offset_x, screen_offset_y)

            if screen_is_moving:
                screen_center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                dx = dy = 0
                if keys[pygame.K_LEFT]: dx = -1
                if keys[pygame.K_RIGHT]: dx = 1
                if keys[pygame.K_UP]: dy = -1
                if keys[pygame.K_DOWN]: dy = 1
                
                character.move(dx, dy, SCREEN_WIDTH, SCREEN_HEIGHT, 
                             is_display_moving=True,
                             screen_center=screen_center,
                             screen_bounds=screen_bounds)
            else:
                dx = dy = 0
                if keys[pygame.K_LEFT]: dx = -1
                if keys[pygame.K_RIGHT]: dx = 1
                if keys[pygame.K_UP]: dy = -1
                if keys[pygame.K_DOWN]: dy = 1
                character.move(dx, dy, SCREEN_WIDTH, SCREEN_HEIGHT)

            bg.draw(screen, screen_offset_x, screen_offset_y)
            character.draw(screen)
            trash_spawner.draw(screen, screen_offset_x, screen_offset_y)
            trash_spawner.update_screen_offset(screen_offset_x, screen_offset_y)

            if current_time - spawn_timer >= SPAWN_DELAY:
                trash_spawner.spawn_trash(count=1)
                spawn_timer = current_time

            trash_spawner.draw(screen, screen_offset_x, screen_offset_y, beach=(state == STATE_DAY1))

            trash_spawner.check_collision(character, trash_info)
            total_score = trash_spawner.get_total_score()  # Update total score

            if trash_spawner.display_info:
                display_trash_info(screen, 245, 75, trash_spawner.current_trash_id) 
                if hide_trash_info():
                    trash_spawner.display_info = False 
                else:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_SPACE]:
                        trash_spawner.display_info = False 
                    else:
                        SCREEN_SPEED_X = 0
                        SCREEN_SPEED_Y = 0
                        VELOCITY_A = 0
                        VELOCITY_B = 0
            else:
                SCREEN_SPEED_X = 5
                SCREEN_SPEED_Y = 5
                VELOCITY_A = 5
                VELOCITY_B = 5

            if state != STATE_DATA_BOOK:  
                timer.update(screen, trash_spawner.display_info)

            day_font = pygame.font.Font(pygame.font.match_font('Tahoma'), 30)
            day_text = day_font.render(f"Ngày {1 if state == STATE_DAY1 else 2}", True, (255, 0, 0))
            screen.blit(day_text, (10, 10))

            # display score
            score_font = pygame.font.Font(pygame.font.match_font('Tahoma'), 24)
            score_text = score_font.render(f"Điểm: {total_score}", True, (0, 0, 255))
            screen.blit(score_text, (10, 50))

            data_book_button = pygame.Rect(10, SCREEN_HEIGHT - 60, 50, 50)
            pygame.draw.rect(screen, (0, 100, 0), data_book_button, border_radius=15)
            pygame.draw.rect(screen, (255, 255, 255), data_book_button, 3, border_radius=15)
            button_font = pygame.font.Font(pygame.font.match_font('Tahoma'), 30)
            button_text = button_font.render("B", True, (255, 255, 255))
            screen.blit(button_text, (data_book_button.centerx - button_text.get_width() // 2,
                                      data_book_button.centery - button_text.get_height() // 2))

            if data_book_button.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                previous_state = state  
                state = STATE_DATA_BOOK

            if keys[pygame.K_b]:
                previous_state = state  
                state = STATE_DATA_BOOK

            if timer.time_up():
                if state == STATE_DAY1:
                    state = STATE_DAY2
                    character = Character(100, 100, os.path.join(resource_path, "character2.png"))  # Reset character for day 2
                else:
                    if not skip_video:
                        play_video(os.path.join(resource_path, "aftercredit.mp4"))
                    state = STATE_END
                timer.reset()

        elif state == STATE_END:
            finish_screen.draw(screen, total_score)
            achievement.save_achievement(total_score)  # Save total score to achievements
            
            if finish_screen.check_play_again():
                state = STATE_START
                screen_offset_x = 0
                screen_offset_y = 0
                # Reset values
                trash_spawner = TrashSpawner(*beach_bg.get_image_size(), data_book=data_book)
                character = Character(100, 100, os.path.join(resource_path, "character1.png"))  # Reset character for day 1

            pygame.display.flip()

        elif state == STATE_DATA_BOOK:
            screen.fill(WHITE)
            data_book.draw(screen)
            if data_book.back_button_clicked():
                state = previous_state 

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    run_game()
