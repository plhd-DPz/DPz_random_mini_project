#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define MAX_YEARS 20
#define MAX_ENTRIES 500
#define NOTE_SIZE 300
#define CELL_WIDTH 12

typedef struct {
    int day;
    int month;
    int marked;
    int rating;
    char note[NOTE_SIZE];
} DayEntry;

typedef struct {
    int year;
    DayEntry entries[MAX_ENTRIES];
    int entryCount;
} YearCalendar;

typedef struct {
    YearCalendar list[MAX_YEARS];
    int count;
} CalendarDB;

CalendarDB db;
YearCalendar *current = NULL;

int isLeap(int y) {
    return (y % 400 == 0) || (y % 4 == 0 && y % 100 != 0);
}

int daysInMonth(int m, int y) {
    int d[] = {31,28,31,30,31,30,31,31,30,31,30,31};
    if (m == 2 && isLeap(y)) return 29;
    return d[m-1];
}

// Zeller weekday: Monday=0 
int weekday(int d, int m, int y) {
    if (m < 3) { m += 12; y--; }
    int k = y % 100;
    int j = y / 100;
    int h = (d + (13*(m+1))/5 + k + k/4 + j/4 + 5*j) % 7;
    int dayIndex = (h + 5) % 7;
    return dayIndex;
}

DayEntry* findEntry(YearCalendar *cal, int d, int m) {
    for (int i = 0; i < cal->entryCount; i++) {
        if (cal->entries[i].day == d && cal->entries[i].month == m)
            return &cal->entries[i];
    }
    return NULL;
}

DayEntry* getOrCreateEntry(YearCalendar *cal, int d, int m) {
    DayEntry *e = findEntry(cal, d, m);
    if (e) return e;

    if (cal->entryCount >= MAX_ENTRIES) return NULL;

    DayEntry *newE = &cal->entries[cal->entryCount++];
    newE->day = d;
    newE->month = m;
    newE->marked = 0;
    newE->rating = 0;
    newE->note[0] = '\0';
    return newE;
}


void saveData() {
    FILE *f = fopen("calendardata.txt", "w");
    if (!f) return;

    fprintf(f, "%d\n", db.count);

    for (int i = 0; i < db.count; i++) {
        YearCalendar *cal = &db.list[i];

        fprintf(f, "YEAR %d %d\n", cal->year, cal->entryCount);

        for (int j = 0; j < cal->entryCount; j++) {
            DayEntry *e = &cal->entries[j];

            fprintf(f, "%d %d %d %d %s\n",
                    e->day, e->month,
                    e->marked, e->rating,
                    e->note);
        }
    }

    fclose(f);
    printf("Data saved.\n");
}

void loadData() {
    FILE *f = fopen("calendardata.txt", "r");

    if (!f) {
        f = fopen("calendardata.txt", "w");
        fclose(f);
        return;
    }

    fscanf(f, "%d\n", &db.count);

    for (int i = 0; i < db.count; i++) {
        YearCalendar *cal = &db.list[i];

        fscanf(f, "YEAR %d %d\n", &cal->year, &cal->entryCount);

        for (int j = 0; j < cal->entryCount; j++) {
            DayEntry *e = &cal->entries[j];

            fscanf(f, "%d %d %d %d ",
                   &e->day, &e->month,
                   &e->marked, &e->rating);

            fgets(e->note, NOTE_SIZE, f);
            e->note[strcspn(e->note, "\n")] = 0;
        }
    }

    fclose(f);
}

/* CALENDAR DISPLAY */

void printCell(YearCalendar *cal, int day, int month) {
    DayEntry *e = findEntry(cal, day, month);

    char cell[60];
    int marked = (e && e->marked);
    int rating = (e) ? e->rating : 0;
    int hasNote = (e && strlen(e->note) > 0);

    if (marked && rating && hasNote)
        sprintf(cell, "%2d*(%d)[N]", day, rating);

    else if (marked && rating)
        sprintf(cell, "%2d*(%d)", day, rating);

    else if (marked && hasNote)
        sprintf(cell, "%2d*[N]", day);

    else if (marked)
        sprintf(cell, "%2d*", day);

    else if (rating && hasNote)
        sprintf(cell, "%2d(%d)[N]", day, rating);

    else if (rating)
        sprintf(cell, "%2d(%d)", day, rating);

    else if (hasNote)
        sprintf(cell, "%2d[N]", day);

    else
        sprintf(cell, "%2d", day);

    printf("%-*s", CELL_WIDTH, cell);
}

void showMonth(YearCalendar *cal, int m) {
    printf("\n===== Month %02d / %d =====\n", m, cal->year);
    printf("Mon         Tue         Wed         Thu         Fri         Sat         Sun\n");

    int first = weekday(1, m, cal->year);
    int total = daysInMonth(m, cal->year);

    for (int i = 0; i < first; i++)
        printf("%-*s", CELL_WIDTH, " ");

    for (int d = 1; d <= total; d++) {
        printCell(cal, d, m);

        if ((first + d) % 7 == 0)
            printf("\n");
    }

    printf("\n");
}

/* COMMAND HELP */

void cmdHelp() {
    printf("\n===== HELP MENU =====\n\n");

    printf("month- MM\n");
    printf("  Example: month- 3\n\n");

    printf("mark- DD/MM\n");
    printf("  Example: mark- 17/3\n\n");

    printf("unmark- DD/MM\n");
    printf("  Example: unmark- 17/3\n\n");

    printf("note- DD/MM\n");
    printf("  Example: note- 14/2\n");
    printf("  Type note text, finish with end-\n\n");

    printf("checknote- DD/MM\n");
    printf("  Example: checknote- 14/2\n\n");

    printf("deletenote- DD/MM\n");
    printf("  Example: deletenote- 14/2\n\n");

    printf("rate- DD/MM SCORE\n");
    printf("  Example: rate- 25/3 10\n\n");

    printf("findnote-\n");
    printf("  Lists all days with notes\n\n");

    printf("listmark-\n");
    printf("  Lists all marked days\n\n");

    printf("switchyear- YYYY\n\n");

    printf("y?-   Show current working year\n\n");

    printf("save-\n\n");

    printf("cleardata-\n");
    printf("  WARNING: deletes ALL data\n\n");

    printf("exit-\n\n");

    printf("SYMBOLS:\n");
    printf("  *    = marked\n");
    printf("  [N]  = note exists\n");
    printf("  (x)  = rating\n");

    printf("======================\n");
}

void cmdMark(int d, int m) {
    DayEntry *e = getOrCreateEntry(current, d, m);
    e->marked = 1;
    printf("Marked %02d/%02d.\n", d, m);
}

void cmdUnmark(int d, int m) {
    DayEntry *e = findEntry(current, d, m);
    if (!e) return;
    e->marked = 0;
    printf("Unmarked %02d/%02d.\n", d, m);
}

void cmdNote(int d, int m) {
    DayEntry *e = getOrCreateEntry(current, d, m);

    printf("Enter note text (end with end-):\n");

    char buffer[NOTE_SIZE] = "";
    char line[200];

    while (1) {
        fgets(line, sizeof(line), stdin);

        if (strncmp(line, "end-", 4) == 0)
            break;

        strcat(buffer, line);
    }

    buffer[strcspn(buffer, "\n")] = 0;
    strcpy(e->note, buffer);

    printf("Note saved for %02d/%02d.\n", d, m);
}

void cmdCheckNote(int d, int m) {
    DayEntry *e = findEntry(current, d, m);

    if (!e || strlen(e->note) == 0) {
        printf("No note found.\n");
        return;
    }

    printf("\nNOTE %02d/%02d:\n%s\n", d, m, e->note);
}

void cmdDeleteNote(int d, int m) {
    DayEntry *e = findEntry(current, d, m);
    if (!e) return;
    e->note[0] = '\0';
    printf("Note deleted.\n");
}

void cmdRate(int d, int m, int score) {
    if (score < 1 || score > 10) {
        printf("Score must be 1-10.\n");
        return;
    }

    DayEntry *e = getOrCreateEntry(current, d, m);
    e->rating = score;
    printf("Rated %02d/%02d = %d.\n", d, m, score);
}

void cmdFindNote() {
    printf("\nDays with notes:\n");

    for (int i = 0; i < current->entryCount; i++) {
        DayEntry *e = &current->entries[i];
        if (strlen(e->note) > 0)
            printf("%02d/%02d\n", e->day, e->month);
    }
}

void cmdListMark() {
    printf("\nMarked days:\n");

    for (int i = 0; i < current->entryCount; i++) {
        DayEntry *e = &current->entries[i];
        if (e->marked)
            printf("%02d/%02d\n", e->day, e->month);
    }
}

void cmdClearData() {
    printf("WARNING: This deletes ALL calendar data. Continue? (Y/N): ");
    char ans[10];
    fgets(ans, sizeof(ans), stdin);

    if (toupper(ans[0]) != 'Y') return;

    FILE *f = fopen("calendardata.txt", "w");
    fclose(f);

    db.count = 0;
    current = NULL;

    printf("All data cleared.\n");
}

// MAIN IS HERE===============================================, just in case XD

int main() {
    db.count = 0;
    loadData();

    if (db.count > 0) {
        printf("\n%d calendars found.\n\n", db.count);

        for (int i = 0; i < db.count; i++)
            printf("(%d) %d\n", i+1, db.list[i].year);

        printf("\nUse existing calendar? (Y/N): ");
        char ans[10];
        fgets(ans, sizeof(ans), stdin);

        if (toupper(ans[0]) == 'Y') {
            printf("Enter year you want to work with: ");
            int choice;
            scanf("%d", &choice);
            getchar();

            current = &db.list[choice-1];
        }
    }

    if (!current) {
        int y;
        printf("Enter start year: ");
        scanf("%d", &y);
        getchar();

        current = &db.list[db.count++];
        current->year = y;
        current->entryCount = 0;
    }

    printf("\nType command- for help.\n");

    char cmd[200];

    while (1) {
        printf("\n> ");
        fgets(cmd, sizeof(cmd), stdin);
        cmd[strcspn(cmd, "\n")] = 0;

        if (strcmp(cmd, "command-") == 0)
            cmdHelp();

        else if (strncmp(cmd, "month-", 6) == 0) {
            int m;
            sscanf(cmd, "month- %d", &m);
            showMonth(current, m);
        }

        else if (strncmp(cmd, "mark-", 5) == 0) {
            int d,m;
            sscanf(cmd, "mark- %d/%d", &d,&m);
            cmdMark(d,m);
        }

        else if (strncmp(cmd, "unmark-", 7) == 0) {
            int d,m;
            sscanf(cmd, "unmark- %d/%d", &d,&m);
            cmdUnmark(d,m);
        }

        else if (strncmp(cmd, "note-", 5) == 0) {
            int d,m;
            sscanf(cmd, "note- %d/%d", &d,&m);
            cmdNote(d,m);
        }

        else if (strncmp(cmd, "checknote-", 10) == 0) {
            int d,m;
            sscanf(cmd, "checknote- %d/%d", &d,&m);
            cmdCheckNote(d,m);
        }

        else if (strncmp(cmd, "deletenote-", 11) == 0) {
            int d,m;
            sscanf(cmd, "deletenote- %d/%d", &d,&m);
            cmdDeleteNote(d,m);
        }

        else if (strncmp(cmd, "rate-", 5) == 0) {
            int d,m,s;
            sscanf(cmd, "rate- %d/%d %d", &d,&m,&s);
            cmdRate(d,m,s);
        }

        else if (strcmp(cmd, "findnote-") == 0)
            cmdFindNote();

        else if (strcmp(cmd, "listmark-") == 0)
            cmdListMark();

        else if (strncmp(cmd, "switchyear-", 11) == 0) {
            int y;
            sscanf(cmd, "switchyear- %d", &y);

            for (int i = 0; i < db.count; i++)
                if (db.list[i].year == y)
                    current = &db.list[i];

            printf("Switched to %d.\n", current->year);
        }

        else if (strcmp(cmd, "y?-") == 0)
            printf("Current year: %d\n", current->year);

        else if (strcmp(cmd, "save-") == 0)
            saveData();

        else if (strcmp(cmd, "cleardata-") == 0)
            cmdClearData();

        else if (strcmp(cmd, "exit-") == 0) {
            saveData();
            printf("Goodbye.\n");
            break;
        }

        else
            printf("Unknown command. Type command- for help.\n");
    }

    return 0;
}
