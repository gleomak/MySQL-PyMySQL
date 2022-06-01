# ----- CONFIGURE YOUR EDITOR TO USE 4 SPACES PER TAB ----- #
import settings
import sys,os
sys.path.append(os.path.join(os.path.split(os.path.abspath(__file__))[0], 'lib'))
import lib.pymysql as db



def connection():
    ''' User this function to create your connections '''
    con = db.connect(
        settings.mysql_host, 
        settings.mysql_user, 
        settings.mysql_passwd, 
        settings.mysql_schema)
    
    return con

def findAirlinebyAge(x,y):
    
    # Create a new connection
    # Create a new connection
    con=connection()
    # Create a cursor on the connection
    cur=con.cursor()
    down =  int(x)
    upper = int(y)
    sql = """SELECT al.name , COUNT(*) FROM airlines al , routes r , flights f , flights_has_passengers fhp , passengers p 
        WHERE al.id = r.airlines_id and r.id = f.routes_id and f.id = fhp.flights_id and p.id = fhp.passengers_id
        and (-p.year_of_birth + '2022') < %d and (-p.year_of_birth + '2022') > %d GROUP BY al.id ORDER BY COUNT(*) DESC"""
    cur.execute(sql % (down , upper))
    r = cur.fetchall()
    Company = r[0][0]
    NumberOfPassengers = r[0][1]
    sql2 = """SELECT COUNT(*) FROM airlines al , airplanes ap , airlines_has_airplanes aha WHERE al.id = aha.airlines_id and ap.id = airplanes_id 
        and al.name = '%s' """
    cur.execute(sql2 % Company)
    r2 = cur.fetchone()
    NumOfAircrafts = r2[0]
    Triple1 = [("airline_name" , "num_of_passengers" , "num_of_aircrafts"),]
    Triple2 = [(Company , NumberOfPassengers , NumOfAircrafts),]
    Final = Triple1 + Triple2
    return Final


def findAirportVisitors(x,a,b):
    
   # Create a new connection
    con=connection()
    
    # Create a cursor on the connection
    cur=con.cursor()
    sql = """SELECT ap.name , COUNT(*)
        FROM airlines al , airports ap , routes r , flights f , flights_has_passengers fhp , passengers p
        WHERE al.name = '%s' and r.airlines_id = al.id and r.destination_id = ap.id
	    and f.routes_id = r.id and f.date >= '%s' and f.date <= '%s' 
        and f.id = fhp.flights_id and p.id = fhp.passengers_id
        GROUP BY ap.name
        ORDER BY COUNT(*) DESC"""
    cur.execute(sql %(x,a,b))
    r = cur.fetchall()
    final = [("airport_name" , "number_of_visitors"),]
    for row in r :
        mytuple = [(row[0] , row[1]),]
        final += mytuple
    return final

def findFlights(x,a,b):

    # Create a new connection
    con=connection()
    # Create a cursor on the connection
    cur=con.cursor()
    sql = """SELECT f.id , al.alias , ap2.name , ap3.model
        FROM routes r , airlines al , flights f , airports ap , airports ap2 , airplanes ap3
        WHERE r.source_id = ap.id and r.destination_id = ap2.id and ap.city = '%s' and ap2.city = '%s' and al.id = r.airlines_id
	    and al.active = 'Y' and f.routes_id = r.id and f.date = '%s'and ap3.id = f.airplanes_id"""
    cur.execute(sql %(a,b,x))
    r = cur.fetchall()
    final = [("flight_id", "alt_name", "dest_name", "aircraft_model"),]
    for row in r:
        t = [(row[0] , row[1] , row[2] , row[3]),]
        final += t
    return final
    

def findLargestAirlines(N):
    # Create a new connection
    con=connection()

    # Create a cursor on the connection
    cur=con.cursor()
    sql = """SELECT al.name , al.code , COUNT(*)
        FROM airlines al , flights f , routes r 
        WHERE al.id = r.airlines_id and r.id = f.routes_id
        GROUP BY al.id
        ORDER BY COUNT(*) DESC"""
    sql2 = """SELECT COUNT(*)
        FROM airlines al , airplanes ap , airlines_has_airplanes aha
        WHERE  al.name = '%s' and al.id = aha.airlines_id and ap.id = aha.airplanes_id"""
    cur.execute(sql)
    r = cur.fetchall()
    i = 0
    final = [("name", "id", "num_of_aircrafts", "num_of_flights"),]
    N = int(N)
    for row in r:
        if(i == N):
            break
        cur.execute(sql2 %(row[0]))
        r2 = cur.fetchone()
        NumOfAircrafts = r2[0]
        temp = [(row[0] , row[1] , NumOfAircrafts , row[2])]
        final += temp
        i += 1
    while(True): #Elegxos isobathmias se arithmo pthsewn
        temp2 = final[N][3]
        temp3 = r[N][2]
        if(temp2 == temp3) :
            cur.execute(sql2 % r[N][0])
            rr = cur.fetchone()
            temp4 = [(r[N][0] , r[N][1] , rr[0] , r[N][2])]
            final += temp4
            N += 1
        else :
            break

    return final
    
def insertNewRoute(x,y):
    # Create a new connection
    con=connection()
    # Create a cursor on the connection
    cur=con.cursor() 
    LastRouteID = """SELECT r.id
            FROM routes r
            ORDER BY r.id DESC""" # Last inserted id Number
    cur.execute(LastRouteID)
    ll = cur.fetchall()
    routeID = ll[0][0] + 1
    FindAirlineID = """SELECT al.id
            FROM airlines al 
            WHERE al.alias = '%s'""" #Vriskw to id tou given Airline
    FindAirportID = """SELECT ap.id
            FROM airports ap
            WHERE ap.name = '%s'""" #Vriskw to id toy aerodromiou
    CheckYX = """SELECT COUNT(*)
        FROM airports ap , airlines al , routes r 
        WHERE ap.name = '%s' and al.alias = '%s' and r.airlines_id = al.id and ap.id = r.source_id""" #Vriskw an uparxei aerodromio me registered hdh to Y aerodromio
    cur.execute(CheckYX %(y, x))
    rr = cur.fetchone()
    if rr[0] == 0:
        return [("PROBLEM WITH AIRPORT Y OR AIRLINE X"),]
    UnMatchedAirports = """SELECT ap3.name
                FROM airports ap3
                WHERE ap3.name NOT IN( SELECT ap2.name
                FROM airlines al , airports ap , airports ap2 , routes r 
                WHERE r.source_id = ap.id and ap.name = '%s' 
                and al.id = r.airlines_id and al.alias = '%s' and ap2.id = r.destination_id)""" #List of airport names poy to given Y airport den exei route
    cur.execute(UnMatchedAirports % (y , x))
    r = cur.fetchall()
    Airports = []
    for row in r : 
        Airports.append(row[0])
    InsertRoute = """INSERT INTO routes(id , airlines_id , source_id , destination_id) VALUES(%d , %d , %d , %d)""" #Insert to neo route
    Airports.remove(y) #Afairw to Y apo ta potential Destination Airports
    if(len(Airports) == 0):
        return [("GIVEN AIRPORT Y HAS ROUTE TO EVERY OTHER AIRPORT"),]
    else :
        dest = Airports[0] # TO name toy Destination Aerodromioy 
        cur.execute(FindAirportID % dest)
        destID = cur.fetchone() #TO id toy Destination aerodromioy
        cur.execute(FindAirportID % y)
        sourceID = cur.fetchone() #To id toy source Aerodromioy
        cur.execute(FindAirlineID % x)
        airlineID = cur.fetchone()
        cur.execute(InsertRoute % (routeID , airlineID[0] , sourceID[0] , destID[0]))
    return [("OK"),]
