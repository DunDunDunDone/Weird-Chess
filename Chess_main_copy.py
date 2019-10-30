


## These are the steps that need to be followed
## Write out the pairs and singles
## Put the pairs above the single column
## If this is a valid partition, you're done, otherwise
## Shift the stuff below the pairs that are less than (3, 4, 6 ... 2, 5)
##   the greatest left element of the pairs upwards, pushing stuff out as you go
## If there's an issue in the second row, resolve it now by bubbling
##   similar to the first row
## Use gravity up, then left (assuming 3 rows)
## 
## 
## 
## 

## Takes [[1, 1, 2, 3, 4, 5, 5, 8], [2, 3, 4, 6, 6, 7, 7, 8]] <- MOT

## 1  3  6  7
## 2  5
## 4
## Goes to
## 
## [[1, 3, 6, 7], [2, 5], [4]]
##

def bijection(MOT):
    """Takes a list with two sub-lists and transforms it into a SYT with 3 rows"""
    return final_gravity(bubble_two(bubble_one(initial_transform(MOT))))


def initial_transform(MOT): # Verified
    """Transforms a MOT into a pseudo-SYT with pairs and singles"""
    pairs = [[], []]
    singles = []
    top = MOT[0]
    bot = MOT[1]
    for i in range(1, 1+len(top)):
        if i in top and i in bot:
            singles.append(i)
        elif i in top:
            pairs[0].append(i)
        else:
            pairs[1].append(i)

    final = rectify([pairs[0]+singles, pairs[1], []])
    return final

def rectify(SYT): # Verified
    """Turns an SYT into the same SYT with Nones to make it a rect"""
    max_len = max(len(SYT[0]), len(SYT[1]), len(SYT[2]))
    top_row = SYT[0] + [None for i in range(max_len-len(SYT[0]))]
    mid_row = SYT[1] + [None for i in range(max_len-len(SYT[1]))]
    bot_row = SYT[2] + [None for i in range(max_len-len(SYT[2]))]
    return [top_row, mid_row, bot_row]

'''def bubble_one(SYT): # Uses a rectified SYT, verified # Make efficient
    """The first bubbling step that moves the singles up"""
    top_row = SYT[0]
    mid_row = SYT[1]
    bot_row = SYT[2]
    while top_row != sorted(top_row):
        for i, item in enumerate(top_row[:-1]):
            if item > top_row[i+1]: # This means item 1+i is in the wrong place and should be bubbled
                #print(top_row[i+1])
                #print(top_row, mid_row, bot_row)
                new_top_row = SYT[0]
                new_mid_row = SYT[1]
                new_bot_row = SYT[2] # Shifting begins here
                new_bot_row[i] = new_mid_row[i]
                new_mid_row[i] = new_top_row[i]
                new_top_row[i] = new_top_row[i+1]
                new_top_row[i+1] = new_mid_row[i+1]
                new_mid_row[i+1] = new_bot_row[i+1]
                new_bot_row[i+1] = None
                #print(top_row, mid_row, bot_row)
                while None in new_top_row: # Removes Nones from top row and all other rows in equal quantity
                    new_top_row = remove_final(new_top_row, None)
                    new_mid_row = remove_final(new_mid_row, None)
                    new_bot_row = remove_final(new_bot_row, None)
                top_row = new_top_row
                mid_row = new_mid_row
                bot_row = new_bot_row
                #print(top_row, mid_row, bot_row)
                break
    #print([top_row, mid_row, bot_row])
    return [top_row, mid_row, bot_row]'''

def bubble_one(SYT): # Uses a rectified SYT, verified # Made efficient
    """The first bubbling step that moves the singles up"""
    top_row = SYT[0]
    mid_row = SYT[1]
    bot_row = SYT[2]
    while top_row != sorted(top_row):
        for i, item in enumerate(top_row[:-1]):
            if item > top_row[i+1]: # This means item 1+i is in the wrong place and should be bubbled
                #print(top_row[i+1])
                #print(top_row, mid_row, bot_row) # Shifting begins here
                bot_row[i] = mid_row[i]
                mid_row[i] = top_row[i]
                top_row[i] = top_row[i+1]
                top_row[i+1] = mid_row[i+1]
                mid_row[i+1] = bot_row[i+1]
                bot_row[i+1] = None
                #print(top_row, mid_row, bot_row)
                while None in top_row: # Removes Nones from top row and all other rows in equal quantity
                    top_row = remove_final(top_row, None)
                    mid_row = remove_final(mid_row, None)
                    bot_row = remove_final(bot_row, None)
                #print(top_row, mid_row, bot_row)
                break
    #print([top_row, mid_row, bot_row])
    return [top_row, mid_row, bot_row]

def remove_final(array, val): # Make efficient
    """Returns the list where the final instance of val has been removed"""
    array.reverse()
    array.remove(val)
    array.reverse()
    return array

'''def bubble_two(SYT): # Uses a rectified SYT
    """The second bubbling step that fixes row two"""
    
    mid_row = SYT[1]
    bot_row = SYT[2]
    while None in mid_row: # Removes Nones from top row and all other rows in equal quantity
        mid_row = remove_final(mid_row, None)
        bot_row = remove_final(bot_row, None)
    while mid_row != sorted(mid_row):
        for i, item in enumerate(mid_row[:-1]):
            if item > mid_row[i+1]: # This means item 1+i is in the wrong place and should be bubbled
                #print(top_row[i+1])
                #print(top_row, mid_row, bot_row)
                new_mid_row = SYT[1]
                new_bot_row = SYT[2] # Shifting begins here
                new_bot_row[i] = new_mid_row[i]
                new_mid_row[i] = new_mid_row[i+1]
                new_mid_row[i+1] = new_bot_row[i+1]
                new_bot_row[i+1] = None
                #print(top_row, mid_row, bot_row)
                while None in new_mid_row: # Removes Nones from top row and all other rows in equal quantity
                    new_mid_row = remove_final(new_mid_row, None)
                    new_bot_row = remove_final(new_bot_row, None)
                mid_row = new_mid_row
                bot_row = new_bot_row
                #print(top_row, mid_row, bot_row)
                break
    return [SYT[0], mid_row, bot_row]'''

def bubble_two(SYT): # Uses a rectified SYT
    """The second bubbling step that fixes row two"""
    
    mid_row = SYT[1]
    bot_row = SYT[2]
    while None in mid_row: # Removes Nones from top row and all other rows in equal quantity
        mid_row = remove_final(mid_row, None)
        bot_row = remove_final(bot_row, None)
    while mid_row != sorted(mid_row):
        for i, item in enumerate(mid_row[:-1]):
            if item > mid_row[i+1]: # This means item 1+i is in the wrong place and should be bubbled
                #print(top_row[i+1])
                #print(top_row, mid_row, bot_row) # Shifting begins here
                bot_row[i] = mid_row[i]
                mid_row[i] = mid_row[i+1]
                mid_row[i+1] = bot_row[i+1]
                bot_row[i+1] = None
                #print(top_row, mid_row, bot_row)
                while None in mid_row: # Removes Nones from top row and all other rows in equal quantity
                    mid_row = remove_final(mid_row, None)
                    bot_row = remove_final(bot_row, None)
                #print(top_row, mid_row, bot_row)
                break
    return [SYT[0], mid_row, bot_row]

def final_gravity(SYT): # Uses a rectified SYT
    """Does the gravity step to finish the partition""" # Removes all None
    new_SYT = SYT
    while None in new_SYT[0] + new_SYT[1] + new_SYT[2]:
        if None in new_SYT[2]:
            new_SYT[2].remove(None)
        if None in new_SYT[1]:
            new_SYT[1].remove(None)
        if None in new_SYT[0]:
            new_SYT[0].remove(None)
    return new_SYT

def valid_SYT(SYT):
    """Checks is SYT is valid"""
    if not ((sorted(SYT[0]) == SYT[0]) and (sorted(SYT[1]) == SYT[1]) and (sorted(SYT[2]) == SYT[2])): # Checks if rows are sorted
        print(SYT)
        return False
    if len(SYT) != 3: # Checks for 3 or less rows
        print(SYT)
        return False
    for col in felxible_zip(SYT[0], SYT[1], SYT[2]): # Checks if columns are sorted
        if not (list(col) == sorted(col)):
            print(SYT)
            return False
    return True

def felxible_zip(l1, l2, l3):
    """Assumes l1 >= l2 >= l3"""
    while min(len(l1), len(l2), len(l3)) > 0:
        yield (l1.pop(0), l2.pop(0), l3.pop(0))
    while min(len(l1), len(l2)) > 0:
        yield (l1.pop(0), l2.pop(0))
    while len(l1) > 0:
        yield (l1.pop(0),)

def MOT_Gen(size, cur_n = 1, cur_t = [[], []]):
    """Takes size of MOT, number to be added, and the current"""
    if cur_n > size: # We're Done!
        return [cur_t]
    if len(cur_t[0]) == size: # If top row is completed, call again with bigger bottom row
        return MOT_Gen(size, cur_n+1, [cur_t[0], cur_t[1]+[cur_n, cur_n]])
    elif len(cur_t[0])+1 == size: # One away from completion of the top row
        if len(cur_t[1])+1 == size: # One away from bottom row completion?
            return MOT_Gen(size, cur_n+1, [cur_t[0]+[cur_n], cur_t[1]+[cur_n]])
        else:
            return (MOT_Gen(size, cur_n+1, [cur_t[0], cur_t[1]+[cur_n, cur_n]])
                    + MOT_Gen(size, cur_n+1, [cur_t[0]+[cur_n], cur_t[1]+[cur_n]]))
    elif len(cur_t[0])+2 <= size:
        if len(cur_t[0]) == len(cur_t[1]):
            return (MOT_Gen(size, cur_n+1, [cur_t[0]+[cur_n, cur_n], cur_t[1]])
                    + MOT_Gen(size, cur_n+1, [cur_t[0]+[cur_n], cur_t[1]+[cur_n]]))
        elif len(cur_t[0]) >= len(cur_t[1])+2:
            return (MOT_Gen(size, cur_n+1, [cur_t[0]+[cur_n, cur_n], cur_t[1]])
                    + MOT_Gen(size, cur_n+1, [cur_t[0], cur_t[1]+[cur_n, cur_n]])
                    + MOT_Gen(size, cur_n+1, [cur_t[0]+[cur_n], cur_t[1]+[cur_n]]))


def duplicate_checker(lis):
    """Returns True if there's a duplicate"""
    while len(lis) != 0:
        if lis.pop() in lis:
            return True
    return False

def duplicate_checker(lis):
    """Returns True if there's a duplicate""" # runs in O(n*k) time UNLIKE SOME CODE
    seen = set()
    for item in lis:
        tupleitem = deeptupler(item)
        if tupleitem in seen:
            return True
        seen.add(tupleitem)
    return False

def deeptupler(lis): # only for 2d arrays
    total = []
    for item in lis:
        total.append(tuple(item))
    return tuple(total)

#print(MOT_Gen(3))
#print(MOT_Gen(4))
    
##print(bijection([[1, 2, 3],
##                 [1, 2, 3]]))
##
##print(bijection([[1, 2, 3],
##                 [1, 2, 3]]))
##
##print(bijection([[1, 2, 2],
##                 [1, 3, 3]]))
##
##print(bijection([[1, 1, 3],
##                 [2, 2, 3]]))

for i in range(19, 30): # 15 works
    print(i)
    x = [bijection(MOT) for MOT in MOT_Gen(i)]
    print(not duplicate_checker(x))
    y = set()
    for SYT in x:
        y.add(valid_SYT(SYT))
    print(not (False in y))
    

#print(bijection([[1, 1, 2],
#                 [2, 3, 3]]))
