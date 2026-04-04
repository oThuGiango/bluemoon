from dbHandler import DBConfig, ResidentDB

cfg = DBConfig(
    host="pg-bluemoon-bluemoon2025.i.aivencloud.com",
    port=20994,
    dbname="defaultdb",
    user="avnadmin",
    password="AVNS_ihvG3I25hPKDjZnGQtv",
    sslmode="require"
)

db = ResidentDB(cfg)
print(db.get_taikhoan("ketoan_hoa"))
print(db.get_members_by_so_can_ho("B101"))
db.close()
