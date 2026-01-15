import pygame

class FinishScreen:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.play_again_button = pygame.Rect(
            screen_width // 2 - 100, 
            screen_height * 2 // 3,
            200, 50
        )

    def draw(self, screen, total_score):
        # Draw gradient background
        for i in range(self.screen_height):
            color = (
                int(135 * (1 - i/self.screen_height)),
                int(206 * (1 - i/self.screen_height)),
                int(250 * (1 - i/self.screen_height))
            )
            pygame.draw.line(screen, color, (0, i), (self.screen_width, i))

        # Draw "Game Over!" with shadow effect
        title_font = pygame.font.Font(pygame.font.match_font('Tahoma'), 72)
        title_shadow = title_font.render("Game Over!", True, (0, 0, 0))
        title_text = title_font.render("Game Over!", True, (255, 255, 255))

        title_x = self.screen_width // 2 - title_text.get_width() // 2
        title_y = self.screen_height // 5
        
        screen.blit(title_shadow, (title_x + 2, title_y + 2))
        screen.blit(title_text, (title_x, title_y))

        # Display score
        score_font = pygame.font.Font(pygame.font.match_font('Tahoma'), 48)
        score_text = score_font.render(f"Total Score: {total_score}", True, (0, 100, 0))
        score_pos = (self.screen_width // 2 - score_text.get_width() // 2, 
                    self.screen_height // 2)
        screen.blit(score_text, score_pos)

        # Draw play again button with hover effect
        mouse_pos = pygame.mouse.get_pos()
        button_color = (0, 150, 0) if self.play_again_button.collidepoint(mouse_pos) else (0, 100, 0)
        
        pygame.draw.rect(screen, button_color, self.play_again_button, border_radius=15)
        pygame.draw.rect(screen, (255, 255, 255), self.play_again_button, 3, border_radius=15)
        
        button_font = pygame.font.Font(pygame.font.match_font('Tahoma'), 40)
        button_text = button_font.render("Play Again", True, (255, 255, 255))
        text_pos = (self.play_again_button.centerx - button_text.get_width() // 2,
                   self.play_again_button.centery - button_text.get_height() // 2)
        screen.blit(button_text, text_pos)

        pygame.display.flip()

    def check_play_again(self):
        """Check if the play again button was clicked"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]  # Left click
        return self.play_again_button.collidepoint(mouse_pos) and mouse_clicked
