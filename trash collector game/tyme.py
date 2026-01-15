import pygame
import time

class Tyme:
    def __init__(self, duration_minutes):
        """
        Initialize the timer.

        :param duration_minutes: Total duration of the timer in minutes.
        """
        self.total_time = duration_minutes * 60  # Convert minutes to seconds
        self.remaining_time = self.total_time
        self.start_time = time.time()
        self.bar_width = 630  # Slightly smaller for margins
        self.bar_height = 25  # Slightly taller
        self.margin = 19  # Margin from screen edges
        self.paused = False

    def reset(self):
        """
        Reset the timer to its full duration.
        """
        self.remaining_time = self.total_time
        self.start_time = time.time()
        self.paused = False

    def update(self, screen, display_info):
        """
        Update the timer and draw the time bar on the screen.

        :param screen: The pygame display surface.
        :param display_info: Boolean indicating if the trash info display is active.
        """
        if display_info:
            self.paused = True
        else:
            if self.paused:
                self.start_time = time.time() - (self.total_time - self.remaining_time)
                self.paused = False

            # Calculate remaining time
            elapsed_time = time.time() - self.start_time
            self.remaining_time = max(0, self.total_time - elapsed_time)

        # Calculate the current width of the time bar
        current_width = int((self.remaining_time / self.total_time) * self.bar_width)

        # Draw background bar
        pygame.draw.rect(screen, (100, 100, 100), 
                        (self.margin + 120, self.margin, 
                         self.bar_width, self.bar_height))
        
        # Draw progress bar with gradient color
        progress = self.remaining_time / self.total_time
        if progress > 0.6:
            color = (0, 255, 0)  # Green
        elif progress > 0.3:
            color = (255, 255, 0)  # Yellow
        else:
            color = (255, 0, 0)  # Red
            
        pygame.draw.rect(screen, color,
                        (self.margin + 120, self.margin,
                         current_width, self.bar_height))
        
        # Draw border
        pygame.draw.rect(screen, (0, 0, 0),
                        (self.margin + 120, self.margin,
                         self.bar_width, self.bar_height), 2)

    def time_up(self):
        """
        Check if the time has run out.

        :return: True if time is up, False otherwise.
        """
        return self.remaining_time <= 0


