# Student ID: 011326324
# Name: Phu Tran
# Project: WGUPS

import datetime
import csv
import sys


# Load the csv files contains packages and route info into lists
with open("address.csv") as address_csv, open("distance.csv") as distance_csv:
    address_list = list(csv.reader(address_csv))
    distance_list = list(csv.reader(distance_csv))

# Creating the hash table use chaining to resolve collision
# References: W-1_ChainingHashTable_zyBooks_Key-Value.py
class HashTableWithChains:
    """Creates a hash table with given initial capacit, number of items, and load factor"""
    def __init__(self, initial_capacity = 30):
        self.table = [[] for _ in range(initial_capacity)]
        self.size = 0
        self.load_factor = 0.75
    
    """Creates a new hash table with a larger capacity and copies the existing items to the new table."""
    def rehash(self):
        # create a new table with double the capacity
        new_table = [[] for _ in range(len(self.table) * 2)]
        # copy the existing items to the new table
        for bucket_list in self.table:
            for pair in bucket_list:
                key = pair[0]
                item = pair[1]
                new_bucket = hash(key) % len(new_table)
                new_table[new_bucket].append(pair)
        # replace the old table with the new table
        self.table = new_table

    """Inserts a new item into the hash table with given key"""
    def insert(self,key,item):
        # Check to see if the table need to be resize 
        if self.size / len(self.table) > self.load_factor:
            self.rehash()
        bucket = hash(key)%len(self.table)
        bucket_list = self.table[bucket]
        # Update key if it is already in the bucket
        for i, pair in enumerate(bucket_list):
            if pair[0] == key:
                bucket_list[i] = (key, item)
                return True
        # if not in the bucket, insert item to the end of the list
        key_value = (key, item)
        bucket_list.append(key_value)
        self.size += 1 # increment the size
        return True
    
    """Search for a given key and return the item if found"""
    def search(self,key):
        bucket = hash(key)%len(self.table)
        bucket_list = self.table[bucket]
        for key_value in bucket_list:
            if key_value[0] == key:
                return key_value[1]
        return None
    
    """Remove an item associated with given key value"""
    def remove(self,key):
        bucket = hash(key)%len(self.table)
        bucket_list = self.table[bucket]
        for i, key_value in enumerate(bucket_list):
            if key_value[0] == key:
                del bucket_list[i]
                return

# Create a package class to store package info
class Packages:
    """Method to take in individual package info and store them into a Packages object"""
    def __init__(self,id,street,city,state,zip,deadline,weight,note,status,depart_time = None,deliver_time = None):
        self.id = id
        self.street = street
        self.city = city
        self.state = state
        self.zip = zip
        self.deadline = deadline
        self.weight = weight
        self.note = note
        self.status = status
        self.depart_time = depart_time
        self.deliver_time = deliver_time
    
    def __str__(self) -> str:
        return f"ID: {self.id}, {self.street}, {self.city}, {self.state}, {self.zip}, Deadline: {self.deadline}, Weight: {self.weight}, Status: {self.status}, Departure Time: {self.depart_time}, Delivery Time: {self.deliver_time}"

    """Method to update the status of a Packages object based on time of the day"""
    def update_status(self,time: datetime.timedelta):
        if self.depart_time > time:
            self.status = "At hub"
        elif self.deliver_time is None:
            self.status = "At hub"
        elif self.deliver_time > time:
            self.status = "On the way"
        else:
            self.status = "Delivered"
        # Add condition to correct no.9 package address after 10:20am
        if self.id == 9:
            if time > datetime.timedelta(hours=10, minutes=20):
                self.street = "410 S State St"
                self.zip = "84111"
            else:
                self.street = "300 State St"
                self.zip = "84103"

# Method to load package info from cvs file
# set the attributes for individual Packages object
# insert the Packages object into HashTableWithChains
def load_package_info(file_name,package_hash_table):
    with open(file_name) as package_csv:
        package_list = csv.reader(package_csv)
        # advance the pointer to the 2nd row of the package_list
        next(package_list)
        for package in package_list:
            id = int(package[0])
            street = package[1]
            city = package[2]
            state = package[3]
            zip = package[4]
            deadline = package[5]
            weight = package[6]
            note = package[7]
            status = "At hub"
            package = Packages(id,street,city,state,zip,deadline,weight,note,status)   
            # print(package): input validation
            package_hash_table.insert(id,package) 

# Setup and load packages info from csv file into hash table
package_hash_table = HashTableWithChains()
load_package_info("package.csv",package_hash_table)

# Create a truck class to store truck object
class Trucks:
    def __init__(self,speed,location,load,depart_time,miles):
        self.speed = speed
        self.location = location
        self.load = load
        self.depart_time = depart_time
        self.total_time = depart_time
        self.miles = miles
    
    def __str__(self):
        return f"{self.speed},{self.location},{self.miles},{self.total_time},{self.depart_time},{self.load}"

# Load the trucks
truck1 = Trucks(18,"4001 South 700 East",[1,2,4,5,7,8,10,11,12,17,21,22,39,40],datetime.timedelta(hours=8),0)
truck2 = Trucks(18,"4001 South 700 East",[3,9,13,14,15,16,18,19,20,23,24,36,38],datetime.timedelta(hours=9),0)
truck3 = Trucks(18,"4001 South 700 East",[6,25,26,27,28,29,30,31,32,33,34,35,37],datetime.timedelta(hours=10, minutes=30),0)

# Method to look up address
def address_lookup(address):
    for row in address_list:
        if address in row[2]:
            return int(row[0])
        
# Method to calculate distance between two addresses
def distance_calc(x,y):
    distance = distance_list[x][y]
    if distance =='':
        distance = distance_list[y][x]
    return float(distance)

# Nearest neighbor algorithm to delivery packages
def delivery_algo(truck):
    """For the packages in a Truck object, add the package to a queue waiting to deliver """
    packages_queue=[]
    for id in truck.load:
        package = package_hash_table.search(id)
        packages_queue.append(package)
    """Remove the packages info from a Truck object"""    
    truck.load.clear()

    """Going through the packages_queue until none is left"""
    while len(packages_queue) > 0:
        # Set up large arbitrarily value for comparision without knowing the distance beforehand
        next_location = 30000
        next_package = None
        for package in packages_queue:
            # Pioritize where to deliver first based on deadline
            if package in [6,25]:
                next_package = package
                next_location = distance_calc(address_lookup(truck.location),address_lookup(package.street))
            elif package in [1,7,14,15,16,17,21,29,30,31,35,38,41]:
                next_package = package
                next_location = distance_calc(address_lookup(truck.location),address_lookup(package.street))
                break
            if distance_calc(address_lookup(truck.location),address_lookup(package.street)) <= next_location:
                next_location = distance_calc(address_lookup(truck.location),address_lookup(package.street))
                next_package = package
        # Add package with the next closest location to the Truck object 
        truck.load.append(next_package.id)
        # Remove the package above from the packages_queue
        packages_queue.remove(next_package)
        # Calculate the current miles and update the time it takes to deliver a package
        truck.miles += next_location
        truck.location = next_package.street
        truck.total_time += datetime.timedelta(hours=next_location / 18)
        next_package.deliver_time = truck.total_time
        next_package.depart_time = truck.depart_time

delivery_algo(truck1)
delivery_algo(truck2)
truck3.depart_time = min(truck1.total_time,truck2.total_time)
delivery_algo(truck3)

# UI to look up packages info and delivery time
# Ask for user to enter time in format HH:MM:SS
# List status for a single package based on ID or all packages 
class Main:
    print("Welcome to WGUPS Delivery Service")
    print("The total distance travel for all trucks is: " + str(truck1.miles+truck2.miles+truck3.miles) + " miles")

    time_input = input("Enter time to check the status of each package (HH:MM:SS): ")
    (h,m,s) = time_input.split(":")

    convert_time = datetime.timedelta(hours=int(h), minutes=int(m), seconds=int(s))
    try:
        user_input = input("Enter an integer (1-40) or 'all': ")
        if user_input.lower() == "all":
            print("\nPackages in Truck 1:")
            for package_id in [1,2,4,5,7,8,10,11,12,17,21,22,39,40]:
                package = package_hash_table.search(package_id)
                package.update_status(convert_time)
                print(str(package))
            print("\nPackages in Truck 2:")
            for package_id in [3,9,13,14,15,16,18,19,20,23,24,36,38]:
                package = package_hash_table.search(package_id)
                package.update_status(convert_time)
                print(str(package))
            print("\nPackages in Truck 3:")
            for package_id in [6,25,26,27,28,29,30,31,32,33,34,35,37]:
                package = package_hash_table.search(package_id)
                package.update_status(convert_time)
                print(str(package))
        else:
            package_id = int(user_input)
            if 1 <= package_id <= 40:
                package = package_hash_table.search(package_id)
                package.update_status(convert_time)
                if package_id in [1,2,4,5,7,8,10,11,12,17,21,22,39,40]:
                    print("Package in Truck 1")
                elif package_id in [3,9,13,14,15,16,18,19,20,23,24,36,38]:
                    print("Package in Truck 2")
                else: 
                    print("Package in Truck 3")
                print(str(package))
            else:
                print("Invalid input. Exiting.")
                sys.exit()
    except ValueError:
        print("Invalid input. Exiting.")
        sys.exit()

