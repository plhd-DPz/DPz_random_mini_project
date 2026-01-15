import pygame

class Background:
    def __init__(self, image_path, width, height):
        """
        Initialize the background.

        :param image_path: Path to the background image file.
        :param width: Width of the screen.
        :param height: Height of the screen.
        """
        self.image = pygame.image.load(image_path)

        # Zoom in the background image by a factor of 3
        self.image_width = self.image.get_width() * 3   
        self.image_height = self.image.get_height() * 3   

        self.image = pygame.transform.scale(self.image, (self.image_width, self.image_height))
        self.width = width
        self.height = height

    def draw(self, screen, offset_x, offset_y):
        """
        Draw the background on the screen with the calculated offset.

        :param screen: The pygame display surface.
        :param offset_x: The horizontal offset for the scrolling background.
        :param offset_y: The vertical offset for the scrolling background.
        """
        # Only draw the parts of the background that are within the screen bounds
        for x in range(0, self.width, self.image_width):
            for y in range(0, self.height, self.image_height):
                # Draw the parts of the background according to the offset x and y
                screen.blit(self.image, (x - offset_x % self.image_width, y - offset_y % self.image_height))

    def get_image_size(self):
        """
        Return the size of the background image for determining movement limits.

        :return: Tuple containing the width and height of the background image.
        """
        return self.image_width, self.image_height

    def get_screen_bounds(self, screen_offset_x, screen_offset_y):
        """Determine the screen bounds."""
        return (
            screen_offset_x <= 0,
            screen_offset_x >= self.image_width - self.width,
            screen_offset_y <= 0,
            screen_offset_y >= self.image_height - self.height
        )

    def create_movement_guides(self, screen_offset_x, screen_offset_y):
        """Create movement guides based on the position of the screen."""
        guides = []
        screen_center = (self.width // 2, self.height // 2)

        # Check edges
        at_left = screen_offset_x <= 0
        at_right = screen_offset_x >= self.image_width - self.width
        at_top = screen_offset_y <= 0
        at_bottom = screen_offset_y >= self.image_height - self.height

        if at_left:
            guides.append(("vertical", (0, screen_center[1])))
        if at_right:
            guides.append(("vertical", (self.width, screen_center[1])))
        if at_top:
            guides.append(("horizontal", (screen_center[0], 0)))
        if at_bottom:
            guides.append(("horizontal", (screen_center[0], self.height)))

        return guides
