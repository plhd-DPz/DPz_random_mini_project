import pygame
import random
import os
from trashinfo import TrashInfo, DataBook, display_trash_info, hide_trash_info 


class Trash:
    resource_path = os.path.join(os.path.dirname(__file__), "resource")
    trash_image = pygame.image.load(os.path.join(resource_path, "trashbag.png"))
    def __init__(self, x, y, width=100, height=100, info=None):
        self.original_x = x
        self.original_y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        image_width = int(width * 2.85)
        image_height = int(height * 1.5)
        self.image = pygame.transform.scale(Trash.trash_image, (image_width, image_height))
        self.image_offset_x = (image_width - width) // 2
        self.image_offset_y = (image_height - height) // 2
        self.info = info if info else random.choice(TrashInfo.TRASH_TYPES)
        self.collection_radius = 40  # Increased collection radius

    def draw(self, screen, offset_x=0, offset_y=0):
        # Calculate screen position based on original position and offset
        screen_x = self.original_x - offset_x
        screen_y = self.original_y - offset_y
        
        # Only draw if on screen
        if (0 <= screen_x <= screen.get_width() and 
            0 <= screen_y <= screen.get_height()):
            self.rect.topleft = (screen_x, screen_y)
            screen.blit(self.image, (screen_x - self.image_offset_x, 
                                   screen_y - self.image_offset_y))

class TrashSpawner:
    def __init__(self, spawn_area_width=800, spawn_area_height=600, max_trash=30, data_book=None):
        self.spawn_area_width = spawn_area_width
        self.spawn_area_height = spawn_area_height
        self.max_trash = max_trash
        self.trash_list = []
        self.score = 0
        self.last_spawn_time = pygame.time.get_ticks()
        self.spawn_delay = 1000  # 1 second between spawns
        self.recent_collections = []  # List of recently collected trash for display
        self.min_trash = 15
        self.spawn_cycle = 3000  # 3 seconds
        self.despawn_time = 10000  # 10 seconds
        self.screen_offset_x = 0
        self.screen_offset_y = 0
        self.display_info = False  # status to show trash info
        self.current_trash_id = None  # ID of the current trash
        self.data_book = data_book  # Instance of DataBook

    def update_screen_offset(self, x, y):
        """Update screen offset."""
        self.screen_offset_x = x
        self.screen_offset_y = y

    def spawn_trash(self, count=1):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_spawn_time >= self.spawn_delay:
            needed_trash = max(0, self.min_trash - len(self.trash_list))
            spawn_count = random.randint(needed_trash, needed_trash + 3)
            
            for _ in range(spawn_count):
                if len(self.trash_list) < self.max_trash:
                    x = random.randint(0, self.spawn_area_width - 30)
                    y = random.randint(0, self.spawn_area_height - 30)
                    self.trash_list.append(Trash(x, y))
            self.last_spawn_time = current_time

    def draw(self, screen, offset_x=0, offset_y=0, beach=True):
        """
        Draw trash and hitbox for debug (optional).
        """
        for trash in self.trash_list:
            trash.draw(screen, offset_x, offset_y)
            # Uncomment để debug hitbox
            # pygame.draw.rect(screen, (255,0,0), trash.rect, 1)

    def check_collision(self, character, trash_info):
        """
        Check collision with the fixed hitbox of the character.
        """
        char_hitbox = character.get_hitbox()
        for trash in self.trash_list[:]:
            # Calculate the actual position of the trash on the screen
            trash_screen_pos = (
                trash.original_x - self.screen_offset_x,
                trash.original_y - self.screen_offset_y
            )
            trash_rect = pygame.Rect(
                trash_screen_pos[0],
                trash_screen_pos[1],
                trash.width,
                trash.height
            )
            
            if char_hitbox.colliderect(trash_rect):
                self.score += trash.info['points']
                trash_info.collect_trash(trash.info)
                self.trash_list.remove(trash)
                self.recent_collections.append((trash.info['points'], pygame.time.get_ticks()))
                self.display_info = True  # Show trash info box
                self.current_trash_id = trash.info['id']  # Save ID of the current trash
                if self.data_book:
                    self.data_book.collect_trash(trash.info['id'])  # Update collection status in DataBook

    def create_collection_token(self, trash_info):
        """
        Create a token to notify that a piece of trash was collected.

        :param trash_info: Information about the collected trash.
        """
        print(f"Token created: {trash_info['name']} collected!")

    def create_score_token(self):
        """
        Create a token to notify the current total score.
        """
        print(f"Token created: Total Score = {self.score}")

    def get_total_score(self):
        """
        Get the total score from collected trash.

        :return: Total score.
        """
        return self.score

    def update_score_display(self, screen, dt):
        current_time = pygame.time.get_ticks()
        font = pygame.font.Font(None, 24)
        
        for i, (score, time_created) in enumerate(self.recent_collections):
            if current_time - time_created > 1000:  # Display for 1 second
                self.recent_collections.remove((score, time_created))
                continue
                
            text = font.render(f"+{score}", True, (0, 255, 0))
            screen.blit(text, (10, 40 + i * 25))
