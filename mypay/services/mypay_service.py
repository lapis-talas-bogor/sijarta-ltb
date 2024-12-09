import uuid
from datetime import date, datetime

from django.http import JsonResponse
from db.utils.query_helpers import execute_query, fetch_dict_all, fetch_dict_one
from pekerjajasa.services.pekerjajasa_servise import PekerjaJasaService
from users.services.user_service import UserService

class MyPayService:
    TR_MYPAY_FIELDS = """
    tr.id as id,
    tr.user_id as uid,
    tr.tgl as tanggal,
    tr.nominal as nominal,
    tr.kategori_id as kategori,
    cat.nama as nama
    """

    @staticmethod
    def get_tr_mypay_from_user_id(user_id: str) -> dict :
        '''Gets transaction history by user id from the database.'''
        sql = f"""
        SELECT
            {MyPayService.TR_MYPAY_FIELDS}
        FROM sijarta.tr_mypay tr 
            JOIN sijarta.kategori_tr_mypay cat ON (tr.kategori_id = cat.id)
        WHERE tr.user_id = %s
        ORDER BY tgl DESC;
        """

        result = fetch_dict_all(sql, [user_id])
        if not result:
            return None
        return result
    
    @staticmethod
    def topup(uid : str,nominal : int) :
        """Updates saldo mypay in the database"""
        sql = f"""
        UPDATE sijarta.user
        SET saldo_mypay = saldo_mypay + %s
        WHERE id = %s;

        INSERT INTO sijarta.tr_mypay VALUES(
        %s, %s, %s, %s, %s
        );
        """

        tanggal = date.today()
        id_ketegori = MyPayService.get_id_kategori_by_nama("Top Up")
        id_transaksi = uuid.uuid4()

        execute_query(
            sql,
            [nominal, uid, id_transaksi,uid, tanggal, nominal, id_ketegori],
        )

    @staticmethod
    def withdrawal(uid : str,nominal : int) :
        """Updates saldo mypay in the database"""
        sql = f"""
        UPDATE sijarta.user
        SET saldo_mypay = saldo_mypay - %s
        WHERE id = %s;

        INSERT INTO sijarta.tr_mypay VALUES(
        %s, %s, %s, %s, %s
        );
        """

        tanggal = date.today()
        id_ketegori = MyPayService.get_id_kategori_by_nama("Penarikan Dana")
        id_transaksi = uuid.uuid4()

        execute_query(
            sql,
            [nominal, uid, id_transaksi,uid, tanggal, nominal, id_ketegori],
        )

    @staticmethod
    def transfer_mypay(id_pengirim : str, no_hp : str, nominal : int) :
        """Transfers 'mypay' balance from sender to recipient and logs the transactions."""

        tanggal = date.today()
        id_ketegori_pengirim = MyPayService.get_id_kategori_by_nama("Transfer")
        id_transfer = uuid.uuid4()
        id_menerima_transfer = uuid.uuid4()
        id_kategori_penerima = MyPayService.get_id_kategori_by_nama("Menerima Transfer")
        id_penerima = str(UserService.get_user_by_phone_number(no_hp)['id'])

        sql = f"""
        UPDATE sijarta.user
        SET saldo_mypay = saldo_mypay - %s
        WHERE id = %s;

        UPDATE sijarta.user
        SET saldo_mypay = saldo_mypay + %s
        WHERE no_hp = %s;

        INSERT INTO sijarta.tr_mypay VALUES(
        %s, %s, %s, %s, %s
        );

        INSERT INTO sijarta.tr_mypay VALUES(
        %s, %s, %s, %s, %s
        );
        """

        
        execute_query(
            sql,
            [nominal, id_pengirim,  
             nominal, no_hp,
             id_transfer, id_pengirim, tanggal, nominal, id_ketegori_pengirim,
             id_menerima_transfer, id_penerima, tanggal, nominal, id_kategori_penerima
            ],
        )

    @staticmethod
    def get_id_kategori_by_nama(nama : str) -> str :
        """Fetches the category ID based on the category name from the database."""
        sql = f"""
        SELECT id FROM sijarta.kategori_tr_mypay
        WHERE nama LIKE %s;
        """

        result = fetch_dict_one(sql, [nama])
        return str(result['id'])
    
    @staticmethod
    def get_id_by_status(nama : str) -> str :
        """Fetches the order status ID based on the given status name from the database."""
        sql = f"""
        SELECT id FROM sijarta.status_pesanan
        WHERE status LIKE %s;
        """

        result = fetch_dict_one(sql, [nama])
        return str(result['id'])
    
    
    @staticmethod
    def get_menunggu_pembayaran_pemesanan_by_user(uid : str) :
        """Fetches orders by user_id that are waiting for payment."""
        sql = f"""
        SELECT
            {PekerjaJasaService.TR_PEMESANAN_JASA_FIELDS}
        FROM sijarta.tr_pemesanan_jasa pj 
            JOIN sijarta.tr_pemesanan_status ps ON(pj.id = ps.id_tr_pemesanan)
            JOIN sijarta.status_pesanan s ON(ps.id_status = s.id)
            JOIN sijarta.user u ON(pj.id_pelanggan = u.id)
            JOIN sijarta.subkategori_jasa sub ON(pj.id_kategori_jasa = sub.id)
            JOIN sijarta.kategori_jasa kj ON(kj.id = sub.kategori_jasa_id)
        WHERE pj.id_pelanggan = %s AND s.status = %s;
        """

        result = fetch_dict_all(sql, [uid, "Menunggu Pembayaran"])
        if not result:
            return None
        return result
    
    @staticmethod
    def bayar(id_transaksi : str, uid : str, nominal : int) :
        """Processes payment for a service transaction, updating the user's balance, 
        transaction status, and recording the payment in the system."""

        id_menunggu_pekerja_terdekat = MyPayService.get_id_by_status("Mencari Pekerja Terdekat")
        time_stamp = datetime.now()
        tanggal = date.today()
        kategori_id = MyPayService.get_id_kategori_by_nama("Pembayaran Jasa")
        id_pembayaran = uuid.uuid4()
    
        sql = f"""
        UPDATE sijarta.user
        SET saldo_mypay = saldo_mypay - %s
        WHERE id = %s;

        UPDATE sijarta.tr_pemesanan_status
        SET id_status = %s,
            tgl_waktu = %s
        WHERE id_tr_pemesanan = %s;
        

        INSERT INTO sijarta.tr_mypay VALUES(
        %s, %s, %s, %s, %s
        );
        """

        execute_query(
        sql,
        [ nominal,uid,
         id_menunggu_pekerja_terdekat, time_stamp, 
         id_transaksi, id_pembayaran, uid, tanggal, nominal, kategori_id],
        )