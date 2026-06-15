from firebird.driver import driver_config, connect

driver_config.fb_client_library.value = (
    r"C:\GDOOR Sistemas\GDOOR PRO\Conversao Firebird\Firebird_5_0\fbclient.dll"
)

conn = connect(
    database=r"localhost:C:\GDOOR Sistemas\GDOOR PRO\DATAGES.FDB",
    user="SYSDBA",
    password="masterkey"
)

print("Conectado!")
conn.close()
