from datetime import datetime

def timeBasedData(deptTimeRange, arrivalTimeRange, data):
    """This function filters the query set according to the time data entered by the user

    Args:
        deptTimeRange (time): departure time range. for eg "00:00-06:00"
        arrivalTimeRange (time): arrival time range. 
        data (queryset): queryset containing the record based on the source and destination

    Returns:
        queryset: returns an updated queryset on the basis of the time data entered
    """
    if deptTimeRange and arrivalTimeRange:
        startDeptTime, endDeptTime = map(str , deptTimeRange.split("-"))
        startArrivalTime, endArrivalTime = map(str, arrivalTimeRange.split("-"))
                    
        startDeptTime = datetime.strptime(startDeptTime, "%H:%M").time()
        endDeptTime = datetime.strptime(endDeptTime, "%H:%M").time()
        
        startArrivalTime = datetime.strptime(startArrivalTime, "%H:%M").time()
        endArrivalTime = datetime.strptime(endArrivalTime, "%H:%M").time()
                    
        updData = data.filter(
            departuretime__gte = startDeptTime,
            departuretime__lte = endDeptTime,
            arrivaltime__gte = startArrivalTime,
            arrivaltime__lte = endArrivalTime
        )
                
    elif deptTimeRange:
        startDeptTime, endDeptTime = map(str , deptTimeRange.split("-"))
        startDeptTime = datetime.strptime(startDeptTime, "%H:%M").time()
        endDeptTime = datetime.strptime(endDeptTime, "%H:%M").time()
        updData = data.filter(
            departuretime__gte = startDeptTime,
            departuretime__lte = endDeptTime,
        )
                
    else:
        startArrivalTime, endArrivalTime = map(str, arrivalTimeRange.split("-"))
        startArrivalTime = datetime.strptime(startArrivalTime, "%H:%M").time()
        endArrivalTime = datetime.strptime(endArrivalTime, "%H:%M").time()
        updData = data.filter(
            arrivaltime__gte = startArrivalTime,
            arrivaltime__lte = endArrivalTime
        )
        
    return updData

def priceBasedData(minPrice, maxPrice, userMinPrice, userMaxPrice, data):
    """This function gives the list of those entries that have the price field values meeting user's input values

    Args:
        minPrice (int): minimum price value in whole list 
        maxPrice (int): maximum price value in the list 
        userMinPrice (int): minimum price entered by the user
        userMaxPrice (int): maximum price entered by the user
        data (queryset): queryset containing the entries satisfying source and destination values

    Returns:
        queryset: list of those entries that have the price field values meeting user's input values
    """
    # diff = maxPrice - minPrice
    # change = (diff*20)/100
    
    # priceOptionList = [minPrice]
    # sum = round(minPrice + change)
    
    # while sum <= maxPrice:
    #     priceOptionList.append(sum)
    #     sum = round(sum + change)
        
    # if maxPrice not in priceOptionList:
    #     priceOptionList.append(maxPrice)
    
    if userMinPrice and userMaxPrice:
        updData = data.filter(
            price__gte = userMinPrice,
            price__lte = userMaxPrice
        ) 
    elif userMinPrice:
        updData = data.filter(  
            price__gte = userMinPrice
        )
    else:
        updData = data.filter(
            price__lte = userMaxPrice
        )
    
    return updData

def durationBasedData(minDuration, maxDuration, data):
    """This function gives the list of those entries that have the duration field values meeting user's input values

    Args:
        minDuration (time): minimum duration eneterd by the user
        maxDuration (time): maximum duration eneterd by the user
        data (queryset): queryset containing the entries satisfying source and destination values

    Returns:
        queryset: list of those entries that have the duration field values meeting user's input values
    """
    if minDuration and maxDuration:
        minDuration = datetime.strptime(minDuration, "%H").time()
        maxDuration = datetime.strptime(maxDuration, "%H").time()
        
        updData = data.filter(
            duration__gte = minDuration,
            duration__lte = maxDuration
        )
        
    elif minDuration:
        minDuration = datetime.strptime(minDuration, "%H").time()
        
        updData = data.filter(
            duration__gte = minDuration
        )
    
    else:
        maxDuration = datetime.strptime(maxDuration, "%H").time()
        
        updData = data.filter(
            duration__lte = maxDuration
        )
        
    return updData