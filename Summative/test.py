def mostRecent(datetime1, datetime2):
    if int(datetime1[:8]) > int(datetime2[:8]):
        return 1
    elif int(datetime1[:8]) < int(datetime2[:8]):
        return 0
    else:
        if int(datetime1[9:15]) >= int(datetime2[9:15]):
            return 1
        else:
            return 0

def latestHun(lst):

    output = []
    
    for x in range(10):
        n = len(lst)
        maxVal = lst[n-1]
          
        for y in range(len(lst)):
            if mostRecent(lst[y], maxVal) == True:
                maxVal = lst[y]; 
                  
        lst.remove(maxVal);

        output.append(maxVal)

    return output
