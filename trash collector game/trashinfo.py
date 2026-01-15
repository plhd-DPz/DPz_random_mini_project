import os
import pygame

class TrashInfo:
    # path to resource folder
    resource_path = os.path.join(os.path.dirname(__file__), "resource")
    
    TRASH_TYPES = [
        {"id": 1, "image": os.path.join(resource_path, "trash1.png"), "points": 1},
        {"id": 2, "image": os.path.join(resource_path, "trash2.png"), "points": 1},
        {"id": 3, "image": os.path.join(resource_path, "trash3.png"), "points": 1},
        {"id": 4, "image": os.path.join(resource_path, "trash4.png"), "points": 1},
        {"id": 5, "image": os.path.join(resource_path, "trash5.png"), "points": 1},
        {"id": 6, "image": os.path.join(resource_path, "trash6.png"), "points": 1},
        {"id": 7, "image": os.path.join(resource_path, "trash7.png"), "points": 1},
        {"id": 8, "image": os.path.join(resource_path, "trash8.png"), "points": 1},
        {"id": 9, "image": os.path.join(resource_path, "trash9.png"), "points": 1},
        {"id": 10, "image": os.path.join(resource_path, "trash10.png"), "points": 1}
    ]
    
    def __init__(self):
        # temporary storage for collected trash information
        self.collected_trash = {}

    @staticmethod
    def get_image(trash_id):
        """
        Get the image file name of a specific type of trash by its id.

        :param trash_id: The id of the trash item.
        :return: Image file name of the trash item or 'unknown.png' if not found.
        """
        for trash in TrashInfo.TRASH_TYPES:
            if trash["id"] == trash_id:
                return trash["image"]
        return os.path.join(TrashInfo.resource_path, "unknown.png")

    @staticmethod
    def get_points(trash_id):
        """
        Get the points of a specific type of trash by its id.

        :param trash_id: The id of the trash item.
        :return: Points of the trash item or 0 if not found.
        """
        for trash in TrashInfo.TRASH_TYPES:
            if trash["id"] == trash_id:
                return trash["points"]
        return 0

    def collect_trash(self, trash_info):
        """
        Collects trash by adding it to the token (temporary storage).

        :param trash_info: Dictionary containing information about the collected trash.
        """
        trash_id = trash_info["id"]
        if trash_id not in self.collected_trash:
            self.collected_trash[trash_id] = trash_info
            print(f"Collected trash with {trash_info['points']} points.")
        else:
            print(f"Trash with id {trash_id} has already been collected.")

    def get_collected_trash(self):
        """
        Returns the list of collected trash.

        :return: Dictionary of collected trash.
        """
        return self.collected_trash

def display_trash_info(screen, x, y, trash_id):
    """
    Display the image of the trash on the screen at position (x, y) and the instruction text.

    :param screen: The pygame display surface.
    :param x: The x-coordinate of the box.
    :param y: The y-coordinate of the box.
    :param trash_id: The ID of the trash to get the image.
    """
    # Get the image path from TrashInfo
    image_path = TrashInfo.get_image(trash_id)
    image = pygame.image.load(image_path)
    image = pygame.transform.scale(image, (360, 450))

    # Draw the image on the screen
    screen.blit(image, (x, y))

    # Draw the instruction text
    font_path = pygame.font.match_font('Tahoma')  # Use Tahoma font for Vietnamese support
    font = pygame.font.Font(font_path, 36)
    text = font.render("Press space to continue", True, (255, 255, 255))
    text_rect = text.get_rect(center=(x + 180, y + 480))
    screen.blit(text, text_rect)

class DataBook:
    def __init__(self):
        self.collected_trash = {i: False for i in range(1, 11)}
        self.displaying_trash_id = None  # ID of the trash being displayed

    def collect_trash(self, trash_id):
        self.collected_trash[trash_id] = True

    def draw(self, screen):
        screen.fill((255, 255, 255))  # Clear the screen with white background
        font = pygame.font.Font(pygame.font.match_font('Tahoma'), 14)
        text = font.render("Press space to exit", True, (0, 0, 0))
        screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, 10))

        for i, trash in enumerate(TrashInfo.TRASH_TYPES):
            x = 50 + (i % 5) * 150
            y = 100 + (i // 5) * 250  # Increase spacing vertically
            if self.collected_trash[trash["id"]]:
                image = pygame.image.load(trash["image"])
                image = pygame.transform.scale(image, (113, 150))
                screen.blit(image, (x, y))
            else:
                pygame.draw.rect(screen, (200, 200, 200), (x, y, 100, 100))
                text = font.render("not collected", True, (0, 0, 0))
                screen.blit(text, (x + 5, y + 45))

            # numbering the trash items
            number_text = font.render(str(i + 1), True, (0, 0, 0))
            screen.blit(number_text, (x + 45, y + 160))

        # description instruction
        instruction_font = pygame.font.Font(pygame.font.match_font('Tahoma'), 18)
        instruction_text = instruction_font.render("Press number keys for details, space to exit", True, (255, 0, 0))
        screen.blit(instruction_text, (screen.get_width() // 2 - instruction_text.get_width() // 2, screen.get_height() - 30))

        # Display trash image if any
        if self.displaying_trash_id:
            display_trash_info(screen, 245, 75, self.displaying_trash_id)

    def handle_key_event(self, event):
        """
        Handle key press events to display detailed trash images.
        """
        if event.type == pygame.KEYDOWN:
            if pygame.K_1 <= event.key <= pygame.K_0 + 10:
                trash_id = event.key - pygame.K_0
                if self.collected_trash.get(trash_id):
                    self.displaying_trash_id = trash_id
            elif event.key == pygame.K_SPACE:
                if self.displaying_trash_id:
                    self.displaying_trash_id = None
                else:
                    return True
        return False

    def back_button_clicked(self):
        """
        Check if the user clicked the space key to exit.
        """
        for event in pygame.event.get():
            if self.handle_key_event(event):
                return True
        return False

def hide_trash_info():
    """
    Hide the box when the user presses the space key.
    """
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            return True
    return False
