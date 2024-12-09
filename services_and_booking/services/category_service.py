from db.utils.query_helpers import execute_query, fetch_dict_all, fetch_dict_one

class CategoryAndSubcategoryService:
    @staticmethod
    def get_all_categories():
        sql = """
        SELECT id, nama_kategori FROM sijarta.kategori_jasa;
        """
        return fetch_dict_all(sql)
    
    @staticmethod
    def get_subcategories_by_category(category_id):
        sql = """
        SELECT id, nama_subkategori FROM sijarta.subkategori_jasa WHERE kategori_jasa_id = %s;
        """
        return fetch_dict_all(sql, [category_id])
    
    @staticmethod
    def search_subcategory_by_name(subcategory_name):
        sql = """
        SELECT s.id AS subcategory_id, s.nama_subkategori AS subcategory_name, k.id AS category_id, k.nama_kategori AS category_name
        FROM sijarta.subkategori_jasa s
        JOIN sijarta.kategori_jasa k ON s.kategori_jasa_id = k.id
        WHERE s.nama_subkategori ILIKE %s;
        """
        return fetch_dict_all(sql, ['%' + subcategory_name + '%'])
    
    @staticmethod
    def get_subcategory_details(subcategory_id):
        sql = """
        SELECT s.id AS subcategory_id, s.nama_subkategori, s.deskripsi, k.id AS category_id, k.nama_kategori
        FROM sijarta.subkategori_jasa s
        JOIN sijarta.kategori_jasa k ON s.kategori_jasa_id = k.id
        WHERE s.id = %s;
        """
        return fetch_dict_one(sql, [subcategory_id])
    
    @staticmethod
    def get_sessions_by_subcategory(subcategory_id):
        sql = """
        SELECT sesi, harga
        FROM sijarta.sesi_layanan
        WHERE subkategori_id = %s;
        """
        return fetch_dict_all(sql, [subcategory_id])
    
    @staticmethod
    def get_workers_by_category(category_id):
        sql = """
        SELECT 
            u.id AS pekerja_id, 
            u.nama AS pekerja_nama,
            u.jenis_kelamin, 
            u.no_hp, 
            u.tgl_lahir, 
            u.alamat,
            p.rating,
            p.link_foto,
            p.jml_pesanan_selesai
        FROM sijarta.user u
        JOIN sijarta.pekerja p ON u.id = p.id
        JOIN sijarta.pekerja_kategori_jasa pkj ON p.id = pkj.pekerja_id
        WHERE pkj.kategori_jasa_id = %s;
        """
        return fetch_dict_all(sql, [category_id])
    
    @staticmethod
    def add_worker_to_category(worker_id, category_id):
        sql = """
        INSERT INTO sijarta.pekerja_kategori_jasa (pekerja_id, kategori_jasa_id)
        VALUES (%s, %s);
        """
        execute_query(sql, [worker_id, category_id])
    
