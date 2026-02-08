import os
import json
import pygame

class Achievement:
    def __init__(self, file_path="achievements.json"):
        """
        Initialize the achievement system.

        :param file_path: Path to the JSON file storing achievements.
        """
        self.file_path = file_path
        self.achievements = self.load_achievements()
        self.last_saved_score = None

    def load_achievements(self):
        """
        Load achievements from the file. If the file doesn't exist, create an empty one.

        :return: A dictionary of achievements.
        """
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                return json.load(f)
        else:
            return {}

    def save_achievement(self, score):
        """
        Save a new achievement with the given score.

        :param score: The score achieved in the current game session.
        """
        if score != self.last_saved_score:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.achievements[timestamp] = score
            with open(self.file_path, 'w') as f:
                json.dump(self.achievements, f, indent=4)
            self.last_saved_score = score

    def clear_achievements(self):
        """
        Clear all achievements.
        """
        self.achievements = {}
        with open(self.file_path, 'w') as f:
            json.dump(self.achievements, f, indent=4)

    def show(self, screen):
        """
        Display all achievements on the screen.

        :param screen: The pygame display surface.
        """
        font = pygame.font.Font(pygame.font.match_font('Tahoma'), 36)
        y_offset = 150
        screen.fill((173, 216, 230))  # Clear the screen with a light blue background

        title = font.render("Thành Tựu", True, (0, 0, 0))
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 10))

        if not self.achievements:
            no_achievements_text = font.render("Bạn chưa có thành tựu nào", True, (0, 0, 0))
            screen.blit(no_achievements_text, (screen.get_width() // 2 - no_achievements_text.get_width() // 2, screen.get_height() // 2))
        else:
            for i, (timestamp, score) in enumerate(self.achievements.items(), start=1):
                achievement_text = f"Lần {i}: {timestamp} - {score} điểm"
                text_surface = font.render(achievement_text, True, (0, 0, 0))
                screen.blit(text_surface, (50, y_offset))
                y_offset += 40

        # back buton
        back_button = pygame.Rect(screen.get_width() // 2 - 100, screen.get_height() - 100, 200, 50)
        pygame.draw.rect(screen, (0, 100, 0), back_button, border_radius=15)
        pygame.draw.rect(screen, (255, 255, 255), back_button, 3, border_radius=15)
        
        button_font = pygame.font.Font(pygame.font.match_font('Tahoma'), 40)
        button_text = button_font.render("Quay lại", True, (255, 255, 255))
        text_pos = (back_button.centerx - button_text.get_width() // 2,
                   back_button.centery - button_text.get_height() // 2)
        screen.blit(button_text, text_pos)

        # Draw clear button
        clear_button = pygame.Rect(screen.get_width() // 2 - 100, screen.get_height() - 200, 200, 50)
        pygame.draw.rect(screen, (200, 0, 0), clear_button, border_radius=15)
        pygame.draw.rect(screen, (255, 255, 255), clear_button, 3, border_radius=15)
        
        clear_text = button_font.render("Xóa Thành Tựu", True, (255, 255, 255))
        clear_text_pos = (clear_button.centerx - clear_text.get_width() // 2,
                          clear_button.centery - clear_text.get_height() // 2)
        screen.blit(clear_text, clear_text_pos)

        pygame.display.flip()

        # wait for user interaction
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button.collidepoint(event.pos):
                        waiting = False
                        break
                    elif clear_button.collidepoint(event.pos):
                        self.clear_achievements()
                        self.show(screen)  # Refresh the screen
                        break

