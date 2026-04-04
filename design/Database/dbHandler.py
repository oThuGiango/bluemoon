from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import os
from psycopg2.pool import SimpleConnectionPool
import psycopg2
import psycopg2.extras

@dataclass
class DBConfig:
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", 5432))
    dbname: str = os.getenv("DB_NAME", "defaultdb")
    user: str = os.getenv("DB_USER", "postgres")
    password: str = os.getenv("DB_PASSWORD", "")
    minconn: int = 1
    maxconn: int = 5
    sslmode: Optional[str] = "require"  # "disable" | "require" | "verify-ca" | "verify-full"
    sslrootcert: Optional[str] = os.getenv("DB_SSLROOTCERT", None)

class ResidentDB:
    """
    Lớp thao tác DB cho hệ thống quản lý hộ/nhân khẩu, hoá đơn, khoản thu/đợt thu.
    Tất cả truy vấn đều param-hoá; kết quả dạng dict (RealDictCursor).
    """
    def __init__(self, cfg: DBConfig):
        conn_kwargs = dict(
            host=cfg.host, port=cfg.port, dbname=cfg.dbname,
            user=cfg.user, password=cfg.password, connect_timeout=5
        )
        if cfg.sslmode:
            conn_kwargs["sslmode"] = cfg.sslmode
        if cfg.sslrootcert:
            conn_kwargs["sslrootcert"] = cfg.sslrootcert

        self.pool = SimpleConnectionPool(cfg.minconn, cfg.maxconn, **conn_kwargs)

    def close(self) -> None:
        if self.pool:
            self.pool.closeall()

    # ------------------ Low-level helpers ------------------ #
    def _get_conn(self):
        return self.pool.getconn()

    def _put_conn(self, conn):
        self.pool.putconn(conn)

    def _execute(
        self, sql: str, params: tuple | list = None,
        fetch: str = "none"  # "one" | "all" | "none"
    ) -> Optional[Any]:
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql, params or ())
                if fetch == "one":
                    row = cur.fetchone()
                    conn.commit()
                    return dict(row) if row else None
                elif fetch == "all":
                    rows = cur.fetchall()
                    conn.commit()
                    return [dict(r) for r in rows]
                else:
                    conn.commit()
                    return None
        except Exception:
            conn.rollback()
            raise
        finally:
            self._put_conn(conn)

    # ------------------ INSERT / UPSERT ------------------ #
    def insert_vaitro(self, ten_vaitro: str) -> int:
        row = self._execute(
            """
            INSERT INTO vaitro (ten_vaitro)
            VALUES (%s)
            RETURNING id_vaitro;
            """,
            (ten_vaitro,), fetch="one"
        )
        return row["id_vaitro"]

    def insert_taikhoan(self, username: str, password: str, id_vaitro: int) -> int:
        """
        Gợi ý: password nên là hash (bcrypt/argon2) ở tầng ứng dụng trước khi lưu.
        CITEXT cho username giúp so sánh không phân biệt hoa/thường.
        """
        row = self._execute(
            """
            INSERT INTO taikhoan (username, password, id_vaitro)
            VALUES (%s, %s, %s)
            ON CONFLICT (username)
            DO UPDATE SET password = EXCLUDED.password,
                          id_vaitro = EXCLUDED.id_vaitro
            RETURNING id_taikhoan;
            """,
            (username, password, id_vaitro), fetch="one"
        )
        return row["id_taikhoan"]

    def insert_hokhau(self, so_can_ho: str, dien_tich: float | None) -> int:
        row = self._execute(
            """
            INSERT INTO hokhau (so_can_ho, dien_tich)
            VALUES (%s, %s)
            ON CONFLICT (so_can_ho)
            DO UPDATE SET dien_tich = EXCLUDED.dien_tich
            RETURNING id_hokhau;
            """,
            (so_can_ho, dien_tich), fetch="one"
        )
        return row["id_hokhau"]

    def insert_nhankhau(
        self, ho_ten: str, ngay_sinh: Optional[str], cccd: Optional[str],
        quan_he_chu_ho: Optional[str], id_hokhau: int
    ) -> int:
        row = self._execute(
            """
            INSERT INTO nhankhau (ho_ten, ngay_sinh, cccd, quan_he_chu_ho, id_hokhau)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id_nhankhau;
            """,
            (ho_ten, ngay_sinh, cccd, quan_he_chu_ho, id_hokhau), fetch="one"
        )
        return row["id_nhankhau"]

    def insert_biendongnhankhau(
        self, loai_biendong: str, ngay_batdau: str, id_nhankhau: int,
        ngay_ketthuc: Optional[str] = None, ly_do: Optional[str] = None
    ) -> int:
        row = self._execute(
            """
            INSERT INTO biendongnhankhau (loai_biendong, ngay_batdau, ngay_ketthuc, ly_do, id_nhankhau)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id_biendong;
            """,
            (loai_biendong, ngay_batdau, ngay_ketthuc, ly_do, id_nhankhau), fetch="one"
        )
        return row["id_biendong"]

    def create_khoanthu(self, ten_khoanthu: str, don_gia: float, don_vi_tinh: str) -> int:
        row = self._execute(
            """
            INSERT INTO khoanthu (ten_khoanthu, don_gia, don_vi_tinh)
            VALUES (%s, %s, %s)
            RETURNING id_khoanthu;
            """,
            (ten_khoanthu, don_gia, don_vi_tinh), fetch="one"
        )
        return row["id_khoanthu"]

    def create_dotthu(
        self, ten_dotthu: str, ngay_batdau: str, id_khoanthu: int,
        ngay_ketthuc: Optional[str] = None, trang_thai: str = "draft"
    ) -> int:
        row = self._execute(
            """
            INSERT INTO dotthuphi (ten_dotthu, ngay_batdau, ngay_ketthuc, trang_thai, id_khoanthu)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id_dotthu;
            """,
            (ten_dotthu, ngay_batdau, ngay_ketthuc, trang_thai, id_khoanthu), fetch="one"
        )
        return row["id_dotthu"]

    def insert_hoadon(
        self, tong_tien: float, id_hokhau: int, id_dotthu: int, ngay_nop: Optional[str] = None
    ) -> int:
        """
        Upsert theo (id_hokhau, id_dotthu) để không trùng hoá đơn 1 hộ/1 đợt.
        """
        row = self._execute(
            """
            INSERT INTO hoadon (tong_tien, ngay_nop, id_hokhau, id_dotthu)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id_hokhau, id_dotthu)
            DO UPDATE SET tong_tien = EXCLUDED.tong_tien,
                          ngay_nop  = EXCLUDED.ngay_nop
            RETURNING id_hoadon;
            """,
            (tong_tien, ngay_nop, id_hokhau, id_dotthu), fetch="one"
        )
        return row["id_hoadon"]

    # ------------------ SELECT / TRUY VẤN ------------------ #
    def get_members_by_hokhau_id(self, id_hokhau: int) -> List[Dict[str, Any]]:
        """
        Trả danh sách nhân khẩu trong 1 hộ; ưu tiên Chủ hộ lên đầu.
        """
        return self._execute(
            """
            SELECT nk.*
            FROM nhankhau nk
            WHERE nk.id_hokhau = %s
            ORDER BY
              CASE nk.quan_he_chu_ho
                WHEN 'Chủ hộ' THEN 0
                WHEN 'Vợ chủ hộ' THEN 1
                WHEN 'Bố chủ hộ' THEN 2
                WHEN 'Mẹ chủ hộ' THEN 3
                WHEN 'Con trai chủ hộ' THEN 4
                WHEN 'Con gái chủ hộ' THEN 5
                WHEN 'Người thân' THEN 6
                ELSE 99
              END,
              nk.id_nhankhau;
            """,
            (id_hokhau,), fetch="all"
        )

    def get_members_by_so_can_ho(self, so_can_ho: str) -> List[Dict[str, Any]]:
        return self._execute(
            """
            SELECT nk.*
            FROM nhankhau nk
            JOIN hokhau h ON h.id_hokhau = nk.id_hokhau
            WHERE h.so_can_ho = %s
            ORDER BY
              CASE nk.quan_he_chu_ho
                WHEN 'Chủ hộ' THEN 0
                WHEN 'Vợ chủ hộ' THEN 1
                WHEN 'Bố chủ hộ' THEN 2
                WHEN 'Mẹ chủ hộ' THEN 3
                WHEN 'Con trai chủ hộ' THEN 4
                WHEN 'Con gái chủ hộ' THEN 5
                WHEN 'Người thân' THEN 6
                ELSE 99
              END,
              nk.id_nhankhau;
            """,
            (so_can_ho,), fetch="all"
        )

    def get_nhankhau(
        self, id_nhankhau: Optional[int] = None, cccd: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        if id_nhankhau is not None:
            return self._execute(
                "SELECT * FROM nhankhau WHERE id_nhankhau = %s;",
                (id_nhankhau,), fetch="one"
            )
        if cccd is not None:
            return self._execute(
                "SELECT * FROM nhankhau WHERE cccd = %s;",
                (cccd,), fetch="one"
            )
        raise ValueError("Cần truyền id_nhankhau hoặc cccd")

    def get_taikhoan(self, username: str) -> Optional[Dict[str, Any]]:
        """
        username là CITEXT nên so sánh không phân biệt hoa/thường.
        """
        return self._execute(
            "SELECT * FROM taikhoan WHERE username = %s;",
            (username,), fetch="one"
        )

    def get_hoadon(
        self,
        id_hoadon: Optional[int] = None,
        id_hokhau: Optional[int] = None,
        id_dotthu: Optional[int] = None
    ) -> List[Dict[str, Any]] | Optional[Dict[str, Any]]:
        if id_hoadon is not None:
            return self._execute(
                """
                SELECT hd.*, h.so_can_ho, dt.ten_dotthu, kt.ten_khoanthu
                FROM hoadon hd
                JOIN hokhau h ON h.id_hokhau = hd.id_hokhau
                JOIN dotthuphi dt ON dt.id_dotthu = hd.id_dotthu
                JOIN khoanthu kt ON kt.id_khoanthu = dt.id_khoanthu
                WHERE hd.id_hoadon = %s;
                """,
                (id_hoadon,), fetch="one"
            )
        # danh sách theo hộ và/hoặc đợt
        where = []
        params = []
        if id_hokhau is not None:
            where.append("hd.id_hokhau = %s")
            params.append(id_hokhau)
        if id_dotthu is not None:
            where.append("hd.id_dotthu = %s")
            params.append(id_dotthu)
        cond = (" WHERE " + " AND ".join(where)) if where else ""
        return self._execute(
            f"""
            SELECT hd.*, h.so_can_ho, dt.ten_dotthu, kt.ten_khoanthu
            FROM hoadon hd
            JOIN hokhau h ON h.id_hokhau = hd.id_hokhau
            JOIN dotthuphi dt ON dt.id_dotthu = hd.id_dotthu
            JOIN khoanthu kt ON kt.id_khoanthu = dt.id_khoanthu
            {cond}
            ORDER BY hd.id_hoadon DESC;
            """,
            tuple(params), fetch="all"
        )

    def get_khoanthu(self, id_khoanthu: int) -> Optional[Dict[str, Any]]:
        return self._execute(
            "SELECT * FROM khoanthu WHERE id_khoanthu = %s;",
            (id_khoanthu,), fetch="one"
        )

    def get_dotthu(self, id_dotthu: int) -> Optional[Dict[str, Any]]:
        return self._execute(
            """
            SELECT dt.*, kt.ten_khoanthu
            FROM dotthuphi dt
            JOIN khoanthu kt ON kt.id_khoanthu = dt.id_khoanthu
            WHERE dt.id_dotthu = %s;
            """,
            (id_dotthu,), fetch="one"
        )

    # ------------------ Tiện ích tính/ghi hoá đơn hàng loạt ------------------ #
    def bill_phi_dich_vu_by_area(
        self, id_dotthu: int, don_gia_per_m2: float
    ) -> int:
        """
        Tạo/ghi (upsert) hoá đơn phí dịch vụ cho TOÀN BỘ hộ dựa trên diện tích * đơn giá.
        Trả về số bản ghi đã ghi/upsert.
        """
        # Lưu ý: id_khoanthu của đợt phải là 'Phí dịch vụ ...' tương ứng,
        # logic ở đây chỉ tính toán theo m2, còn kiểm soát loại khoản thu là do phía gọi đảm bảo.
        rows = self._execute(
            """
            WITH base AS (
              SELECT h.id_hokhau, h.dien_tich
              FROM hokhau h
            ),
            calc AS (
              SELECT b.id_hokhau,
                     ROUND(COALESCE(b.dien_tich, 0) * %s, 2) AS tong_tien
              FROM base b
            ),
            upsert AS (
              INSERT INTO hoadon (tong_tien, ngay_nop, id_hokhau, id_dotthu)
              SELECT c.tong_tien, NULL, c.id_hokhau, %s
              FROM calc c
              ON CONFLICT (id_hokhau, id_dotthu)
              DO UPDATE SET tong_tien = EXCLUDED.tong_tien
              RETURNING id_hoadon
            )
            SELECT COUNT(*) AS affected FROM upsert;
            """,
            (don_gia_per_m2, id_dotthu), fetch="one"
        )
        return int(rows["affected"])
