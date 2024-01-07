import pypyodbc
from datetime import datetime


class Connection:
    connection = None
    cursor = None
    def __new__(obj, driver, server, database = None):
        try:
            connect_str = f"""
            DRIVER={{{driver}}};
            SERVER={server};
            DATABASE={database};
            Trusted_Connection=yes;
            """ if database else f"""
            DRIVER={{{driver}}};
            SERVER={server};
            Trusted_Connection=yes;
            """
            Connection.connection = pypyodbc.connect(connect_str, autocommit = True)
            Connection.cursor = Connection.connection.cursor()
        except Exception as error:
            raise error
Connection("SQL Server", "ABDULLAH-LAPTOP\\SQLExpress", "test1")


class AddUser:
    def __init__(self):
        self.add_data_to_database(AddUser.verify_input(self.get_input()))

    def get_input(self):
        id_number = input("Enter ID (10 digits): ")
        name = input("Enter Quad name: ")
        date = input("Enter birth date (0000-00-00): ")
        nationality = input("Enter nationality: ")
        phone_number = input("Enter phone number: ")

        return {"id": id_number, "name": name, "date": date, "nationality": nationality, "phone_number": phone_number}
    
    def verify_input(data: dict):
        verified_data = {}
        # Check id
        id_number = data.get("id", None)
        if not id_number: return False
        else:
            if len(id_number) == 10:
                verified_data["id"] = id_number
        # Check name
        name = data.get("name", None)
        if name and len(name.split(" ")) == 4:
            verified_data["name"] = name
        else: verified_data["name"] = None
        # Check date
        date = data.get("date", None)
        if date and len(date.split("-")) == 3:
            date_value = datetime.strptime(date, "%Y-%m-%d")
            verified_data["date"] = date_value
        else: verified_data["date"] = None
        # Check nationality
        nationality = data.get("nationality", None)
        if nationality: verified_data["nationality"] = nationality
        else: verified_data["nationality"] = None
        # Check phone number
        phone_number = data.get("phone_number", None)
        if phone_number and len(phone_number) == 10:
            verified_data["phone_number"] = phone_number
        else: verified_data["phone_number"] = None
        
        return verified_data

    def add_data_to_database(self, data: dict):
        if data:
            try:
                values = (data["id"], data["name"], data["date"], data["nationality"], data["phone_number"])
                query = "INSERT INTO users (id, name, age, nationality, phone_number) VALUES (?, ?, ?, ?, ?)"
                Connection.cursor.execute(query, values)
                Connection.connection.commit()
                print("This user have been added successfully")
                return True
            except Exception as error:
                print(error)
                return False

class Search:
    def __init__(self):
        print("-" * 35)
        self.number = input("Enter ID: ")
        self.search()
    
    def search(self):
        Connection.cursor.execute("SELECT * FROM users WHERE id = ?",(self.number,))
        result = Connection.cursor.fetchall()
        if not result == []:
            result_dict = dict.fromkeys(["ID", "Name", "Date", "Nationality", "Phone Number"])
            for index, key in enumerate(result_dict.keys()):
                result_dict[key] = result[0][index]
            print(result_dict)

            data = {}
            for key, value in result_dict.items():
                data[key.lower().replace(" ", "_")] = value
            self.ask_for_service(data)
        else:
            print("There is no user with this number")
            return False
    
    def ask_for_service(self, data):
        service = input("if want to update data enter 1\nif you want to delete this user enter 2\nif you want to get back to the start menu enter 3\nenter a number: ")
        match service:
            case "1":
                UpdateUser(data)
            case "2":
                delete_user(data)
            case "3":
                main_menu()
            case _:
                self.ask_for_service(data)

class UpdateUser:
    def __init__(self, data):
        self.data = data
        print("-" * 30)
        self.want_to_change = input("To change:-\nName enter 1\nDate enter 2\nnationality enter 3\nPhone Number enter 4\nTo cancel enter 5\nenter a number: ")
        match self.want_to_change:
            case "1":
                self.change("name", "Enter new quad name: ")
            case "2":
                self.change("data", "Enter new data: ")
            case "3":
                self.change("nationality", "Enter new nationality: ")
            case "4":
                self.change("phone_number", "Enter new phone number: ")
            case "5":
                return None

    def change(self, data, input_string):
        new_data = input(input_string)
        updated_data = self.data
        updated_data[f"{data}"] = new_data
        verified_data = AddUser.verify_input(updated_data)
        verified_data["date"] = verified_data["date"].strftime("%Y-%m-%d")
        if verified_data == updated_data:
            query = f"UPDATE users SET {data} = ? WHERE id = ?"
            values = (new_data, self.data["id"])
            Connection.cursor.execute(query, values)
            self.change_again()
        else:
            print("there is something wrong with the new data you've inserted make sure:\n1- the name contains 4 names\n2- the date is in this format (2003-09-01)\n3- the phone number contains 10 digits")
            self.__init__(self.data)
    
    def change_again(self):
        again = input("do you want to change anything else (yes/no): ").lower()
        if again == "yes":
            self.__init__(self.data)
        return False

def delete_user(data):
    sure = input(f"are you sure you want to delete this user\n{data}\nenter (yes/no)").lower()
    if sure == "yes":
        Connection.cursor.execute(f"DELETE FROM users WHERE id = {data['id']}")

def main_menu():
    print("-" * 35)
    service = input("if want to add a user enter 1\nif you want to search for a user enter 2\nif you want to close the program enter 3\nenter a number: ")
    match service:
        case "1":
            AddUser()
        case "2":
            Search()
        case _:
            print("thank you see you soon")
            exit()
    main_menu()
main_menu()

Connection.cursor.close()
Connection.connection.close()