import pymysql

try:
    connection = pymysql.connect(
        host="82.165.140.195",  # Die IP-Adresse des Hosts (Server)
        port=3306,  # Verwende Port 3306 für MariaDB
        user="airpulution",  # Der MariaDB-Benutzername
        password="Quantrufix42",  # Das Passwort für den Benutzer
        database="airpulution_db"
    )

    print("Verbindung erfolgreich!")
    connection.close()
except Exception as e:
    print(f"Fehler bei der Verbindung: {e}")
