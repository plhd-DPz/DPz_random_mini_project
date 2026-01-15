import pygame
from PIL import Image

class Character:
    def __init__(self, x, y, image_path, SCREEN_WIDTH=800, SCREEN_HEIGHT=600):
        #create character at position (x, y) with image from image_path
        self.x = x
        self.y = y
        self.image_path = image_path
        self.original_image = pygame.image.load(image_path)
        scale_factor = 3
        new_width = self.original_image.get_width() // scale_factor
        new_height = self.original_image.get_height() // scale_factor
        self.image = pygame.transform.scale(self.original_image, (new_width, new_height))
        self.rect = self.image.get_rect(topleft=(x, y))

        # Basic speed for each direction
        self.base_speed = 5     # Base speed
        self.speed_left = self.base_speed
        self.speed_right = self.base_speed
        self.speed_up = self.base_speed
        self.speed_down = self.base_speed
        self.border_speed = self.base_speed  # Border speed is the same as base speed
        self.axis_alignment_tolerance = 2

        # Position and size attributes
        self.center_x = x + self.rect.width // 2
        self.center_y = y + self.rect.height // 2
        self.hitbox_size = 40
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT

        # Variable to track facing direction
        self.facing_right = True  # Default facing right

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self, dx, dy, SCREEN_WIDTH, SCREEN_HEIGHT, is_display_moving=False, screen_center=None, screen_bounds=None):
        """
        Move the character with 4 independent directions.
        screen_bounds: (is_at_left, is_at_right, is_at_top, is_at_bottom)
        """
        if dx != 0 or dy != 0:
            final_dx = final_dy = 0
            
            if is_display_moving and screen_center:
                current_pos = self.get_center()
                dist_to_y_axis = abs(current_pos[0] - screen_center[0])
                dist_to_x_axis = abs(current_pos[1] - screen_center[1])
                # Move with full speed when not axis-aligned
                if dx < 0:  # left
                    final_dx = -self.base_speed if dist_to_y_axis > self.axis_alignment_tolerance else 0
                elif dx > 0:  # right
                    final_dx = self.base_speed if dist_to_y_axis > self.axis_alignment_tolerance else 0

                if dy < 0:  # up
                    final_dy = -self.base_speed if dist_to_x_axis > self.axis_alignment_tolerance else 0
                elif dy > 0:  # down
                    final_dy = self.base_speed if dist_to_x_axis > self.axis_alignment_tolerance else 0

                # Handle movement when at screen edges
                if screen_bounds:
                    is_at_left, is_at_right, is_at_top, is_at_bottom = screen_bounds
                    if (is_at_left and dx < 0) or (is_at_right and dx > 0):
                        final_dx = dx * self.base_speed
                    if (is_at_top and dy < 0) or (is_at_bottom and dy > 0):
                        final_dy = dy * self.base_speed
            else:
                final_dx = dx * self.base_speed
                final_dy = dy * self.base_speed

            # Update position
            new_x = self.x + final_dx
            new_y = self.y + final_dy

            # Limit within screen
            margin_x = -70  # Reduce margin to allow character to reach horizontal edges
            margin_y = -20  # Reduce margin to allow character to reach vertical edges
            if margin_x <= new_x <= SCREEN_WIDTH - self.rect.width - margin_x:
                self.x = new_x
            if margin_y <= new_y <= SCREEN_HEIGHT - self.rect.height - margin_y:
                self.y = new_y

            # Update rect and center
            self.rect.topleft = (self.x, self.y)
            self.center_x = self.x + self.rect.width // 2
            self.center_y = self.y + self.rect.height // 2

            # Check movement direction and flip image if needed
            if dx > 0 and not self.facing_right:  # Moving right and facing left
                self.flip_image()
                self.facing_right = True
            elif dx < 0 and self.facing_right:  # Moving left and facing right
                self.flip_image()
                self.facing_right = False

    def get_center(self):
        return (self.center_x, self.center_y)

    def get_hitbox(self):
        return pygame.Rect(
            self.x + self.rect.width // 2 - self.hitbox_size // 2,
            self.y + self.rect.height // 2 - self.hitbox_size // 2,
            self.hitbox_size,
            self.hitbox_size
        )

    def flip_image(self):
        """Flip the character's image."""
        self.image = pygame.transform.flip(self.image, True, False)

    def check_axis_alignment(self, char_pos, screen_center):
        """
        Check if the character is aligned with the x or y axis.
        Returns (is_on_y_axis, is_on_x_axis)
        """
        dx = abs(char_pos[0] - screen_center[0])  # Distance to y axis
        dy = abs(char_pos[1] - screen_center[1])  # Distance to x axis

        # Check if aligned with axes
        on_y_axis = dx <= self.axis_alignment_tolerance
        on_x_axis = dy <= self.axis_alignment_tolerance
        
        return on_y_axis, on_x_axis

    def calculate_dynamic_velocity(self, char_pos, screen_center):
        """
        Calculate velocity based on relative position to the x, y axes passing through the center.
        Returns (vx, vy) as the velocity components in the horizontal and vertical directions.
        """
        dx = abs(char_pos[0] - screen_center[0])
        dy = abs(char_pos[1] - screen_center[1])
        
        tolerance = 2
        vx = vy = self.base_speed  # Use base_speed for both components

        if dx <= tolerance:
            vx = 0
        if dy <= tolerance:
            vy = 0
        if dx <= tolerance and dy <= tolerance:
            vx = vy = 0

        return vx, vy

    def is_character_centered(self):
        char_center = self.get_center()
        screen_center = (self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2)
        return (abs(char_center[0] - screen_center[0]) < 5 and 
                abs(char_center[1] - screen_center[1]) < 5)
