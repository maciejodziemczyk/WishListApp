import sqlite3 as sql
import pandas as pd
import ast
from difflib import get_close_matches
conn = sql.connect("wishlist.db")
c = conn.cursor()
# **********************************************************************************************************************
#                                          REGISTER FUNCTION
# **********************************************************************************************************************
def register():
    flag = 0
    while flag == 0:

        # user's input
        login = input("Enter your login: ")
        password = input("Enter your password: ")
        password1 = input("Confirm your password: ")
        while password != password1:
            print("Your password aren't the same.")
            password = input("Enter your password: ")
            password1 = input("Confirm your password: ")
        email = input("Enter your e-mail address: ")
        # email error handling
        while not (
                email.find("@") > -1 and email.find('.', email.find("@")) > -1 and email.find('.', email.find("@")) > (
                email.find("@") + 1)):
            print("Wrong e-mail format")
            email = input("Enter your e-mail adress: ")

        # database connection
        conn = sql.connect("wishlist.db")
        c = conn.cursor()

        # checking if login is taken
        c.execute("SELECT * FROM users WHERE login = ? OR email = ?", (login, email))
        if c.fetchall():
            print("Login or e-mail is taken, try again")
        else:
            flag = 1

    # user's input
    name = input("Enter your name: ")
    surname = input("Enter your surname: ")
    zip_code = input("Enter your zip code: ")
    # error handling
    while not (len(zip_code) == 6 and zip_code[2] == "-"):
        print("Wrong zip code format")
        zip_code = input("Enter your zip code: ")
    city = input("Enter your city: ")
    street = input("Enter your street: ")
    number = input("Enter your house number: ")


    # inserting data to database
    c.execute("INSERT INTO adress VALUES (?, ?, ?, ?, ?)", (None, zip_code, city, street, number))
    c.execute("SELECT adress_id FROM adress ORDER BY adress_id DESC LIMIT 1")
    max_adress_id = c.fetchall()[0]
    c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)",
              (None, login, password, email, name, surname, max_adress_id[0]))

    # looking for function returns
    c.execute("SELECT user_id FROM users WHERE login = ?", (login,))
    user_id = c.fetchall()[0]

    # closing connection
    conn.commit()
    conn.close()
    return user_id
# **********************************************************************************************************************
#                                          LOGIN FUNCTION
# **********************************************************************************************************************
def login():
    while True:
        # user's input
        userLogin = input("Login: ")
        #userEmail = input("e-mail: ")
        userPassword = input("Password: ")


        # database connection
        conn = sql.connect("wishlist.db")
        c = conn.cursor()

        # Authorization
        #c.execute("SELECT * FROM users WHERE password = ? AND (login = ? or email = ?)", (userPassword, userLogin, userEmail))
        c.execute("SELECT * FROM users WHERE password = ? AND login = ?", (userPassword, userLogin))
        user = c.fetchall()
        if user:
            user = user[0] # because it was list of tuples
            print("\nWelcome {}".format(user[4]))
            c.execute("SELECT user_id FROM users WHERE login = ?", (userLogin,))
            user_id = c.fetchall()[0]
#            os.system("choice.py")
            break
        else:
            print("Login or password not recognized!")
            choice = input("Would you like to try again? (Y/N): ")
            if choice.lower() == "n":
                break

    return user_id
# **********************************************************************************************************************
#                                          LIST ADDING FUNCTION
# **********************************************************************************************************************
def addList():

    global wishListDF
    # database connection
    conn = sql.connect("wishlist.db")
    c = conn.cursor()

    # users's input
    wishes = []
    item = 0
    while str(item).lower() != "s":
        item = input("Enter your dream here (if you want to stop press 'S'): ")
        wishes.append(item) if item.lower() != "s" else print("")

    if len(wishes) > 0:
        c.execute("INSERT INTO wishlists VALUES (?, ?, ?)", (None, user_id, str(wishes)))
        print("Wishlist added successfully!\n")

        c.execute("SELECT wishlist_id FROM wishlists WHERE wish=? AND  user_id=?",(str(wishes), user_id))
        ID = c.fetchall()[0][0]
        data = {'wishlistID': int(ID), 'wishes': wishes}
        wishListDF=pd.DataFrame.append(wishListDF,data,ignore_index=True)
        wishListDF.to_csv('wishListDF.csv', index=False)
    #print(wishListDF)
    # closing connection
    conn.commit()
    conn.close()
# **********************************************************************************************************************
#                                          LIST UPDATING FUNCTION
# **********************************************************************************************************************
def updateList(wishlist_id):

    global wishListDF
    # database connection
    conn = sql.connect("wishlist.db")
    c = conn.cursor()

    # users's input
    c.execute("SELECT wish FROM wishlists WHERE wishlist_id = ?", (wishlist_id,))
    user_lists = c.fetchall()
    wish = transform(user_lists)[0]
    print(wish)
    wishDict = {}
    i = 0
    for w in wish:
        i += 1
        wishDict.update({i: w})

    while True:
        if not wishDict:
            c.execute("DELETE FROM wishlists WHERE wishlist_id = ?", (wishlist_id, ))
        for k, v in wishDict.items():
            print("{}. {}".format(k, v))
        new = input("Which wish you want to delete ('S' to stop): ")
        try:
            new = int(new)
            if (new <= len(wishDict)) and (new >= 0): #BYŁA ZMIANA - SPRAWDZIĆ
                wishDict.pop(int(new))
            else:
                choice = input("One of displayed integer should be entered ('S' to stop): ")
                if choice.lower() == 's':
                    break
        except:
            if new.lower() == 's':
                break
            choice = input("One of displayed integer should be entered, ('S' to stop): ")
            if choice.lower() == 's':
                break
    while True:
        for k, v in wishDict.items():
            print("{}. {}".format(k, v))
        new = input("Enter your next dream here ('S' to stop): ")
        if new.lower() == "s":
            break
        else:
            if new != "":
                i = max(wishDict.keys())+1
                wishDict.update({i: new})
            else:
                pass

    wishes = list(wishDict.values())
    c.execute("UPDATE wishlists SET wish = ? WHERE wishlist_id = ?", (str(wishes), wishlist_id))
    print("Wishlist updated successfully!\n")

    #closing connection
    conn.commit()
    conn.close()

    ID = wishlist_id
    wishListDF.loc[(wishListDF.wishlistID == int(ID)),'wishes']=str(wishes)
    wishListDF.to_csv('wishListDF.csv', index=False)
# **********************************************************************************************************************
#                                          LIST DELETING FUNCTION
# **********************************************************************************************************************
def deleteList(wishlist_id):

    # database connection
    conn = sql.connect("wishlist.db")
    c = conn.cursor()

    c.execute("DELETE FROM wishlists WHERE wishlist_id = ?", (wishlist_id,))
    print("Delete successful!\n")

    # closing connection
    conn.commit()
    conn.close()
# **********************************************************************************************************************
#                                          WISH TRANSFORM FUNCTION
# **********************************************************************************************************************
def transform(user_lists):
    premierlist = []
    for Lst in user_lists:

        Lst = Lst[0]
        Lst = Lst[1:-1]

        newlist = Lst.split(sep=",")
        helplist = []
        for item in newlist:
            if item[0] == " ":
                item = item[2:-1]
            else:
                item = item[1:-1]
            helplist.append(item)
        newlist = list(helplist)
        premierlist.append(helplist)

    return premierlist
# **********************************************************************************************************************
#                                          GROUP ADDING FUNCTION
# **********************************************************************************************************************
def addGroup(user_id):

    # database connection
    conn = sql.connect("wishlist.db")
    c = conn.cursor()

    # users's input
    while True:
        group_name = input("Group creating menu.\nEnter group name ('S' to stop): ")
        if group_name.lower() != "s" and group_name.lower() != "":
            c.execute("INSERT INTO groups VALUES (?, ?)", (None, group_name))
            c.execute("SELECT group_id FROM groups ORDER BY group_id DESC LIMIT 1")
            group_id = c.fetchall()[0][0]

            print("Your lists:")
            c.execute("SELECT wish FROM wishlists WHERE user_id=?", (user_id,))
            result = c.fetchall()
            wishesDict = {}
            i = 0
            for r in result:
                i += 1
                r = r[0]
                wishesDict.update({i: r})
            for k, v in wishesDict.items():
                print("{}. {}".format(k, v))
            while True:
                new = input("Which one you want to add to this group ('R' to return): ")
                if not str(new).lower() == "r":
                    try:
                        new = int(new)
                        if new in list(wishesDict.keys()):
                            wishlist = wishesDict.get(new)
                            c.execute("SELECT wishlist_id FROM wishlists WHERE wish = ? AND user_id = ?", (str(wishlist), user_id))
                            wishlist_id = c.fetchall()[0][0]
                            # Walidacja
                            c.execute("SELECT connection_id, group_id FROM connections WHERE\
                            wishlist_id = ?", (wishlist_id,))  # połączenie i grupa gdzie jest konkretna wishlista JEST JEŻELI TA LISTA MA POŁĄCZENIE
                            listChecing = c.fetchall()
                            c.execute("SELECT c.connection_id FROM connections c INNER JOIN wishlists w on c.wishlist_id =\
                            w.wishlist_id INNER JOIN users u on w.user_id = u.user_id WHERE c.group_id = ? AND u.user_id\
                            = ?", (group_id, user_id))  # CZY JA MAM POŁĄCZENIE DO TEJ GRUPY
                            userChecking = c.fetchall()
                            if listChecing or userChecking:  # JEŻELI LISTA MA POŁĄCZENIE ALBO JA JESTEM W TEJ GRUPIE
                                if listChecing and not userChecking:  # JEŻELI TA LISTA MA POŁĄCZENIE A JA NIE JESTEM W TEJ GRUPIE
                                    c.execute("SELECT g.group_name FROM groups g INNER JOIN connections c on\
                                    g.group_id = c.group_id WHERE c.wishlist_id = ?", (wishlist_id,))
                                    assignedGroup = c.fetchall()[0][0]
                                    print('This wishlist has been assigned to group "{}" before.'.format(assignedGroup))
                                    listChecing.clear()
                                    continue
                                elif userChecking and not listChecing:  # JEŻELI TA LISTA NIE MA POŁĄCZENIA A JA JESTEM W TEJ GRUPIE
                                    c.execute("SELECT w.wish FROM wishlists w INNER JOIN connections c on \
                                    w.wishlist_id = c.wishlist_id WHERE c.group_id = ?", (group_id,))
                                    assignedList = c.fetchall()[0][0]
                                    print("You have added {} to this group already!".format(assignedList))
                                    userChecking.clear()
                                    continue
                                else:
                                    c.execute("SELECT g.group_name FROM groups g INNER JOIN connections c on\
                                    g.group_id = c.group_id WHERE c.wishlist_id = ?", (wishlist_id,))
                                    assignedGroup = c.fetchall()[0][0]
                                    c.execute("SELECT w.wish FROM wishlists w INNER JOIN connections c on \
                                    w.wishlist_id = c.wishlist_id WHERE c.group_id = ?", (group_id,))
                                    assignedList = c.fetchall()[0][0]
                                    print(
                                        'This list is in "{}" group and you have added {} to this group already!.'.format(
                                            assignedGroup, assignedList))  # lista ma jakiekolwiek połączenie a ja jestem w tej grupie
                                    continue
                            else:
                                c.execute("INSERT INTO connections VALUES (?, ?, ?)", (None, group_id, wishlist_id))
                                conn.commit()
                                #print("Done")
                                print("Group #{} '{}' added succesfully!".format(group_id, group_name))
                            break
                            # Koniec walidacji
                        else:
                            print("Choosen list doesn't exist. Try again")
                            continue
                    except:
                        print("You should to enter an integer!")
                        continue
                else:
                    break
        elif group_name.lower() == "":
            print("Group name should have one character at least")
            continue
        else:
            break
        break
    conn.close()
# **********************************************************************************************************************
#                                          GROUP JOINING FUNCTION
# **********************************************************************************************************************
def joinGroup(user_id):

    # database connection
    conn = sql.connect("wishlist.db")
    c = conn.cursor()

    # users's input

    while True:
        group_name = input("Group joining menu.\nEnter name of the group you want to join ('S' to stop): ")
        if group_name.lower() != "s" and group_name.lower() != "":
            # c.execute("INSERT INTO groups VALUES (?, ?)", (None, group_name))
            c.execute("SELECT group_id FROM groups WHERE group_name = ?", (group_name, ))
            group_id = c.fetchall()

            if not group_id:
                c.execute("SELECT group_name FROM groups")
                results = c.fetchall()
                names = [result[0] for result in results]
                similar = get_close_matches(group_name, names, cutoff=0.6)
                if similar:
                    yn = input('Did you mean "{}" instead? [Y] - yes: '.format(similar[0]))
                    if yn.lower() == "y":
                        group_name = similar[0]
                        c.execute("SELECT group_id FROM groups WHERE group_name = ?", (group_name, ))
                        group_id = c.fetchall()[0][0]
                    else:
                        continue
                else:
                    print("Entered group doesn't exist!.")
                    continue
            else:
                group_id = group_id[0][0]

            print("Your lists:")
            c.execute("SELECT wish FROM wishlists WHERE user_id = ?", (user_id, ))
            result = c.fetchall()
            wishesDict = {}
            i = 0
            for r in result:
                i += 1
                r = r[0]
                wishesDict.update({i: r})
            for k, v in wishesDict.items():
                print("{}. {}".format(k, v))
            while True:
                new = input("Which one you want to add to this group ('S' to stop): ")
                if not str(new).lower() == "s":
                    try:
                        new = int(new)
                        if new in list(wishesDict.keys()):
                            wishlist = wishesDict.get(new)
                            c.execute("SELECT wishlist_id FROM wishlists WHERE wish = ? AND user_id = ?",
                                      (str(wishlist), user_id))
                            wishlist_id = c.fetchall()[0][0]
                            # Walidacja
                            c.execute("SELECT connection_id, group_id FROM connections WHERE\
                             wishlist_id = ?", (wishlist_id, ))  # połączenie i grupa gdzie jest konkretna wishlista JEST JEŻELI TA LISTA MA POŁĄCZENIE
                            listChecing = c.fetchall()
                            c.execute("SELECT c.connection_id FROM connections c INNER JOIN wishlists w on c.wishlist_id =\
                             w.wishlist_id INNER JOIN users u on w.user_id = u.user_id WHERE c.group_id = ? AND u.user_id\
                              = ?", (group_id, user_id))  # CZY JA MAM POŁĄCZENIE DO TEJ GRUPY
                            userChecking = c.fetchall()
                            if listChecing or userChecking:  # JEŻELI LISTA MA POŁĄCZENIE ALBO JA JESTEM W TEJ GRUPIE
                                if listChecing and not userChecking:  # JEŻELI TA LISTA MA POŁĄCZENIE A JA NIE JESTEM W TEJ GRUPIE
                                    c.execute("SELECT g.group_name FROM groups g INNER JOIN connections c on\
                                    g.group_id = c.group_id WHERE c.wishlist_id = ?", (wishlist_id, ))
                                    assignedGroup = c.fetchall()[0][0]
                                    print('This wishlist has been assigned to group "{}" before.'.format(assignedGroup))
                                    listChecing.clear()
                                    continue
                                elif userChecking and not listChecing:  # JEŻELI TA LISTA NIE MA POŁĄCZENIA A JA JESTEM W TEJ GRUPIE
                                    c.execute("SELECT w.wish FROM wishlists w INNER JOIN connections c on \
                                    w.wishlist_id = c.wishlist_id WHERE c.group_id = ?", (group_id, ))
                                    assignedList = c.fetchall()[0][0]
                                    print("You have added {} to this group already!".format(assignedList))
                                    userChecking.clear()
                                    continue
                                else:
                                    c.execute("SELECT g.group_name FROM groups g INNER JOIN connections c on\
                                    g.group_id = c.group_id WHERE c.wishlist_id = ?", (wishlist_id,))
                                    assignedGroup = c.fetchall()[0][0]
                                    c.execute("SELECT w.wish FROM wishlists w INNER JOIN connections c on \
                                    w.wishlist_id = c.wishlist_id WHERE c.group_id = ?", (group_id,))
                                    assignedList = c.fetchall()[0][0]
                                    print('This list is in "{}" group and you have added {} to this group already!'.format(assignedGroup, assignedList)) # lista ma jakiekolwiek połączenie a ja jestem w tej grupie
                                    continue
                            else:
                                c.execute("INSERT INTO connections VALUES (?, ?, ?)", (None, group_id, wishlist_id))
                                conn.commit()
                                #print("Done")
                                print("Group #{} '{}' joined successfully!".format(group_id, group_name))
                            break
                            # Koniec walidacji
                        else:
                            print("Choosen list doesn't exist. Try again")
                            continue
                    except:
                        print("You should enter an integer!")
                        continue
                else:
                    break  # koniec wybierania list 's'
        elif group_name.lower() == "":
            print("Group name should have at least one character!")
            continue
        else:
            break

    conn.close()

    # -----------------------------------------------------------------------------------------------------

# **********************************************************************************************************************
#                                          GROUP VIEWING FUNCTION
# **********************************************************************************************************************
def viewGroup(user_id):

    # database connection
    conn = sql.connect("wishlist.db")
    c = conn.cursor()
    print("Group viewing menu.\nYour groups:")
    c.execute("SELECT g.group_id, g.group_name FROM groups g INNER JOIN connections c on g.group_id = c.group_id\
     INNER JOIN wishlists w on c.wishlist_id = w.wishlist_id INNER JOIN users u on w.user_id = u.user_id\
      WHERE u.user_id = ?", (user_id, ))
    result = c.fetchall()
    for r in result:
        print(r[0], r[1])

    # users's input
    while True:
        group_choice = input("\nWhich group you want to open ('R' to return): ")  # dotąd jest okej
        if group_choice.lower() == "r":
            break
       # elif group_choice == a:
       #     print("hello")
        else:
            flag = 0
            for r in result:
                if group_choice == str(r[0]):
                    flag = 1
                    break
                else:
                    continue
            if flag == 1:
                c.execute("SELECT connection_id FROM connections WHERE group_id = ?", (group_choice, ))
                choosenGroup = c.fetchall()
                c.execute("SELECT u.name, u.surname, w.wish FROM users u INNER JOIN wishlists w on u.user_id = w.user_id \
                INNER JOIN connections c on w.wishlist_id = c.wishlist_id WHERE c.group_id = ?", (group_choice, ))
                groups = c.fetchall()
                #while True:
                for g in groups:
                    print("\n{} {}".format(g[0], g[1]))
                    groupLists = ast.literal_eval(g[2])
                    for d in groupLists:
                        print(d)

                insideGroup = input("\nTo select wish press 'S', to leave group press 'L' ('R' to return): ")

                if insideGroup.lower() == "s":
                    selectWish(group_choice)
                    break
                elif insideGroup.lower() == "l":
                    leaveGroup(choosenGroup)
                    break
                elif insideGroup.lower() == "r":
                    viewGroup(user_id)
                    break
                else:
                    print("Couldn't recognize your answer!")
                    viewGroup(user_id)
                    continue

            else:
                print("You have to enter one of values printed above")
    conn.close()

def leaveGroup(choosenGroup):
    confirm=input("\nAre you sure you want to leave this group? Y/N: ")
    if confirm.lower() == "y":

        # database connection
        conn = sql.connect("wishlist.db")
        c = conn.cursor()

        c.execute("DELETE FROM connections WHERE connection_id = ?", (choosenGroup[0]))
        print("\nYou left group successfully\n")

        # closing connection
        conn.commit()
        conn.close()

    elif confirm.lower() == "n":
        viewGroup(user_id)
    else:
        print("Couldn't recognize your answer!")
        viewGroup(user_id)

def selectWish(group_choice):
    #global wishListDF
    c.execute("SELECT u.name, u.surname, w.wish, w.wishlist_id FROM users u INNER JOIN wishlists w on u.user_id = w.user_id \
    INNER JOIN connections c on w.wishlist_id = c.wishlist_id WHERE c.group_id = ?", (group_choice, ))
    groups = c.fetchall()
    #while True:
    print("")
    while True:
        for g in groups:
            print("#{} {} {}".format(g[3], g[0], g[1]))

        whose = input("\nIn which list you want to select wish ('R' to return): ")
        if whose.lower() == "r":
            break
        c.execute("SELECT u.name, u.surname, w.wish, w.wishlist_id, u.user_id FROM users u INNER JOIN wishlists w on u.user_id = w.user_id \
        INNER JOIN connections c on w.wishlist_id = c.wishlist_id WHERE c.wishlist_id = ?", (whose, ))
        selection=c.fetchall()
        if selection:
            if selection[0][4] != user_id:
                while True:
                    wishListDF = pd.read_csv('wishListDF.csv')
                    wishListDF.drop(wishListDF.columns[wishListDF.columns.str.contains('unnamed', case=False)], axis=1,
                                    inplace=True)
                    wishListDF = wishListDF[['wishlistID', 'wishes']]
                    wishListDF["wishlistID"] = wishListDF["wishlistID"].astype(int)
                    print("\n#{} {}'s {} wishlist:".format(selection[0][3], selection[0][0], selection[0][1]))

                    selectedWish = wishListDF[wishListDF.wishlistID == selection[0][3]]
                    wishesList=ast.literal_eval(selectedWish.iat[0,1])
                    for i, w in enumerate(wishesList):
                        print("{}. {}".format(i+1,w))

                    wishSelection = input("\nWhich wish you want to select ('R' to return): ")
                    if wishSelection.lower() == "r":
                        break
                    try:
                        wishSelection = int(wishSelection)
                    except :
                        continue

                    if (isinstance(wishSelection, int)) and (wishSelection > 0) and (wishSelection <= len(wishesList)):
                        tempAWish=ast.literal_eval(selectedWish.iat[0,1])
                        aWish=tempAWish[int(wishSelection)-1]
                        if aWish[0]=="(" and aWish[-1]==")":
                            print("\nThis wish is already selected!\n")
                            # tutaj break(?) jak juz bedzie zapetlone, zeby cofalo to wyboru wishow
                            # chociaz na teraz cofa do menu group w ostate cznosci moze zostac
                        else:
                            print("\n{}\n".format(aWish))
                            answer = input("Are you sure that you want select that wish (Y/N)?: ")
                            if answer.lower() == "y":
                                aWish="({})".format(aWish)

                                wishesList[int(wishSelection)-1]=aWish
                                i=wishListDF.loc[wishListDF.wishlistID == selection[0][3]].index.values
                                wishListDF.at[i[0], 'wishes'] = wishesList

                                wishListDF.to_csv('wishListDF.csv', index=False)
                                print("\nWish selected successfully\n")
                                break
                            #break
                    else:
                        print("\nYou have to enter one of index values printed above!")

            else:
                print("\nYou can't select wish from your own wishlist!\n")
        else:
            print("\nYou have to enter one of values printed above!\n")


# **********************************************************************************************************************
# ---------------------------------------MAIN PART---------------------------------------------------------------------
user_id = []
print("***** WISHLIST APP *****")
#przed pierwszym uruchomieniem (jesli nie ma pliku .csv) nalezy odkomentowac linijke nizej i skomentowac cztery kolejne
#wishListDF = pd.DataFrame ()
wishListDF = pd.read_csv('wishListDF.csv')
wishListDF.drop(wishListDF.columns[wishListDF.columns.str.contains('unnamed',case = False)],axis = 1, inplace = True)
wishListDF = wishListDF[['wishlistID','wishes']]
wishListDF["wishlistID"] = wishListDF["wishlistID"].astype(int)

while True:
    choose = input("\nTo login press 'L', to register press 'R': ")
    if choose.lower() == "l":
        print("\nLogging in\n")
        try:
            user_id = login()[0]
        except:
            print("Bye!")
        break
    elif choose.lower() == "r":
        print("\nRegister\n")
        register()
        print("\nLogging in\n")
        user_id = login()[0]
        break
    else:
        print("\nCouldn't recognize your answer!")
        wybor = input("To quit press 'Q', to try again press any other key.")
        if wybor.lower() == "q":
            break
# ---------------------------------------CHOICE PART------------------------------------------------------------------
if user_id:
    while True:
        choose = input("\nWishlists press 'L' Groups - 'G' ('Q' to quit): ")
        if choose.lower() == "l":
            print("\nLists")
            while True:
                choose = input("To add list press 'A', to view existing lists press 'V' ('R' to return): ")
                if choose.lower() == "a":
                    print("\nAdd new list")
                    addList()
                    #break
                elif choose.lower() == "v":
                    print("\nView existing lists")
                    c.execute("SELECT wish FROM wishlists WHERE user_id = ?", (user_id,))
                    user_lists = c.fetchall()
                    i = 0
                    wishes = transform(user_lists)
                    if wishes:
                        for wish in wishes:
                            i += 1
                            print("\nList {}".format(i))
                            print(wish)
                        choose = input("\nTo edit existing list press 'E',to delete existing list press 'D' ('R' to return): ")
                        if choose.lower() == "e" or choose.lower() == "d":
                            if choose.lower() == "e":
                                choosenList = input("Choose list you want to edit ('S' to stop): ")
                            else:
                                choosenList = input("Choose list you want to delete: ('S' to stop): ")
                            while True: # pętla wyboru list do edycji
                                if not str(choosenList).lower() == "s":
                                    try:
                                        choosenList = int(choosenList)
                                        if choosenList in range(1, len(wishes)+1):
                                            choosenList = wishes[int(choosenList) - 1]
                                            c.execute("SELECT wishlist_id FROM wishlists WHERE wish = ?",
                                                      (str(choosenList),))
                                            wish_id = c.fetchone()[0]
                                            if choose.lower() == "e":
                                                updateList(wish_id)
                                            else:
                                                deleteList(wish_id)
                                            break # koniec pętli wyboru listy do edycji
                                        else:
                                            choosenList = input("Choosen list doesn't exist. Try again ('S' to stop): ")
                                            continue
                                    except:
                                        choosenList = input("Choosen list doesn't exist. Try again ('S' to stop): ")
                                        continue
                                else:
                                    print("")
                                    break # koniec pętli wyboru listy do edycji
                            continue
                        elif choose.lower() == "r":
                            continue
                        else:
                            print("Couldn't recognize your answer!")
                            continue
                    else:
                        print("No wishlists found!")
                        continue
                elif choose.lower() == "r":
                    break
                else:
                    print("Couldn't recognize your answer!")
                    continue
            #print("Pomyślne zakończenie menu List")
#            break
        elif choose.lower() == 'g':
            print("\nGroups")
            while True:
                choose = input("Create group 'C', Join existing group 'J', View your groups 'V' ('R' to return): ")
                if choose.lower() == "c":
                    print("Create new group")
                    addGroup(user_id)
                    #break
                elif choose.lower() == "j":
                    joinGroup(user_id)
                    #break
                elif choose.lower() == "v":
                    c.execute("SELECT c.connection_id FROM connections c INNER JOIN wishlists w on c.wishlist_id =\
                    w.wishlist_id INNER JOIN users u on w.user_id = u.user_id WHERE u.user_id\
                    = ?", (user_id,))  # CZY JEST POŁĄCZENIE DO JAKIEJŚ GRUPY
                    isGroup = c.fetchall()
                    if isGroup:
                        c.execute("SELECT c.connection_id FROM connections c INNER JOIN wishlists w on c.wishlist_id =\
                                            w.wishlist_id INNER JOIN users u on w.user_id = u.user_id WHERE u.user_id\
                                            != ?", (user_id,))  # CZY W TEJ GRUPIE JEST KTOŚ JESZCZE
                        otherUser = c.fetchall()
                        if otherUser:
                            #print("Your groups:")
                            viewGroup(user_id)
                        else:
                            print("No other users in this group!")
                    else:
                        print("\nYou haven't got any groups!")

                    '''while True:
                        go = input("View your groups ('Q' to quit): ")
                        if go.lower() == "q":
                            break
                        else:
                            viewGroup(user_id)
                            break
                        #break'''
                elif choose.lower() == "r":
                    break
                else:
                    print("Couldn't recognize your answer!")
                    continue
                    #wybor = input("To quit press 'Q': ")
                    #if wybor.lower() == "q":
                    #    break
            continue  # wraca do pytania Listy czy Grupy?
        elif choose.lower() == "q":
            print("\nBye!\n")
            break
        else:
            print("Couldn't recognize your answer!")
            continue
