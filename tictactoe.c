#include <stdio.h>
#include <conio.h>
#include <windows.h>
#include <time.h>

#define BLUE 9
#define WHITE 15

char board[3][3];
int cursorX = 0, cursorY = 0;
int currentPlayer = 0; // 0 = X, 1 = O
int gameCount = 0;

void setColor(int color) {
    SetConsoleTextAttribute(GetStdHandle(STD_OUTPUT_HANDLE), color);
}

void clearScreen() {
    system("cls");
}

void initBoard() {
    for (int y = 0; y < 3; y++)
        for (int x = 0; x < 3; x++)
            board[y][x] = ' ';
}

void drawBoard() {
    setColor(BLUE);
    printf("\n");

    for (int y = 0; y < 3; y++) {
        printf("   ");
        for (int x = 0; x < 3; x++) {
            if (cursorX == x && cursorY == y)
                setColor(WHITE);
            else
                setColor(BLUE);

            printf("  %c  ", board[y][x]);

            setColor(BLUE);
            if (x < 2) printf("|");
        }
        printf("\n");

        if (y < 2) {
            printf("   -----+-----+-----\n");
        }
    }
    setColor(WHITE);
}

int checkWin() {
    for (int i = 0; i < 3; i++) {
        if (board[i][0] != ' ' &&
            board[i][0] == board[i][1] &&
            board[i][1] == board[i][2])
            return 1;

        if (board[0][i] != ' ' &&
            board[0][i] == board[1][i] &&
            board[1][i] == board[2][i])
            return 1;
    }

    if (board[0][0] != ' ' &&
        board[0][0] == board[1][1] &&
        board[1][1] == board[2][2])
        return 1;

    if (board[0][2] != ' ' &&
        board[0][2] == board[1][1] &&
        board[1][1] == board[2][0])
        return 1;

    return 0;
}

int isDraw() {
    for (int y = 0; y < 3; y++)
        for (int x = 0; x < 3; x++)
            if (board[y][x] == ' ')
                return 0;
    return 1;
}

void saveLog(const char* result) {
    FILE* f = fopen("game_log.txt", "a");
    if (!f) return;

    fprintf(f, "Game %d: %s\n", gameCount, result);
    fclose(f);
}

void gameLoop() {
    initBoard();
    cursorX = cursorY = 0;
    currentPlayer = 0;
    gameCount++;

    while (1) {
        clearScreen();
        printf("TIC TAC TOE 3x3\n");
        printf("Player %d (%c)\n", currentPlayer + 1,
               currentPlayer == 0 ? 'X' : 'O');
        drawBoard();

        int ch = _getch();

        if (ch == 27) break; // ESC
        if (ch == 224) {
            ch = _getch();
            if (ch == 72 && cursorY > 0) cursorY--;
            if (ch == 80 && cursorY < 2) cursorY++;
            if (ch == 75 && cursorX > 0) cursorX--;
            if (ch == 77 && cursorX < 2) cursorX++;
        } else if (ch == 13) { // ENTER
            if (board[cursorY][cursorX] == ' ') {
                board[cursorY][cursorX] =
                    currentPlayer == 0 ? 'X' : 'O';

                if (checkWin()) {
                    clearScreen();
                    drawBoard();
                    printf("\nPlayer %d WIN!\n", currentPlayer + 1);

                    saveLog(currentPlayer == 0 ? "Winner = X" : "Winner = O");
                    system("pause");
                    return;
                }

                if (isDraw()) {
                    clearScreen();
                    drawBoard();
                    printf("\nDRAW!\n");
                    saveLog("Draw");
                    system("pause");
                    return;
                }

                currentPlayer = 1 - currentPlayer;
            }
        }
    }
}

void startScreen() {
    clearScreen();
    setColor(BLUE);
    printf("\n\n");
    printf("     TIC TAC TOE\n");
    printf("   2 PLAYER - SAME PC\n\n");
    setColor(WHITE);
    printf("   Press ENTER to start\n");
    printf("   Press ESC to quit\n");

    while (1) {
        int ch = _getch();
        if (ch == 13) return;
        if (ch == 27) exit(0);
    }
}

int main() {
    startScreen();

    while (1) {
        gameLoop();
        startScreen();
    }

    return 0;
}
