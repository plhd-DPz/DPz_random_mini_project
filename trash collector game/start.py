import pygame
from achievement import Achievement

class StartScreen:
    def __init__(self, screen_width, screen_height):
        """
        Initialize the start screen.

        :param screen_width: Width of the screen.
        :param screen_height: Height of the screen.
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.start_button = pygame.Rect(screen_width // 2 - 150, screen_height // 2 - 60, 300, 70)
        self.achievement_button = pygame.Rect(screen_width // 2 - 150, screen_height // 2 + 30, 300, 70)
        self.help_button = pygame.Rect(screen_width - 60, 10, 50, 50)  # Nút dấu chấm hỏi
        self.skip_video_button = pygame.Rect(screen_width // 2 - 150, screen_height // 2 + 120, 300, 70)  # skip video button
        self.skip_video = False  

    def draw(self, screen):
        """
        Draw the start screen.

        :param screen: The pygame display surface.
        """
        # Background gradient
        for i in range(screen.get_height()):
            color = (
                int(135 * (1 - i/screen.get_height())),
                int(206 * (1 - i/screen.get_height())),
                int(250 * (1 - i/screen.get_height()))
            )
            pygame.draw.line(screen, color, (0, i), (screen.get_width(), i))

        # Title with shadow
        font = pygame.font.Font(pygame.font.match_font('Tahoma'), 60)
        title = font.render("Save the ocean", True, (0, 0, 0))
        screen.blit(title, (self.screen_width // 2 - title.get_width() // 2 + 2, 52))
        title = font.render("Save the ocean", True, (255, 255, 255))
        screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 50))

        # Buttons with gradients and hover effects
        mouse_pos = pygame.mouse.get_pos()
        self.draw_button(screen, self.start_button, "Start", mouse_pos)
        self.draw_button(screen, self.achievement_button, "Achievements", mouse_pos)
        self.draw_small_button(screen, self.help_button, "?", mouse_pos)
        self.draw_button(screen, self.skip_video_button, "Skip Intro", mouse_pos, self.skip_video)

    def draw_button(self, screen, button, text, mouse_pos, tick=False):
        hover = button.collidepoint(mouse_pos)
        color = (0, 150, 0) if hover else (0, 100, 0)
        pygame.draw.rect(screen, color, button, border_radius=15)
        pygame.draw.rect(screen, (255, 255, 255), button, 3, border_radius=15)
        
        font = pygame.font.Font(pygame.font.match_font('Tahoma'), 30)  
        text_surf = font.render(text, True, (255, 255, 255))
        screen.blit(text_surf, (button.centerx - text_surf.get_width() // 2,
                               button.centery - text_surf.get_height() // 2))
        
        if tick:
            tick_font = pygame.font.Font(pygame.font.match_font('Tahoma'), 40)
            tick_text = tick_font.render("✔", True, (255, 255, 255))
            screen.blit(tick_text, (button.right - 50, button.top + 10))

    def draw_small_button(self, screen, button, text, mouse_pos):
        hover = button.collidepoint(mouse_pos)
        color = (0, 150, 0) if hover else (0, 100, 0)
        pygame.draw.rect(screen, color, button, border_radius=15)
        pygame.draw.rect(screen, (255, 255, 255), button, 3, border_radius=15)
        
        font = pygame.font.Font(pygame.font.match_font('Tahoma'), 30)
        text_surf = font.render(text, True, (255, 255, 255))
        screen.blit(text_surf, (button.centerx - text_surf.get_width() // 2,
                               button.centery - text_surf.get_height() // 2))

    def start_button_clicked(self):
        """
        Check if the start button is clicked.

        :return: True if the start button is clicked, False otherwise.
        """
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        return self.start_button.collidepoint(mouse_pos) and mouse_pressed[0]

    def achievement_button_clicked(self):
        """
        Check if the achievement button is clicked.

        :return: True if the achievement button is clicked, False otherwise.
        """
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        return self.achievement_button.collidepoint(mouse_pos) and mouse_pressed[0]

    def help_button_clicked(self):
        """
        Check if the help button is clicked.

        :return: True if the help button is clicked, False otherwise.
        """
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        return self.help_button.collidepoint(mouse_pos) and mouse_pressed[0]

    def skip_video_button_clicked(self):
        """
        Check if the skip video button is clicked.

        :return: True if the skip video button is clicked, False otherwise.
        """
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        if self.skip_video_button.collidepoint(mouse_pos) and mouse_pressed[0]:
            self.skip_video = not self.skip_video
            return True
        return False


