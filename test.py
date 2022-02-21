from datetime import datetime
from backendService import login, uploadFight
from fight import Fight, Player

# make fake fight object
pw1 = Player('w1', 'w1_name', 'w1_class', 0)
pw2 = Player('w2', 'w2_name', 'w2_class', 0)
pw3 = Player('w3', 'w3_name', 'w3_class', 0)
pw4 = Player('w4', 'w4_name', 'w4_class', 0)
pw5 = Player('w5', 'w5_name', 'w5_class', 0)
pl1 = Player('l1', 'l1_name', 'l1_class', 1)
pl2 = Player('l2', 'l2_name', 'l2_class', 1)
pl3 = Player('l3', 'l3_name', 'l3_class', 1)
pl4 = Player('l4', 'l4_name', 'l4_class', 1)
pl5 = Player('l5', 'l5_name', 'l5_class', 1)
players = (pw1, pw2, pw3, pw4, pw5, pl1, pl2, pl3, pl4, pl5) 
fight = Fight(0, 0, 1234, 5678, datetime.now(), 'fakeFilePath.png', 'w1', players)

# TEST: log into server
# print('---- TEST: log into backend ----')
# login()

# TEST: upload fight to backend
print('---- TEST: upload fight to backend ----')
fightID = uploadFight(fight, upload=False)

if fightID:
    if fightID == 0:
        print(f"some error during upload. Fight was not uploaded!")
    else:
        print(f"fight uploaded with ID={fightID}")
else:
    print(f"some error during upload. Fight was not uploaded!")
