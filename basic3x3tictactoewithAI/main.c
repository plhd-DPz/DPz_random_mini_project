#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define LOGFILE "logtictactoe.txt"
#define SAVEFILE "tictactoe_save.txt"

char board[3][3];
int gameStarted = 0;
char currentColor[20] = "\033[0m";

/* the following COLOR use ANSI escape, and honestly idk what it is
I copy this part from AI when asked for a portable alternative of SetConsoleTextAttribute()
if you also don't know what it is, better use the part below(only work on window though)

#include <windows.h>
void setColor(int color)
{
    SetConsoleTextAttribute(GetStdHandle(STD_OUTPUT_HANDLE), color);
}
*/
#define RESET   "\033[0m"
#define RED     "\033[31m"
#define GREEN   "\033[32m"
#define YELLOW  "\033[33m"
#define BLUE    "\033[34m"
#define PURPLE  "\033[35m"
#define CYAN    "\033[36m"

/* ===================== AI DIALOG SYSTEM ===================== */
/* ADD NEW SENTENCES INSIDE THESE ARRAYS TO EXPAND AI PERSONALITY */

const char* aiMidGameLines[] = {
    "AI: Interesting choice.",
    "AI: Calculating... maybe.",
    "AI: You sure about that?",
    "AI: Bold move.",
    "AI: Hmmm...",
    "AI: I see your plan.",
    "AI: Suspicious.",
    "AI: That might backfire.",
    "AI: You're thinking too much.",
    "AI: Or not thinking at all."
};

const char* aiWinLines[] = {
    "AI: Beep boop. Victory.",
    "AI: Skill issue detected.",
    "AI: Humans remain predictable.",
    "AI: That was inevitable.",
    "AI: GG.",
    "AI: I was only using 3 percents of my power.",
    "AI: Easy.",
    "AI: Thank you for participating."
};

const char* aiLoseLines[] = {
    "AI: ...This is not over.",
    "AI: I demand a rematch.",
    "AI: That was luck.",
    "AI: My circuits slipped.",
    "AI: I was going easy on you.",
    "AI: System error. Definitely not my fault.",
    "AI: I let you win.",
    "AI: Temporary setback."
};

/* ============================================================ */

int zoomLevel = 100;   // default zoom 100%
int lastMove = 0;

int midCount = sizeof(aiMidGameLines)/sizeof(aiMidGameLines[0]);
int winCount = sizeof(aiWinLines)/sizeof(aiWinLines[0]);
int loseCount = sizeof(aiLoseLines)/sizeof(aiLoseLines[0]);

void help();
void initBoard();
void printBoard();
int checkWin();
int boardFull();
int playerMove(int pos);
void aiMove();
void logResult(char *result);
void showLog();
void clearLog();
void saveGame();
void setColor(char *color);
void showColors();
void aiSpeak(int type);

void help() {
    printf("\n===== COMMAND LIST =====\n");
    printf("/help         : show commands\n");
    printf("/start        : start new game\n");
    printf("/color        : show board color list\n");
    printf("/color name   : change board color\n");
    printf("/log          : show win/loss log\n");
    printf("/clear        : clear log file\n");
    printf("/save         : save current game\n");
    printf("/zoom SIZE    : change board zoom (100 - 500)\n");
    printf("                example: /zoom 150\n");
    printf("/exit         : exit program\n");
    printf("\nGame instructions:\n");
    printf("Type number (1-9) to place X (you are RED)\n");
    printf("AI plays O (GREEN)\n\n");
}

void initBoard() {
    char c = '1';
    for(int i=0;i<3;i++)
        for(int j=0;j<3;j++)
            board[i][j] = c++;
}

void printSymbol(char c){
    if(c=='X') printf(RED "X" RESET);
    else if(c=='O') printf(GREEN "O" RESET);
    else printf("%c", c);
}

void printBoard() {

    int scale = zoomLevel / 100;
    if(scale < 1) scale = 1;

    int cellWidth = 6 * scale;
    int cellHeight = 3 * scale;

    int totalWidth = (cellWidth + 1) * 3 + 1;

    printf("\n");

    for(int i=0;i<totalWidth;i++)
        printf("-");
    printf("\n");

    for(int row=0; row<3; row++){

        for(int h=0; h<cellHeight; h++){

            for(int col=0; col<3; col++){

                printf("%s|", currentColor);

                for(int w=0; w<cellWidth; w++){

                    if(h == cellHeight/2 && w == cellWidth/2){
                        printSymbol(board[row][col]);
                    } else {
                        printf(" ");
                    }
                }

                printf(RESET);
            }

            printf("|\n");
        }

        for(int i=0;i<totalWidth;i++)
            printf("-");
        printf("\n");
    }
}


int checkWin() {
    for(int i=0;i<3;i++) {
        if(board[i][0]==board[i][1] && board[i][1]==board[i][2])
            return board[i][0];
        if(board[0][i]==board[1][i] && board[1][i]==board[2][i])
            return board[0][i];
    }
    if(board[0][0]==board[1][1] && board[1][1]==board[2][2])
        return board[0][0];
    if(board[0][2]==board[1][1] && board[1][1]==board[2][0])
        return board[0][2];
    return 0;
}

int boardFull() {
    for(int i=0;i<3;i++)
        for(int j=0;j<3;j++)
            if(board[i][j] != 'X' && board[i][j] != 'O')
                return 0;
    return 1;
}

int playerMove(int pos) {
    int r = (pos-1)/3;
    int c = (pos-1)%3;

    if(board[r][c] != 'X' && board[r][c] != 'O'){
        board[r][c] = 'X';
        lastMove = pos;
        return 1;
    }
    printf("Invalid move!\n");
    return 0;
}

void aiSpeak(int type){
    if(type==0 && midCount>0)
        printf("%s\n", aiMidGameLines[rand()%midCount]);

    else if(type==1 && winCount>0)
        printf("%s\n", aiWinLines[rand()%winCount]);

    else if(type==2 && loseCount>0)
        printf("%s\n", aiLoseLines[rand()%loseCount]);
}


void aiMove() {

    printf("Your last move: %d\n", lastMove);

        aiSpeak(0);

    // simple logic to try win(actually it work better than I thought)
    for(int i=1;i<=9;i++){
        int r=(i-1)/3, c=(i-1)%3;
        if(board[r][c]!='X' && board[r][c]!='O'){
            char temp = board[r][c];
            board[r][c]='O';
            if(checkWin()=='O') return;
            board[r][c]=temp;
        }
    }

    for(int i=1;i<=9;i++){
        int r=(i-1)/3, c=(i-1)%3;
        if(board[r][c]!='X' && board[r][c]!='O'){
            char temp = board[r][c];
            board[r][c]='X';
            if(checkWin()=='X'){
                board[r][c]='O';
                return;
            }
            board[r][c]=temp;
        }
    }

    int move;
    do{
        move = rand()%9;
    }while(board[move/3][move%3]=='X' || board[move/3][move%3]=='O');

    board[move/3][move%3]='O';
}

void logResult(char *result){

    FILE *f = fopen(LOGFILE,"r");
    int count = 0;
    char line[200];

    if(f){
        while(fgets(line,200,f)) count++;
        fclose(f);
    }

    f = fopen(LOGFILE,"a");
    if(!f) return;

    fprintf(f,"Game %d: %s\n", count+1, result);
    fclose(f);
}

void showLog(){
    FILE *f=fopen(LOGFILE,"r");
    if(!f){
        printf("No log found.\n");
        return;
    }

    char line[200];
    int win=0, loss=0, draw=0;

    while(fgets(line,200,f)){
        printf("%s",line);

        if(strstr(line,"WIN")) win++;
        else if(strstr(line,"LOSS")) loss++;
        else if(strstr(line,"DRAW")) draw++;
    }

    fclose(f);

    printf("\n===== TOTAL STATS =====\n");
    printf("Wins  : %d\n", win);
    printf("Losses: %d\n", loss);
    printf("Draws : %d\n", draw);
    printf("=======================\n");
}

void clearLog(){
    FILE *f=fopen(LOGFILE,"w");
    fclose(f);
    printf("Log cleared.\n");
}

void saveGame(){
    if(!gameStarted){
        printf("No game to save.\n");
        return;
    }
    FILE *f=fopen(SAVEFILE,"w");
    for(int i=0;i<3;i++)
        for(int j=0;j<3;j++)
            fprintf(f,"%c",board[i][j]);
    fclose(f);
    printf("Game saved.\n");
}

void setColor(char *color){
    if(strcmp(color,"yellow")==0) strcpy(currentColor,YELLOW);
    else if(strcmp(color,"blue")==0) strcpy(currentColor,BLUE);
    else if(strcmp(color,"purple")==0) strcpy(currentColor,PURPLE);
    else if(strcmp(color,"cyan")==0) strcpy(currentColor,CYAN);
    else printf("Unknown color.\n");
}

void showColors(){
    printf("Available board colors:\n");
    printf("yellow, blue, purple, cyan\n");
    printf("(X always red, O always green)\n");
}

int main(){
    srand(time(NULL));
    char input[100];

    help();

    while(1){
        printf("> ");
        fgets(input,100,stdin);
        input[strcspn(input,"\n")] = 0;

        if(strcmp(input,"/help")==0) help();

        else if(strcmp(input,"/start")==0){
            initBoard();
            gameStarted=1;
            printf("Game started!\n");
            printBoard();
        }

        else if(strncmp(input,"/zoom",5)==0){
            int size;
            if(sscanf(input,"/zoom %d",&size)==1){
                if(size < 100){
                    printf("Zoom must be at least 100.\n");
                } else if (size > 500){
                    printf("Zoom must not be higher than 500.\n");
                } else {
                    zoomLevel = size;
                    printf("Zoom set to %d%%\n", zoomLevel);
                }
            } else {
                printf("Usage: /zoom 150\n");
            }
        }

        else if(strcmp(input,"/exit")==0) break;
        else if(strcmp(input,"/log")==0) showLog();
        else if(strcmp(input,"/clear")==0) clearLog();
        else if(strcmp(input,"/save")==0) saveGame();

        else if(strncmp(input,"/color",6)==0){
            if(strlen(input)<=6) showColors();
            else{
                char color[20];
                sscanf(input,"/color %s",color);
                setColor(color);
            }
        }

        else if(gameStarted && strlen(input)==1 && input[0]>='1' && input[0]<='9'){
            int pos=input[0]-'0';

            if(!playerMove(pos)) continue;

            if(checkWin()=='X'){
                printBoard();
                printf("You WIN!\n");
                aiSpeak(2);
                logResult("WIN");
                gameStarted=0;
                continue;
            }

            if(boardFull()){
                printBoard();
                printf("DRAW!\n");
                logResult("DRAW");
                gameStarted=0;
                continue;
            }

            aiMove();

            if(checkWin()=='O'){
                printBoard();
                printf("AI WINS!\n");
                aiSpeak(1);
                logResult("LOSS");
                gameStarted=0;
                continue;
            }

            printBoard();
        }

        else{
            printf("Unknown command. Type /help\n");
        }
    }

    return 0;
}

