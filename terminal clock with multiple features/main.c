#include <stdio.h>
#include <time.h>
#include <windows.h>
#include <conio.h>
#include <string.h>

#define RESET   "\033[0m"
#define RED     "\033[31m"
#define GREEN   "\033[32m"
#define YELLOW  "\033[33m"
#define BLUE    "\033[34m"
#define PURPLE  "\033[35m"
#define CYAN    "\033[36m"

char currentColor[20] = "\033[0m";

void help() {
    printf("%s\n========== TIME UTILITY HELP ==========\n" RESET, currentColor);

    printf("%s\nAvailable commands:\n" RESET, currentColor);
    printf("%s/help           : show this help message\n" RESET, currentColor);
    printf("%s/clock          : open digital clock mode\n" RESET, currentColor);
    printf("%s/stopwatch      : open stopwatch mode\n" RESET, currentColor);
    printf("%s/countdown      : start countdown mode\n" RESET, currentColor);
    printf("%s/color          : show available colors\n" RESET, currentColor);
    printf("%s/color NAME     : change interface color\n" RESET, currentColor);
    printf("%s/exit           : exit program\n" RESET, currentColor);

    printf("%s\nClock mode:\n" RESET, currentColor);
    printf("%s  - Shows current system time\n" RESET, currentColor);
    printf("%s  - Press 'q' to return to menu\n" RESET, currentColor);

    printf("%s\nStopwatch mode:\n" RESET, currentColor);
    printf("%s  - Measure elapsed time\n" RESET, currentColor);

    printf("%s\nCountdown mode:\n" RESET, currentColor);
    printf("%s  - Enter number of seconds to count down\n" RESET, currentColor);

    printf("%s\n=======================================\n\n" RESET, currentColor);
}

void runClock() {
    int lastSec = -1;

    while (1) {
        time_t now = time(NULL);
        struct tm *t = localtime(&now);

        if (t->tm_sec != lastSec) {
            lastSec = t->tm_sec;

            printf("\r%s%02d:%02d:%02d%s  (press q to quit)",
                   currentColor,
                   t->tm_hour,
                   t->tm_min,
                   t->tm_sec,
                   RESET);

            fflush(stdout);
        }

        if (_kbhit()) {
            char ch = _getch();
            if (ch == 'q' || ch == 'Q') {
                printf("\n");
                return;
            }
        }
        Sleep(30);
    }
}


void runStopwatch() {
    clock_t startTime;
    clock_t now;
    double elapsed = 0.0;
    int running = 0;
    char command;

    printf("=== STOPWATCH ===\n");
    printf("s = start/resume | p = pause | t = show time | q = quit\n");

    while (1) {
        printf("Enter command: ");
        scanf(" %c", &command);

        if (command == 's') {
            if (!running) {
                startTime = clock();
                running = 1;
                printf("Started.\n");
            }
        }

        else if (command == 'p') {
            if (running) {
                now = clock();
                elapsed += (double)(now - startTime) / CLOCKS_PER_SEC;
                running = 0;
                printf("Paused.\n");
            }
        }

        else if (command == 't') {
            double total;

            if (running) {
                now = clock();
                total = elapsed + (double)(now - startTime) / CLOCKS_PER_SEC;
            } else {
                total = elapsed;
            }

            printf("Elapsed time: %s%.2f%s seconds\n",
                   currentColor,
                   total,
                   RESET);
        }

        else if (command == 'q') {
            if (running) {
                now = clock();
                elapsed += (double)(now - startTime) / CLOCKS_PER_SEC;
            }

            printf("Final time: %s%.2f%s seconds\n",
                   currentColor,
                   elapsed,
                   RESET);

            while (getchar() != '\n');

            return;
        }

        else {
            printf("Invalid command.\n");
        }
    }
}

void runCountdown() {
    int seconds;

    printf("Enter countdown seconds: ");
    scanf("%d", &seconds);
    while (getchar() != '\n');   // clear buffer

    if (seconds <= 0) {
        printf("Invalid time.\n");
        return;
    }

    printf("Countdown started. Press 'q' to cancel.\n");

    time_t endTime = time(NULL) + seconds;

    int lastShown = -1;

    while (1) {
        time_t now = time(NULL);
        int remaining = (int)difftime(endTime, now);

        if (remaining != lastShown && remaining >= 0) {
            lastShown = remaining;

            printf("\rRemaining: %s%d%s seconds   ",
                   currentColor,
                   remaining,
                   RESET);
            fflush(stdout);
        }

        if (remaining <= 0) {
            printf("\nTIME UP!\n");
            break;
        }

        if (_kbhit()) {
            char ch = _getch();
            if (ch == 'q' || ch == 'Q') {
                printf("\nCountdown cancelled.\n");
                break;
            }
        }

        Sleep(50);
    }
}



void setColor(char *color){

    if(strcmp(color,"yellow")==0) strcpy(currentColor,YELLOW);
    else if(strcmp(color,"blue")==0) strcpy(currentColor,BLUE);
    else if(strcmp(color,"purple")==0) strcpy(currentColor,PURPLE);
    else if(strcmp(color,"cyan")==0) strcpy(currentColor,CYAN);
    else if(strcmp(color,"red")==0) strcpy(currentColor,RED);
    else if(strcmp(color,"green")==0) strcpy(currentColor,GREEN);
    else {
        printf("Unknown color.\n");
        return;
    }

    printf("Color changed to %s%s%s\n",
           currentColor,
           color,
           RESET);
}


void showColors(){
    printf("Available board colors:\n");
    printf("yellow, blue, purple, cyan, red, green\n");
}

int main(){
    char input[100];

    printf("clock\n");
    help();

    while (1) {

        printf("> ");
        fgets(input, 100, stdin);
        input[strcspn(input, "\n")] = 0;

        if (strcmp(input, "/clock") == 0) {
            runClock();
        }

        else if (strcmp(input, "/help") == 0) {
            help();
        }

        else if(strncmp(input,"/color",6)==0){
            if(strlen(input)<=6) showColors();
            else{
                char color[20];
                sscanf(input,"/color %s",color);
                setColor(color);
            }
        }

        else if (strcmp(input, "/stopwatch") == 0) {
            runStopwatch();
        }
        else if (strcmp(input, "/countdown") == 0) {
            runCountdown();
        }

        else if (strcmp(input, "/exit") == 0) {
            break;
        }

        else {
            printf("%sUnknown command\n" RESET, currentColor);
        }
    }

    return 0;
}
