# coh2balancer
#PL
Działanie:
Projekt mający na celu balansowanie gier wśród znajomych w company of heroes 2
Założene jest proste, dodajemy graczy do pliku cohstats(nazwa edytowalana w zmiennych globalnych), odpalamy main.py
Wybieramy 8 graczy z dropdownów, generujemy teamy. Po wygranej wpisujemy punkty zwycięstwa które miała wygrana drużyna i zaznaczamy kto wygrał. Potwierdzamy. 
Systema automatycznie skoryguje rankingi graczy. 
Kwestie techniczne:
Program można zaadoptować do dowolnej gry komputerowej. Wystarczy przeredagować listę losowanych map, frakcji.
Tworzony domyślnie pod 4v4, w przypadku 3v3 i 2v2 dodać słupy o wartości typu 9999.


#ANG
Functionality:
A project aimed at balancing games among friends in Company of Heroes 2.
The concept is simple: we add players to the cohstats file (the name can be edited in global variables), run main.py, select 8 players from the dropdowns, and generate teams. After a match, we enter the victory points that the winning team had and mark who won. We then confirm the result.
The system will automatically adjust the player rankings.

Technical details:
The program can be adapted to any computer game. It only requires editing the list of maps and factions to be randomized.
The program is designed by default for 4v4 matches; for 3v3 and 2v2, you should add dummy entries with a value of 9999.
